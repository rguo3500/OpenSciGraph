# -*- coding: utf-8 -*-
"""
OpenSciGraph - JSONL → Parquet 导出脚本（阶段一）

用途
----
把"已规范化的 JSONL"转换为 Parquet 交付文件。
依赖：pandas + pyarrow（见 requirements.txt）。

行为约定
--------
- 只读输入 JSONL；绝不修改、删除输入文件
- 拒绝把输出写入 data/raw（原始输入受保护）
- 非法 QID / 缺必填字段的行会被 **跳过** 并记入报告的 skipped 清单（不中断整批）
- 小批次流式读取（--batch-size），不会一次性把超大文件读进内存
- 可重复运行（幂等）；若输出文件已存在，默认拒绝覆盖，需显式 --force
- 失败后恢复：被跳过的行会写入 reports/ 的跳行清单，修复后可重跑

输出
----
- data/processed/*.parquet      结构化交付文件（UTF-8，snappy 压缩）
- reports/parquet_export_<时间戳>.json   处理统计与跳过明细
- logs/jsonl_to_parquet.log     追加日志

用法（在项目虚拟环境中执行）
---------------------------
    python src/jsonl_to_parquet.py --input data/interim/sample_records.jsonl \
        --output data/processed/sample_records.parquet
    python src/jsonl_to_parquet.py --input data/interim/sample_records.jsonl \
        --output data/processed/sample_records.parquet --force
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402  (必须在 sys.path 调整之后导入)
    PROCESSED_DIR,
    REPORTS_DIR,
    assert_writable,
    human_bytes,
    is_valid_qid,
    iter_jsonl,
    load_config,
    parse_jsonl_line,
    relative_to_project,
    setup_logger,
    timestamp_slug,
    utc_now_iso,
    write_json_report,
)

REPORT_TYPE = "parquet_export"

#: Parquet 输出列顺序（结构化交付格式的契约）
COLUMNS: List[str] = [
    "entity_id",
    "entity_label_zh",
    "entity_label_en",
    "entity_type",
    "description",
    "description_lang",
    "aliases",
    "source",
    "license",
    "retrieved_at",
    "is_synthetic",
    "data_origin",
]


def _normalize_aliases(value: Any) -> List[str]:
    """把 aliases 统一成字符串列表（缺失 -> []，字符串 -> 单元素列表）。"""
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, (list, tuple, set)):
        return [str(item) for item in value if not (isinstance(item, str) and not item.strip())]
    return [str(value)]


def _normalize_row(record: Dict[str, Any]) -> Dict[str, Any]:
    """按 COLUMNS 契约裁剪并规范化单条记录。"""
    row: Dict[str, Any] = {}
    for column in COLUMNS:
        value = record.get(column)
        if column == "aliases":
            row[column] = _normalize_aliases(value)
        elif column == "is_synthetic":
            row[column] = bool(value) if value is not None else None
        else:
            row[column] = value
    return row


def load_records(
    input_path: Path,
    required_fields: List[str],
    batch_size: int,
) -> Dict[str, Any]:
    """流式读取并过滤 JSONL，返回可写入 Parquet 的行与统计信息。"""
    rows: List[Dict[str, Any]] = []
    skipped: List[Dict[str, Any]] = []
    seen_ids: set = set()

    stats = {
        "total_lines": 0,
        "blank_lines": 0,
        "kept_rows": 0,
        "skipped_rows": 0,
        "duplicate_rows": 0,
        "batches": 0,
    }

    for batch in iter_jsonl(input_path, batch_size=batch_size):
        stats["batches"] += 1
        for lineno, raw_line in batch:
            stats["total_lines"] += 1
            if not raw_line.strip():
                stats["blank_lines"] += 1
                continue

            record, error = parse_jsonl_line(raw_line)
            if record is None:
                skipped.append({"line": lineno, "reason": error})
                stats["skipped_rows"] += 1
                continue

            missing = [f for f in required_fields if f not in record]
            if missing:
                skipped.append(
                    {"line": lineno, "reason": f"缺少必填字段: {', '.join(missing)}"}
                )
                stats["skipped_rows"] += 1
                continue

            entity_id = record.get("entity_id")
            if not is_valid_qid(entity_id):
                skipped.append(
                    {"line": lineno, "reason": f"非法 QID: {entity_id!r}", "entity_id": entity_id}
                )
                stats["skipped_rows"] += 1
                continue

            if entity_id in seen_ids:
                skipped.append(
                    {"line": lineno, "reason": f"重复 entity_id（保留首条）: {entity_id}", "entity_id": entity_id}
                )
                stats["skipped_rows"] += 1
                stats["duplicate_rows"] += 1
                continue

            seen_ids.add(entity_id)
            rows.append(_normalize_row(record))
            stats["kept_rows"] += 1

    return {"rows": rows, "skipped": skipped, "stats": stats}


def write_parquet(
    rows: List[Dict[str, Any]],
    output_path: Path,
    compression: str,
    write_index: bool,
) -> Dict[str, Any]:
    """用 pandas + pyarrow 写出 Parquet，返回统计信息。"""
    try:
        import pandas as pd
    except ImportError as exc:  # pragma: no cover - 依赖缺失时给出明确指引
        raise SystemExit(
            "缺少依赖 pandas。请先在项目虚拟环境中执行：\n"
            "    python -m pip install -r requirements.txt"
        ) from exc

    dataframe = pd.DataFrame(rows, columns=COLUMNS)

    # 布尔列显式声明为可空布尔类型，保证 Parquet 中的类型稳定
    if "is_synthetic" in dataframe.columns:
        dataframe["is_synthetic"] = dataframe["is_synthetic"].astype("boolean")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_parquet(
        output_path,
        engine="pyarrow",
        compression=compression,
        index=write_index,
    )

    return {
        "rows": int(dataframe.shape[0]),
        "columns": int(dataframe.shape[1]),
        "column_names": list(dataframe.columns),
        "dtypes": {name: str(dtype) for name, dtype in dataframe.dtypes.items()},
        "null_counts": {name: int(count) for name, count in dataframe.isna().sum().items()},
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="OpenSciGraph: 把规范化 JSONL 导出为 Parquet（只读输入）。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--input", required=True, help="已规范化的 JSONL 文件路径")
    parser.add_argument(
        "--output",
        default=None,
        help="Parquet 输出路径（默认 data/processed/<输入文件名>.parquet）",
    )
    parser.add_argument("--batch-size", type=int, default=None, help="每批处理行数")
    parser.add_argument(
        "--compression",
        default=None,
        choices=["snappy", "gzip", "brotli", "zstd", "none"],
        help="压缩算法（默认取 config/settings.json 的 parquet.compression）",
    )
    parser.add_argument(
        "--report",
        default=None,
        help="导出报告输出路径（默认 reports/parquet_export_<时间戳>.json）",
    )
    parser.add_argument("--force", action="store_true", help="允许覆盖已存在的输出文件")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    config = load_config()
    logger = setup_logger("jsonl_to_parquet", level=config.get("logging", {}).get("level"))

    jsonl_cfg = config.get("jsonl", {})
    parquet_cfg = config.get("parquet", {})
    required_fields: List[str] = list(jsonl_cfg.get("required_fields", []))
    batch_size = args.batch_size or int(config.get("batch_size", 500))
    compression = args.compression or str(parquet_cfg.get("compression", "snappy"))
    write_index = bool(parquet_cfg.get("index", False))

    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = (Path.cwd() / input_path).resolve()
    if not input_path.is_file():
        logger.error("输入文件不存在或不是文件：%s", input_path)
        return 2

    output_path = (
        Path(args.output)
        if args.output
        else PROCESSED_DIR / f"{input_path.stem}.parquet"
    )
    if not output_path.is_absolute():
        output_path = (Path.cwd() / output_path).resolve()

    # 保护 data/raw：任何写入 raw 的尝试都直接失败
    try:
        assert_writable(output_path)
    except PermissionError as exc:
        logger.error(str(exc))
        return 3

    if output_path.exists() and not args.force:
        logger.error(
            "输出文件已存在，未覆盖：%s\n如需覆盖请显式加 --force 参数。",
            relative_to_project(output_path),
        )
        return 4

    logger.info("读取 JSONL：%s（batch_size=%d）", relative_to_project(input_path), batch_size)
    loaded = load_records(input_path, required_fields, batch_size)
    rows = loaded["rows"]
    skipped = loaded["skipped"]
    stats = loaded["stats"]

    if not rows:
        logger.error("没有可写入的记录（全部被跳过），已中止，未生成 Parquet。")
        return 5

    logger.info("解析完成：保留 %d 行，跳过 %d 行。", len(rows), len(skipped))

    parquet_stats = write_parquet(rows, output_path, compression, write_index)
    logger.info(
        "Parquet 已写出：%s（%s）",
        relative_to_project(output_path),
        human_bytes(output_path.stat().st_size),
    )

    report: Dict[str, Any] = {
        "report_type": REPORT_TYPE,
        "generated_at": utc_now_iso(),
        "script": "src/jsonl_to_parquet.py",
        "input_file": relative_to_project(input_path),
        "input_size_bytes": input_path.stat().st_size,
        "input_size_human": human_bytes(input_path.stat().st_size),
        "output_file": relative_to_project(output_path),
        "output_size_bytes": output_path.stat().st_size,
        "output_size_human": human_bytes(output_path.stat().st_size),
        "compression": compression,
        "engine": "pyarrow",
        "batch_size": batch_size,
        "processing_stats": stats,
        "parquet_stats": parquet_stats,
        "skipped_rows": skipped[: int(jsonl_cfg.get("max_details_in_report", 50))],
        "skipped_rows_truncated": max(0, len(skipped) - int(jsonl_cfg.get("max_details_in_report", 50))),
        "columns_contract": COLUMNS,
        "notes": [
            "输出为派生数据，不含任何真实 Wikidata 抓取结果（除非输入本身来自合法来源）。",
            "输入文件保持原样，未被修改。",
            "data/raw 目录受保护，本脚本拒绝向其写入。",
        ],
    }
    report_path = (
        Path(args.report)
        if args.report
        else REPORTS_DIR / f"parquet_export_{timestamp_slug()}.json"
    )
    if not report_path.is_absolute():
        report_path = (Path.cwd() / report_path).resolve()
    assert_writable(report_path)
    write_json_report(report, report_path)
    logger.info("报告已写入：%s", relative_to_project(report_path))

    print("-" * 62)
    print(f"输入 JSONL : {report['input_file']}  ({report['input_size_human']})")
    print(f"输出 Parquet: {report['output_file']}  ({report['output_size_human']})")
    print(f"保留行数   : {parquet_stats['rows']}")
    print(f"列数       : {parquet_stats['columns']}  {parquet_stats['column_names']}")
    print(f"跳过行数   : {stats['skipped_rows']}（其中重复 {stats['duplicate_rows']}）")
    print(f"压缩方式   : {compression}")
    print("-" * 62)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
