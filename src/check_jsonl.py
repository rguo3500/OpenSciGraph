# -*- coding: utf-8 -*-
"""
OpenSciGraph - JSONL 校验脚本（阶段一）

用途
----
检查"小型 JSONL 文件"的格式与数据质量，并输出结构化报告。
本脚本 **只读**，绝不修改或删除输入文件。

校验内容
--------
1. 编码：以 UTF-8 打开，中文/日文/德文等多语言文本不会被破坏
2. 结构：每行必须是合法的 JSON 对象
3. 必填字段：见 config/settings.json -> jsonl.required_fields
4. QID 合法性：Wikidata 规范 = Q + 正整数（如 Q42）
5. 重复记录：按 entity_id 识别，仅第一条视为有效，其余标记为重复
6. 空标签：中英文标签都为空的记录给出警告
7. 合成数据标记：检查 is_synthetic 是否为 true（防止测试数据被误认为真实数据）

输出
----
- 控制台摘要（UTF-8）
- logs/check_jsonl.log 追加日志
- reports/jsonl_check_<时间戳>.json 结构化报告

退出码
------
0 = 未发现 error 级问题
1 = 发现 error 级问题（--strict 时，warning 也会导致退出码 1）

用法（在项目虚拟环境中执行）
---------------------------
    python src/check_jsonl.py --input data/interim/sample_records.jsonl
    python src/check_jsonl.py --input data/interim/sample_records.jsonl --batch-size 100
    python src/check_jsonl.py --input data/interim/sample_records.jsonl --strict
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# 允许以 `python src/check_jsonl.py` 直接运行时找到同目录的 common 模块
sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402  (必须在 sys.path 调整之后导入)
    QID_PATTERN,
    REPORTS_DIR,
    assert_writable,
    contains_cjk,
    contains_latin,
    human_bytes,
    is_blank,
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

REPORT_TYPE = "jsonl_validation"


# ---------------------------------------------------------------------------
# 校验主逻辑
# ---------------------------------------------------------------------------


def validate_file(
    input_path: Path,
    config: Dict[str, Any],
    batch_size: int = 500,
) -> Dict[str, Any]:
    """校验一个 JSONL 文件并返回结构化报告字典。"""
    jsonl_cfg = config.get("jsonl", {})
    required_fields: List[str] = list(jsonl_cfg.get("required_fields", []))
    optional_fields: List[str] = list(jsonl_cfg.get("optional_fields", []))
    max_details: int = int(jsonl_cfg.get("max_details_in_report", 50))

    totals = {
        "total_lines": 0,
        "blank_lines": 0,
        "parsed_records": 0,
        "valid_records": 0,
        "error_records": 0,
        "warning_records": 0,
        "batches": 0,
    }
    issues: Dict[str, List[Dict[str, Any]]] = {
        "invalid_json": [],
        "not_a_json_object": [],
        "missing_required_fields": [],
        "invalid_qid": [],
        "duplicate_entity_id": [],
        "blank_labels": [],
        "missing_synthetic_flag": [],
    }
    counters = {
        "invalid_json": 0,
        "not_a_json_object": 0,
        "missing_required_fields": 0,
        "invalid_qid": 0,
        "duplicate_entity_id": 0,
        "blank_labels": 0,
        "missing_synthetic_flag": 0,
    }

    seen_ids: Dict[str, int] = {}
    field_presence = {field: 0 for field in required_fields + optional_fields}
    languages = {"records_with_cjk": 0, "records_with_latin": 0, "records_with_both": 0}
    entity_types: Dict[str, int] = {}
    synthetic_true = 0

    def add_detail(bucket: str, detail: Dict[str, Any]) -> None:
        counters[bucket] += 1
        if len(issues[bucket]) < max_details:
            issues[bucket].append(detail)

    for batch in iter_jsonl(input_path, batch_size=batch_size):
        totals["batches"] += 1
        for lineno, raw_line in batch:
            totals["total_lines"] += 1

            if not raw_line.strip():
                totals["blank_lines"] += 1
                continue

            record, error = parse_jsonl_line(raw_line)
            if record is None:
                # 区分"不是 JSON"和"JSON 但不是对象"
                bucket = "not_a_json_object" if "顶层结构" in (error or "") else "invalid_json"
                add_detail(bucket, {"line": lineno, "reason": error})
                totals["error_records"] += 1
                continue

            totals["parsed_records"] += 1

            # --- 必填字段 ---
            missing = [f for f in required_fields if f not in record]
            for field in record:
                if field in field_presence:
                    field_presence[field] += 1

            has_error = False
            if missing:
                add_detail(
                    "missing_required_fields",
                    {"line": lineno, "entity_id": record.get("entity_id"), "missing": missing},
                )
                has_error = True

            # --- QID 合法性 ---
            entity_id = record.get("entity_id")
            if entity_id is not None and not is_valid_qid(entity_id):
                add_detail(
                    "invalid_qid",
                    {
                        "line": lineno,
                        "entity_id": entity_id,
                        "expected_pattern": QID_PATTERN.pattern,
                        "hint": "合法 QID 形如 Q42 / Q100001（字母 Q + 不以 0 开头的正整数）",
                    },
                )
                has_error = True

            # --- 合成数据标记 ---
            if record.get("is_synthetic") is True:
                synthetic_true += 1
            elif "is_synthetic" in record:
                add_detail(
                    "missing_synthetic_flag",
                    {
                        "line": lineno,
                        "entity_id": entity_id,
                        "is_synthetic": record.get("is_synthetic"),
                        "hint": "测试数据必须显式标记 is_synthetic = true",
                    },
                )

            if has_error:
                totals["error_records"] += 1
                continue

            # --- 重复检测（基于 entity_id，保留首条） ---
            if isinstance(entity_id, str):
                if entity_id in seen_ids:
                    add_detail(
                        "duplicate_entity_id",
                        {
                            "line": lineno,
                            "entity_id": entity_id,
                            "first_seen_line": seen_ids[entity_id],
                        },
                    )
                    totals["warning_records"] += 1
                    continue
                seen_ids[entity_id] = lineno

            # --- 空标签告警 ---
            if is_blank(record.get("entity_label_zh")) and is_blank(
                record.get("entity_label_en")
            ):
                add_detail(
                    "blank_labels",
                    {"line": lineno, "entity_id": entity_id, "hint": "中文与英文标签均为空"},
                )
                totals["warning_records"] += 1

            # --- 多语言统计 ---
            text_blob = " ".join(
                str(record.get(key, ""))
                for key in ("entity_label_zh", "entity_label_en", "description", "entity_type")
            )
            has_cjk = contains_cjk(text_blob)
            has_latin = contains_latin(text_blob)
            if has_cjk:
                languages["records_with_cjk"] += 1
            if has_latin:
                languages["records_with_latin"] += 1
            if has_cjk and has_latin:
                languages["records_with_both"] += 1

            etype = record.get("entity_type")
            if isinstance(etype, str) and etype.strip():
                entity_types[etype] = entity_types.get(etype, 0) + 1

            totals["valid_records"] += 1

    report: Dict[str, Any] = {
        "report_type": REPORT_TYPE,
        "generated_at": utc_now_iso(),
        "script": "src/check_jsonl.py",
        "input_file": relative_to_project(input_path),
        "input_size_bytes": input_path.stat().st_size,
        "input_size_human": human_bytes(input_path.stat().st_size),
        "batch_size": batch_size,
        "required_fields": required_fields,
        "totals": totals,
        "issue_counts": counters,
        "issues": issues,
        "field_presence": field_presence,
        "language_stats": languages,
        "entity_type_counts": dict(sorted(entity_types.items())),
        "synthetic_records_marked_true": synthetic_true,
        "details_truncated_at": max_details,
        "notes": [
            "本报告由只读校验脚本生成，未修改任何输入文件。",
            "duplicate_entity_id 采用「保留首条」策略，被去重的行不计入 valid_records。",
            "is_synthetic 用于区分合成测试数据与真实数据，禁止把合成数据当作真实数据使用。",
        ],
    }
    return report


def summarize(report: Dict[str, Any]) -> str:
    """把报告浓缩成适合打印的多行文本摘要。"""
    totals = report["totals"]
    counters = report["issue_counts"]
    lines = [
        "-" * 62,
        f"输入文件      : {report['input_file']}  ({report['input_size_human']})",
        f"批次大小      : {report['batch_size']}    实际批次数: {totals['batches']}",
        "-" * 62,
        f"总行数        : {totals['total_lines']}",
        f"空行          : {totals['blank_lines']}",
        f"可解析记录    : {totals['parsed_records']}",
        f"有效记录      : {totals['valid_records']}",
        f"错误记录      : {totals['error_records']}",
        f"告警记录      : {totals['warning_records']}",
        "-" * 62,
        f"JSON 解析失败 : {counters['invalid_json']}",
        f"非对象结构    : {counters['not_a_json_object']}",
        f"缺必填字段    : {counters['missing_required_fields']}",
        f"非法 QID      : {counters['invalid_qid']}",
        f"重复 entity_id: {counters['duplicate_entity_id']}",
        f"空标签        : {counters['blank_labels']}",
        f"合成标记缺失  : {counters['missing_synthetic_flag']}",
        "-" * 62,
        f"含中文记录    : {report['language_stats']['records_with_cjk']}",
        f"含拉丁字母记录: {report['language_stats']['records_with_latin']}",
        f"标记为合成数据: {report['synthetic_records_marked_true']}",
        "-" * 62,
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 命令行入口
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="OpenSciGraph: 校验小型 JSONL 文件（只读，不修改输入）。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--input",
        required=True,
        help="待校验的 JSONL 文件路径，例如 data/interim/sample_records.jsonl",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="报告输出路径（默认 reports/jsonl_check_<时间戳>.json）",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="每批处理的行数（默认取 config/settings.json 的 batch_size，即 500）",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="严格模式：出现任何警告（warning）也返回退出码 1",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    config = load_config()
    logger = setup_logger("openscigraph", level=config.get("logging", {}).get("level"))

    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = (Path.cwd() / input_path).resolve()
    if not input_path.exists():
        logger.error("输入文件不存在：%s", input_path)
        return 2
    if not input_path.is_file():
        logger.error("输入路径不是文件：%s", input_path)
        return 2

    batch_size = args.batch_size or int(config.get("batch_size", 500))

    logger.info("开始校验 JSONL：%s（batch_size=%d）", relative_to_project(input_path), batch_size)
    report = validate_file(input_path, config, batch_size=batch_size)

    output_path = (
        Path(args.output)
        if args.output
        else REPORTS_DIR / f"jsonl_check_{timestamp_slug()}.json"
    )
    assert_writable(output_path)  # 保护 data/raw
    write_json_report(report, output_path)

    print(summarize(report))
    logger.info("报告已写入：%s", relative_to_project(output_path))

    totals = report["totals"]
    has_error = totals["error_records"] > 0
    has_warning = totals["warning_records"] > 0

    if has_error:
        logger.error("校验结束：发现 %d 条错误记录，需修复后重跑。", totals["error_records"])
        return 1
    if args.strict and has_warning:
        logger.warning("严格模式：存在 %d 条告警记录，退出码 1。", totals["warning_records"])
        return 1
    logger.info("校验结束：无错误记录。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
