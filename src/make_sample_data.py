# -*- coding: utf-8 -*-
"""
OpenSciGraph - 合成测试数据生成脚本（阶段一）

用途
----
生成 10 条 **完全合成的测试记录**，写入 data/interim/sample_records.jsonl。

⚠️ 重要声明
----------
这些记录 **不是** 真实的 Wikipedia / Wikidata 数据，也 **不是** 对真实条目的改写。
它们是为验证数据管道而人工编造的虚构条目，并且：
  - 每条记录都带有 "is_synthetic": true
  - 每条记录的 data_origin 都为 "SYNTHETIC_TEST_ONLY"
  - source 字段为 "synthetic-fixture"
任何下游使用都必须先检查 is_synthetic，禁止把合成数据当作真实数据对外发布。

覆盖的边界情况
--------------
1. 纯中文记录
2. 纯英文记录
3. 中英混合记录
4. 缺失可选字段（description / aliases 为 null）
5. 缺失 entity_label_en
6. 重复 entity_id（与第 2 条冲突）
7. 非法 QID（含字母，如 QABC123）
8. 非法 QID（缺少 Q 前缀，如 "42"）
9. 多语言记录（日文 + 德文）
10. 空字符串标签（"entity_label_zh" 为 ""）

覆盖到的语言：简体中文、英文、日文、德文 —— 用于验证 UTF-8 多语言读写。

用法（在项目虚拟环境中执行）
---------------------------
    python src/make_sample_data.py
    python src/make_sample_data.py --force        # 覆盖已存在的输出
    python src/make_sample_data.py --output data/interim/other.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402  (必须在 sys.path 调整之后导入)
    INTERIM_DIR,
    assert_writable,
    relative_to_project,
    setup_logger,
    utc_now_iso,
)

DEFAULT_OUTPUT = INTERIM_DIR / "sample_records.jsonl"
GENERATED_AT = "2026-10-12T00:00:00Z"  # 固定值，保证脚本可重复运行得到完全一致的结果

SYNTHETIC_SOURCE = "synthetic-fixture"
SYNTHETIC_LICENSE = "CC0-1.0 (synthetic fixture, contains no real-world data)"
SYNTHETIC_ORIGIN = "SYNTHETIC_TEST_ONLY"


def _base(entity_id: str, **overrides: Any) -> Dict[str, Any]:
    """构造一条带有完整合成标记的基础记录。"""
    record: Dict[str, Any] = {
        "entity_id": entity_id,
        "entity_label_zh": None,
        "entity_label_en": None,
        "entity_type": None,
        "description": None,
        "description_lang": None,
        "aliases": [],
        "source": SYNTHETIC_SOURCE,
        "license": SYNTHETIC_LICENSE,
        "retrieved_at": GENERATED_AT,
        "is_synthetic": True,
        "data_origin": SYNTHETIC_ORIGIN,
    }
    record.update(overrides)
    return record


def build_records() -> List[Dict[str, Any]]:
    """返回 10 条合成测试记录。"""
    return [
        # 1) 纯中文
        _base(
            "Q900000001",
            entity_label_zh="合成量子拓扑材料",
            entity_label_en="Synthetic Quantum Topological Material",
            entity_type="concept",
            description="这是一个用于测试的虚构材料概念，与任何真实化合物无关。",
            description_lang="zh",
            aliases=["拓扑量子材料（虚构）", "合成拓扑材料"],
        ),
        # 2) 纯英文
        _base(
            "Q900000002",
            entity_label_zh=None,
            entity_label_en="Synthetic Protein Folding Benchmark",
            entity_type="dataset",
            description=(
                "A fabricated benchmark dataset used only for pipeline testing. "
                "It does not describe any real research artifact."
            ),
            description_lang="en",
            aliases=["SPF-Bench (fake)"],
        ),
        # 3) 中英混合
        _base(
            "Q900000003",
            entity_label_zh="深空射电阵列（合成）",
            entity_label_en="Deep Space Radio Array",
            entity_type="facility",
            description="这是一个虚构的观测设施 Deep Space Radio Array，中文名称为深空射电阵列。",
            description_lang="zh-en",
            aliases=["DSRA（虚构）"],
        ),
        # 4) 缺失可选字段：description / description_lang / aliases 全为 null
        _base(
            "Q900000004",
            entity_label_zh="缺失描述的合成条目",
            entity_label_en="Synthetic Entry Without Description",
            entity_type="concept",
            description=None,
            description_lang=None,
            aliases=None,
        ),
        # 5) 缺失 entity_label_en
        _base(
            "Q900000005",
            entity_label_zh="仅有中文标签的合成条目",
            entity_label_en=None,
            entity_type="concept",
            description="该条目故意缺少英文标签，用于测试缺失值处理。",
            description_lang="zh",
            aliases=["仅中文标签"],
        ),
        # 6) 重复 entity_id（与第 2 条相同，模拟重复抓取）
        _base(
            "Q900000002",
            entity_label_zh="重复条目（与第 2 条 QID 相同）",
            entity_label_en="Synthetic Protein Folding Benchmark (duplicate)",
            entity_type="dataset",
            description="重复 entity_id 的测试行，用于验证去重逻辑。",
            description_lang="zh",
            aliases=["duplicate-fake"],
        ),
        # 7) 非法 QID：含字母
        _base(
            "QABC123",
            entity_label_zh="非法 QID 示例（含字母）",
            entity_label_en="Invalid QID Example (letters)",
            entity_type="concept",
            description="entity_id 含非数字字符，应被校验脚本标记为错误。",
            description_lang="zh",
        ),
        # 8) 非法 QID：缺少 Q 前缀
        _base(
            "42",
            entity_label_zh="非法 QID 示例（缺前缀）",
            entity_label_en="Invalid QID Example (no prefix)",
            entity_type="concept",
            description="entity_id 缺少 Q 前缀，应被校验脚本标记为错误。",
            description_lang="zh",
        ),
        # 9) 多语言（日文 + 德文）
        _base(
            "Q900000009",
            entity_label_zh="合成多语言研究机构",
            entity_label_en="Synthetic Multilingual Research Institute",
            entity_type="organization",
            description=(
                "日本語のテスト記述です。ドイツ語のテスト記述：Dies ist ein synthetischer Testdatensatz. "
                "This record exists only to verify UTF-8 handling of CJK, kana and umlauts (ä, ö, ü, ß)."
            ),
            description_lang="ja-de-en",
            aliases=["合成多言語研究機関", "Synthetisches Institut"],
        ),
        # 10) 空字符串标签（异常值）
        _base(
            "Q900000010",
            entity_label_zh="",
            entity_label_en="",
            entity_type="concept",
            description="中英文标签均为空字符串，用于测试空值告警。",
            description_lang="zh",
            aliases=[],
        ),
    ]


def write_jsonl(records: List[Dict[str, Any]], output_path: Path, force: bool) -> None:
    """把记录写成 UTF-8 JSONL（每行一条，ensure_ascii=False 保留中文原字符）。"""
    assert_writable(output_path)  # 保护 data/raw
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists() and not force:
        raise FileExistsError(
            f"输出文件已存在：{output_path}\n如需覆盖请加 --force 参数。"
        )
    with output_path.open("w", encoding="utf-8", newline="\n") as fh:
        for record in records:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="OpenSciGraph: 生成 10 条合成测试记录（不是真实 Wikidata 数据）。"
    )
    parser.add_argument("--output", default=None, help=f"输出路径（默认 {DEFAULT_OUTPUT}）")
    parser.add_argument("--force", action="store_true", help="允许覆盖已存在的输出文件")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    logger = setup_logger("make_sample_data")

    output_path = Path(args.output) if args.output else DEFAULT_OUTPUT
    if not output_path.is_absolute():
        output_path = (Path.cwd() / output_path).resolve()

    records = build_records()
    try:
        write_jsonl(records, output_path, force=args.force)
    except FileExistsError as exc:
        logger.error(str(exc))
        return 4
    except PermissionError as exc:
        logger.error(str(exc))
        return 3

    logger.info("已生成 %d 条合成测试记录 -> %s", len(records), relative_to_project(output_path))
    logger.info("所有记录均已标记 is_synthetic=true, data_origin=%s", SYNTHETIC_ORIGIN)

    print("-" * 62)
    print(f"输出文件 : {relative_to_project(output_path)}")
    print(f"记录条数 : {len(records)}")
    print(f"生成时间 : {utc_now_iso()}")
    print("数据性质 : 100% 合成测试数据（非真实 Wikipedia/Wikidata 数据）")
    print("-" * 62)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
