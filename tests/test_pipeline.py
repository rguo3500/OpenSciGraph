# -*- coding: utf-8 -*-
"""
OpenSciGraph - 阶段一单元测试（Python 标准库 unittest）

运行方式（在项目虚拟环境中执行）：
    python -m unittest discover -s tests -v
或：
    python tests/test_pipeline.py

测试覆盖：
- QID 合法性判断
- 空值判断
- JSONL 小批次流式读取
- 单行 JSON 解析（含错误分支）
- aliases 字段规范化
- data/raw 写入保护
- 合成测试集：条数、合成标记、边界情况齐全性
- 校验脚本的统计结果与预期完全一致
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import common  # noqa: E402
import check_jsonl  # noqa: E402
import jsonl_to_parquet  # noqa: E402
import make_sample_data  # noqa: E402

SAMPLE_FILE = PROJECT_ROOT / "data" / "interim" / "sample_records.jsonl"


class TestQidValidation(unittest.TestCase):
    """QID 校验规则。"""

    def test_valid_qids(self) -> None:
        for value in ["Q1", "Q42", "Q100001", "Q900000010"]:
            with self.subTest(value=value):
                self.assertTrue(common.is_valid_qid(value))

    def test_invalid_qids(self) -> None:
        for value in ["Q0", "QABC123", "42", "q42", "Q-1", "Q 42", "", "Q01", None, 42]:
            with self.subTest(value=value):
                self.assertFalse(common.is_valid_qid(value))

    def test_qid_number(self) -> None:
        self.assertEqual(common.qid_number("Q42"), 42)
        self.assertIsNone(common.qid_number("QABC"))


class TestBlankDetection(unittest.TestCase):
    """空值判断（None / 空串 / 纯空白）。"""

    def test_blank(self) -> None:
        for value in [None, "", "   ", "\t\n"]:
            with self.subTest(value=value):
                self.assertTrue(common.is_blank(value))

    def test_not_blank(self) -> None:
        for value in ["a", "中文", "  x  ", 0]:
            with self.subTest(value=value):
                self.assertFalse(common.is_blank(value))


class TestJsonlIo(unittest.TestCase):
    """JSONL 读取与解析。"""

    def _write_temp(self, lines) -> Path:
        tmp = Path(tempfile.mkdtemp(prefix="oscg_")) / "tmp.jsonl"
        with tmp.open("w", encoding="utf-8", newline="\n") as fh:
            for line in lines:
                fh.write(line + "\n")
        return tmp

    def test_iter_jsonl_batching(self) -> None:
        tmp = self._write_temp([json.dumps({"i": i}) for i in range(7)])
        batches = list(common.iter_jsonl(tmp, batch_size=3))
        self.assertEqual([len(b) for b in batches], [3, 3, 1])
        # 行号从 1 开始且连续
        self.assertEqual([lineno for b in batches for lineno, _ in b], list(range(1, 8)))

    def test_parse_valid_line(self) -> None:
        record, error = common.parse_jsonl_line('{"entity_id": "Q1"}')
        self.assertIsNone(error)
        self.assertEqual(record, {"entity_id": "Q1"})

    def test_parse_broken_json(self) -> None:
        record, error = common.parse_jsonl_line('{"entity_id": "Q1"')
        self.assertIsNone(record)
        self.assertIsNotNone(error)

    def test_parse_non_object(self) -> None:
        record, error = common.parse_jsonl_line("[1, 2, 3]")
        self.assertIsNone(record)
        self.assertIn("JSON 对象", error)

    def test_chinese_roundtrip(self) -> None:
        tmp = self._write_temp([json.dumps({"label": "中文标签"}, ensure_ascii=False)])
        raw = tmp.read_text(encoding="utf-8")
        self.assertIn("中文标签", raw)
        record, error = common.parse_jsonl_line(raw.strip())
        self.assertIsNone(error)
        self.assertEqual(record["label"], "中文标签")


class TestNormalization(unittest.TestCase):
    """aliases 与行的规范化。"""

    def test_aliases_variants(self) -> None:
        self.assertEqual(jsonl_to_parquet._normalize_aliases(None), [])
        self.assertEqual(jsonl_to_parquet._normalize_aliases(""), [])
        self.assertEqual(jsonl_to_parquet._normalize_aliases("别名"), ["别名"])
        self.assertEqual(jsonl_to_parquet._normalize_aliases(["a", "b"]), ["a", "b"])

    def test_normalize_row_column_contract(self) -> None:
        row = jsonl_to_parquet._normalize_row({"entity_id": "Q1", "is_synthetic": True})
        self.assertEqual(list(row.keys()), jsonl_to_parquet.COLUMNS)
        self.assertEqual(row["aliases"], [])
        self.assertIs(row["is_synthetic"], True)


class TestWriteProtection(unittest.TestCase):
    """data/raw 目录必须不可写。"""

    def test_raw_dir_is_protected(self) -> None:
        with self.assertRaises(PermissionError):
            common.assert_writable(common.RAW_DIR / "should_not_exist.parquet")

    def test_processed_dir_is_writable(self) -> None:
        result = common.assert_writable(common.PROCESSED_DIR / "ok.parquet")
        self.assertTrue(str(result).endswith("ok.parquet"))


class TestSyntheticFixture(unittest.TestCase):
    """合成测试数据本身的约束。"""

    def setUp(self) -> None:
        self.assertFalse(
            not SAMPLE_FILE.exists(),
            f"合成数据文件不存在，请先运行 python src/make_sample_data.py（{SAMPLE_FILE}）",
        )
        self.records = [
            json.loads(line)
            for line in SAMPLE_FILE.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def test_record_count(self) -> None:
        self.assertEqual(len(self.records), 10)

    def test_all_marked_synthetic(self) -> None:
        for index, record in enumerate(self.records, start=1):
            with self.subTest(line=index):
                self.assertIs(record.get("is_synthetic"), True)
                self.assertEqual(record.get("data_origin"), "SYNTHETIC_TEST_ONLY")

    def test_edge_cases_present(self) -> None:
        qids = [r.get("entity_id") for r in self.records]
        # 无效 QID 至少 2 条
        self.assertGreaterEqual(sum(1 for q in qids if not common.is_valid_qid(q)), 2)
        # 重复 QID 至少 1 组
        self.assertGreater(len(qids) - len(set(qids)), 0)
        # 存在空标签记录
        self.assertTrue(
            any(
                common.is_blank(r.get("entity_label_zh"))
                and common.is_blank(r.get("entity_label_en"))
                for r in self.records
            )
        )
        # 存在含中文与含拉丁字母的记录
        blob = " ".join(json.dumps(r, ensure_ascii=False) for r in self.records)
        self.assertTrue(common.contains_cjk(blob))
        self.assertTrue(common.contains_latin(blob))


class TestValidationReport(unittest.TestCase):
    """校验脚本对固定 fixture 的统计结果。"""

    @classmethod
    def setUpClass(cls) -> None:
        if not SAMPLE_FILE.exists():
            raise unittest.SkipTest("合成数据文件不存在，跳过校验统计测试")
        cls.report = check_jsonl.validate_file(SAMPLE_FILE, common.load_config(), batch_size=3)

    def test_totals(self) -> None:
        totals = self.report["totals"]
        self.assertEqual(totals["total_lines"], 10)
        self.assertEqual(totals["parsed_records"], 10)
        self.assertEqual(totals["error_records"], 2)      # 两条非法 QID
        self.assertEqual(totals["warning_records"], 2)    # 一条重复 + 一条空标签
        self.assertEqual(totals["valid_records"], 7)
        self.assertEqual(totals["batches"], 4)            # batch_size=3 -> 10 行分 4 批

    def test_issue_counts(self) -> None:
        counts = self.report["issue_counts"]
        self.assertEqual(counts["invalid_qid"], 2)
        self.assertEqual(counts["duplicate_entity_id"], 1)
        self.assertEqual(counts["blank_labels"], 1)
        self.assertEqual(counts["invalid_json"], 0)
        self.assertEqual(counts["missing_required_fields"], 0)

    def test_synthetic_flag_counted(self) -> None:
        self.assertEqual(self.report["synthetic_records_marked_true"], 10)


class TestParquetExport(unittest.TestCase):
    """JSONL -> Parquet 的实际导出（在临时目录进行，不写入项目 data 目录）。"""

    def test_export_roundtrip(self) -> None:
        try:
            import pandas  # noqa: F401
            import pyarrow  # noqa: F401
        except ImportError:
            self.skipTest("pandas / pyarrow 未安装，跳过 Parquet 导出测试")

        if not SAMPLE_FILE.exists():
            self.skipTest("合成数据文件不存在")

        out_dir = Path(tempfile.mkdtemp(prefix="oscg_parquet_"))
        out_file = out_dir / "sample.parquet"

        loaded = jsonl_to_parquet.load_records(
            SAMPLE_FILE,
            common.load_config()["jsonl"]["required_fields"],
            batch_size=4,
        )
        stats = jsonl_to_parquet.write_parquet(
            loaded["rows"], out_file, compression="snappy", write_index=False
        )

        self.assertTrue(out_file.exists())
        self.assertEqual(stats["rows"], 7)     # 10 条 - 2 条非法 QID - 1 条重复
        self.assertEqual(stats["columns"], len(jsonl_to_parquet.COLUMNS))

        import pandas as pd

        df = pd.read_parquet(out_file, engine="pyarrow")
        self.assertEqual(df.shape[0], 7)
        # 多语言文本必须能原样读回
        self.assertIn("合成量子拓扑材料", df["entity_label_zh"].tolist())
        joined = " ".join(df["description"].dropna().tolist())
        self.assertIn("日本語", joined)
        self.assertIn("synthetischer", joined)


if __name__ == "__main__":
    unittest.main(verbosity=2)
