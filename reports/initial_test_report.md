# OpenSciGraph · 第一阶段初始测试报告

- 生成时间（UTC）：`2026-10-14T10:29:43Z`
- 生成脚本：`tests/run_stage1_tests.py`（基于真实运行结果自动汇总）
- 项目根目录：`E:\OpenSciGraph`

> **数据性质声明**：本次测试使用的 10 条记录由 `src/make_sample_data.py` 合成生成，**不是**真实 Wikipedia / Wikidata 数据，每条均标记 `is_synthetic = true`、`data_origin = SYNTHETIC_TEST_ONLY`。禁止将其作为真实数据使用或对外发布。

## 1. 环境信息

| 项目 | 值 |
|---|---|
| 操作系统 | Windows-11-10.0.26200-SP0 |
| Python | 3.13.14 |
| Python 路径 | `E:\OpenSciGraph\.venv\Scripts\python.exe` |
| pandas | 2.3.3 |
| pyarrow | 26.0.0 |
| numpy | 2.5.4 |

## 2. 执行步骤与结果

| # | 步骤 | 命令 | 退出码 | 结果 |
|---|---|---|---|---|
| 1 | 生成合成测试数据 | `python src/make_sample_data.py --force` | 0 | 通过 |
| 2 | 校验 JSONL | `python src/check_jsonl.py --input data/interim/sample_records.jsonl --output reports/jsonl_check_stage1.json --batch-size 3` | 1 | 通过（退出码 1 属预期） |
| 3 | 导出 Parquet | `python src/jsonl_to_parquet.py --input data/interim/sample_records.jsonl --output data/processed/sample_records.parquet --report reports/parquet_export_stage1.json --batch-size 4 --force` | 0 | 通过 |
| 4 | 单元测试（unittest） | `python -m unittest discover -s tests -v` | 0 | 通过 |

> **关于非零退出码**：
> - `校验 JSONL`：退出码 1 属预期：合成夹具故意包含 2 条非法 QID（QABC123、42）

### 2.1 生成合成测试数据

命令（工作目录 `E:\OpenSciGraph`）：

```powershell
python src/make_sample_data.py --force
```

标准输出（退出码 0）：

```text
2026-10-14 18:29:43 | INFO    | 已生成 10 条合成测试记录 -> data/interim/sample_records.jsonl
2026-10-14 18:29:43 | INFO    | 所有记录均已标记 is_synthetic=true, data_origin=SYNTHETIC_TEST_ONLY
--------------------------------------------------------------
输出文件 : data/interim/sample_records.jsonl
记录条数 : 10
生成时间 : 2026-10-14T10:29:43Z
数据性质 : 100% 合成测试数据（非真实 Wikipedia/Wikidata 数据）
--------------------------------------------------------------
```

### 2.2 校验 JSONL

命令（工作目录 `E:\OpenSciGraph`）：

```powershell
python src/check_jsonl.py --input data/interim/sample_records.jsonl --output reports/jsonl_check_stage1.json --batch-size 3
```

标准输出（退出码 1）：

```text
2026-10-14 18:29:44 | INFO    | 开始校验 JSONL：data/interim/sample_records.jsonl（batch_size=3）
--------------------------------------------------------------
输入文件      : data/interim/sample_records.jsonl  (5.0 KB)
批次大小      : 3    实际批次数: 4
--------------------------------------------------------------
总行数        : 10
空行          : 0
可解析记录    : 10
有效记录      : 7
错误记录      : 2
告警记录      : 2
--------------------------------------------------------------
JSON 解析失败 : 0
非对象结构    : 0
缺必填字段    : 0
非法 QID      : 2
重复 entity_id: 1
空标签        : 1
合成标记缺失  : 0
--------------------------------------------------------------
含中文记录    : 6
含拉丁字母记录: 7
标记为合成数据: 10
--------------------------------------------------------------
2026-10-14 18:29:44 | INFO    | 报告已写入：reports/jsonl_check_stage1.json
2026-10-14 18:29:44 | ERROR   | 校验结束：发现 2 条错误记录，需修复后重跑。
```

### 2.3 导出 Parquet

命令（工作目录 `E:\OpenSciGraph`）：

```powershell
python src/jsonl_to_parquet.py --input data/interim/sample_records.jsonl --output data/processed/sample_records.parquet --report reports/parquet_export_stage1.json --batch-size 4 --force
```

标准输出（退出码 0）：

```text
2026-10-14 18:29:45 | INFO    | 读取 JSONL：data/interim/sample_records.jsonl（batch_size=4）
2026-10-14 18:29:45 | INFO    | 解析完成：保留 7 行，跳过 3 行。
2026-10-14 18:29:50 | INFO    | Parquet 已写出：data/processed/sample_records.parquet（9.2 KB）
2026-10-14 18:29:50 | INFO    | 报告已写入：reports/parquet_export_stage1.json
--------------------------------------------------------------
输入 JSONL : data/interim/sample_records.jsonl  (5.0 KB)
输出 Parquet: data/processed/sample_records.parquet  (9.2 KB)
保留行数   : 7
列数       : 12  ['entity_id', 'entity_label_zh', 'entity_label_en', 'entity_type', 'description', 'description_lang', 'aliases', 'source', 'license', 'retrieved_at', 'is_synthetic', 'data_origin']
跳过行数   : 3（其中重复 1）
压缩方式   : snappy
--------------------------------------------------------------
```

### 2.4 单元测试（unittest）

命令（工作目录 `E:\OpenSciGraph`）：

```powershell
python -m unittest discover -s tests -v
```

标准输出（退出码 0）：

```text
（无输出）
```

标准错误：

```text
test_blank (test_pipeline.TestBlankDetection.test_blank) ... ok
test_not_blank (test_pipeline.TestBlankDetection.test_not_blank) ... ok
test_chinese_roundtrip (test_pipeline.TestJsonlIo.test_chinese_roundtrip) ... ok
test_iter_jsonl_batching (test_pipeline.TestJsonlIo.test_iter_jsonl_batching) ... ok
test_parse_broken_json (test_pipeline.TestJsonlIo.test_parse_broken_json) ... ok
test_parse_non_object (test_pipeline.TestJsonlIo.test_parse_non_object) ... ok
test_parse_valid_line (test_pipeline.TestJsonlIo.test_parse_valid_line) ... ok
test_aliases_variants (test_pipeline.TestNormalization.test_aliases_variants) ... ok
test_normalize_row_column_contract (test_pipeline.TestNormalization.test_normalize_row_column_contract) ... ok
test_export_roundtrip (test_pipeline.TestParquetExport.test_export_roundtrip) ... ok
test_invalid_qids (test_pipeline.TestQidValidation.test_invalid_qids) ... ok
test_qid_number (test_pipeline.TestQidValidation.test_qid_number) ... ok
test_valid_qids (test_pipeline.TestQidValidation.test_valid_qids) ... ok
test_all_marked_synthetic (test_pipeline.TestSyntheticFixture.test_all_marked_synthetic) ... ok
test_edge_cases_present (test_pipeline.TestSyntheticFixture.test_edge_cases_present) ... ok
test_record_count (test_pipeline.TestSyntheticFixture.test_record_count) ... ok
test_issue_counts (test_pipeline.TestValidationReport.test_issue_counts) ... ok
test_synthetic_flag_counted (test_pipeline.TestValidationReport.test_synthetic_flag_counted) ... ok
test_totals (test_pipeline.TestValidationReport.test_totals) ... ok
test_processed_dir_is_writable (test_pipeline.TestWriteProtection.test_processed_dir_is_writable) ... ok
test_raw_dir_is_protected (test_pipeline.TestWriteProtection.test_raw_dir_is_protected) ... ok

----------------------------------------------------------------------
Ran 21 tests in 0.582s

OK
```

## 3. JSONL 校验结果（真实统计）

| 指标 | 数值 |
|---|---|
| 输入文件 | `data/interim/sample_records.jsonl` |
| 文件大小 | 5.0 KB |
| 总行数 | 10 |
| 可解析记录 | 10 |
| 有效记录 | 7 |
| 错误记录 | 2 |
| 告警记录 | 2 |
| 非法 QID | 2 |
| 重复 entity_id | 1 |
| 空标签 | 1 |
| JSON 解析失败 | 0 |
| 缺必填字段 | 0 |
| 标记为合成数据的记录 | 10 |

问题明细（QID 与去重）：

```json
{
  "invalid_qid": [
    {
      "line": 7,
      "entity_id": "QABC123",
      "expected_pattern": "^Q[1-9][0-9]*$",
      "hint": "合法 QID 形如 Q42 / Q100001（字母 Q + 不以 0 开头的正整数）"
    },
    {
      "line": 8,
      "entity_id": "42",
      "expected_pattern": "^Q[1-9][0-9]*$",
      "hint": "合法 QID 形如 Q42 / Q100001（字母 Q + 不以 0 开头的正整数）"
    }
  ],
  "duplicate_entity_id": [
    {
      "line": 6,
      "entity_id": "Q900000002",
      "first_seen_line": 2
    }
  ],
  "blank_labels": [
    {
      "line": 10,
      "entity_id": "Q900000010",
      "hint": "中文与英文标签均为空"
    }
  ]
}
```

## 4. Parquet 导出结果（真实统计）

| 指标 | 数值 |
|---|---|
| 输入 | `data/interim/sample_records.jsonl`（5.0 KB） |
| 输出 | `data/processed/sample_records.parquet`（9.2 KB） |
| 写出引擎 | pyarrow |
| 压缩 | snappy |
| 保留行数 | 7 |
| 列数 | 12 |
| 跳过行数 | 3 |
| 其中重复行 | 1 |

被跳过的行（含原因）：

```json
[
  {
    "line": 6,
    "reason": "重复 entity_id（保留首条）: Q900000002",
    "entity_id": "Q900000002"
  },
  {
    "line": 7,
    "reason": "非法 QID: 'QABC123'",
    "entity_id": "QABC123"
  },
  {
    "line": 8,
    "reason": "非法 QID: '42'",
    "entity_id": "42"
  }
]
```

### 4.1 Parquet 回读验证（UTF-8 / 多语言）

| 指标 | 数值 |
|---|---|
| 回读行数 | 7 |
| 回读列数 | 12 |
| 列名 | entity_id, entity_label_zh, entity_label_en, entity_type, description, description_lang, aliases, source, license, retrieved_at, is_synthetic, data_origin |

多语言关键字命中情况：

| 关键字 | 是否命中 |
|---|---|
| `合成` | 是 |
| `日本語` | 是 |
| `synthetischer` | 是 |
| `ü` | 是 |
| `fabricated` | 是 |

列空值统计：

```json
{
  "entity_id": 0,
  "entity_label_zh": 1,
  "entity_label_en": 1,
  "entity_type": 0,
  "description": 1,
  "description_lang": 1,
  "aliases": 0,
  "source": 0,
  "license": 0,
  "retrieved_at": 0,
  "is_synthetic": 0,
  "data_origin": 0
}
```

## 5. 单元测试结果

- 命令：`python -m unittest discover -s tests -v`
- 退出码：0（0 = 全部通过）

标准错误输出（unittest 将测试结果写入 stderr）：

```text
test_blank (test_pipeline.TestBlankDetection.test_blank) ... ok
test_not_blank (test_pipeline.TestBlankDetection.test_not_blank) ... ok
test_chinese_roundtrip (test_pipeline.TestJsonlIo.test_chinese_roundtrip) ... ok
test_iter_jsonl_batching (test_pipeline.TestJsonlIo.test_iter_jsonl_batching) ... ok
test_parse_broken_json (test_pipeline.TestJsonlIo.test_parse_broken_json) ... ok
test_parse_non_object (test_pipeline.TestJsonlIo.test_parse_non_object) ... ok
test_parse_valid_line (test_pipeline.TestJsonlIo.test_parse_valid_line) ... ok
test_aliases_variants (test_pipeline.TestNormalization.test_aliases_variants) ... ok
test_normalize_row_column_contract (test_pipeline.TestNormalization.test_normalize_row_column_contract) ... ok
test_export_roundtrip (test_pipeline.TestParquetExport.test_export_roundtrip) ... ok
test_invalid_qids (test_pipeline.TestQidValidation.test_invalid_qids) ... ok
test_qid_number (test_pipeline.TestQidValidation.test_qid_number) ... ok
test_valid_qids (test_pipeline.TestQidValidation.test_valid_qids) ... ok
test_all_marked_synthetic (test_pipeline.TestSyntheticFixture.test_all_marked_synthetic) ... ok
test_edge_cases_present (test_pipeline.TestSyntheticFixture.test_edge_cases_present) ... ok
test_record_count (test_pipeline.TestSyntheticFixture.test_record_count) ... ok
test_issue_counts (test_pipeline.TestValidationReport.test_issue_counts) ... ok
test_synthetic_flag_counted (test_pipeline.TestValidationReport.test_synthetic_flag_counted) ... ok
test_totals (test_pipeline.TestValidationReport.test_totals) ... ok
test_processed_dir_is_writable (test_pipeline.TestWriteProtection.test_processed_dir_is_writable) ... ok
test_raw_dir_is_protected (test_pipeline.TestWriteProtection.test_raw_dir_is_protected) ... ok

----------------------------------------------------------------------
Ran 21 tests in 0.582s

OK
```

## 6. 实际创建 / 生成的文件

目录：

```text
.venv_c_mirror_backup
.venv_c_mirror_backup/Include
.venv_c_mirror_backup/Lib
.venv_c_mirror_backup/Lib/site-packages
.venv_c_mirror_backup/Lib/site-packages/dateutil
.venv_c_mirror_backup/Lib/site-packages/dateutil/parser
.venv_c_mirror_backup/Lib/site-packages/dateutil/tz
.venv_c_mirror_backup/Lib/site-packages/dateutil/zoneinfo
.venv_c_mirror_backup/Lib/site-packages/numpy
.venv_c_mirror_backup/Lib/site-packages/numpy/_core
.venv_c_mirror_backup/Lib/site-packages/numpy/_core/include
.venv_c_mirror_backup/Lib/site-packages/numpy/_core/include/numpy
.venv_c_mirror_backup/Lib/site-packages/numpy/_core/include/numpy/random
.venv_c_mirror_backup/Lib/site-packages/numpy/_core/lib
.venv_c_mirror_backup/Lib/site-packages/numpy/_core/lib/pkgconfig
.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests
.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/data
.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/examples
.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/examples/cython
.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/examples/limited_api
.venv_c_mirror_backup/Lib/site-packages/numpy/_pyinstaller
.venv_c_mirror_backup/Lib/site-packages/numpy/_pyinstaller/tests
.venv_c_mirror_backup/Lib/site-packages/numpy/_typing
.venv_c_mirror_backup/Lib/site-packages/numpy/_utils
.venv_c_mirror_backup/Lib/site-packages/numpy/char
.venv_c_mirror_backup/Lib/site-packages/numpy/core
.venv_c_mirror_backup/Lib/site-packages/numpy/ctypeslib
.venv_c_mirror_backup/Lib/site-packages/numpy/doc
.venv_c_mirror_backup/Lib/site-packages/numpy/f2py
.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/_backends
.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/src
.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests
.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src
.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/abstract_interface
.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/array_from_pyobj
.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/assumed_shape
.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/block_docstring
.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/callback
.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/cli
.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/common
.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/crackfortran
.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/f2cmap
.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/inplace
.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/isocintrin
.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/kind
.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/mixed
.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/modules
.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/modules/gh25337
.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/modules/gh26920
.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/negative_bounds
.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/parameter
.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/quoted_character
.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/regression
.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/return_character
.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/return_complex
.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/return_integer
.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/return_logical
.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/return_real
.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/routines
.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/size
.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/string
.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/value_attrspec
.venv_c_mirror_backup/Lib/site-packages/numpy/fft
.venv_c_mirror_backup/Lib/site-packages/numpy/fft/tests
.venv_c_mirror_backup/Lib/site-packages/numpy/lib
.venv_c_mirror_backup/Lib/site-packages/numpy/lib/tests
.venv_c_mirror_backup/Lib/site-packages/numpy/lib/tests/data
.venv_c_mirror_backup/Lib/site-packages/numpy/linalg
.venv_c_mirror_backup/Lib/site-packages/numpy/linalg/tests
.venv_c_mirror_backup/Lib/site-packages/numpy/ma
.venv_c_mirror_backup/Lib/site-packages/numpy/ma/tests
.venv_c_mirror_backup/Lib/site-packages/numpy/matrixlib
.venv_c_mirror_backup/Lib/site-packages/numpy/matrixlib/tests
.venv_c_mirror_backup/Lib/site-packages/numpy/polynomial
.venv_c_mirror_backup/Lib/site-packages/numpy/polynomial/tests
.venv_c_mirror_backup/Lib/site-packages/numpy/random
.venv_c_mirror_backup/Lib/site-packages/numpy/random/_examples
.venv_c_mirror_backup/Lib/site-packages/numpy/random/_examples/cffi
.venv_c_mirror_backup/Lib/site-packages/numpy/random/_examples/cython
.venv_c_mirror_backup/Lib/site-packages/numpy/random/_examples/numba
.venv_c_mirror_backup/Lib/site-packages/numpy/random/lib
.venv_c_mirror_backup/Lib/site-packages/numpy/random/tests
.venv_c_mirror_backup/Lib/site-packages/numpy/random/tests/data
.venv_c_mirror_backup/Lib/site-packages/numpy/rec
.venv_c_mirror_backup/Lib/site-packages/numpy/strings
.venv_c_mirror_backup/Lib/site-packages/numpy/testing
.venv_c_mirror_backup/Lib/site-packages/numpy/testing/_private
.venv_c_mirror_backup/Lib/site-packages/numpy/testing/tests
.venv_c_mirror_backup/Lib/site-packages/numpy/tests
.venv_c_mirror_backup/Lib/site-packages/numpy/typing
.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests
.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data
.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail
.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/misc
.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/pass
.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal
.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info
.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses
.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy
.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/_core
.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/_core/include
.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/_core/include/numpy
.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/_core/include/numpy/libdivide
.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/_core/src
.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/_core/src/common
.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/_core/src/common/pythoncapi-compat
.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/_core/src/highway
.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/_core/src/multiarray
.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/_core/src/npysort
.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/_core/src/npysort/x86-simd-sort
.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/_core/src/umath
.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/_core/src/umath/svml
.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/fft
.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/fft/pocketfft
.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/linalg
.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/linalg/lapack_lite
.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/ma
.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/random
.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/random/src
.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/random/src/distributions
.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/random/src/mt19937
.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/random/src/pcg64
.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/random/src/philox
.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/random/src/sfc64
.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/random/src/splitmix64
.venv_c_mirror_backup/Lib/site-packages/numpy.libs
.venv_c_mirror_backup/Lib/site-packages/pandas
.venv_c_mirror_backup/Lib/site-packages/pandas/_config
.venv_c_mirror_backup/Lib/site-packages/pandas/_libs
.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs
.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/window
.venv_c_mirror_backup/Lib/site-packages/pandas/_testing
.venv_c_mirror_backup/Lib/site-packages/pandas/api
.venv_c_mirror_backup/Lib/site-packages/pandas/api/extensions
.venv_c_mirror_backup/Lib/site-packages/pandas/api/indexers
.venv_c_mirror_backup/Lib/site-packages/pandas/api/interchange
.venv_c_mirror_backup/Lib/site-packages/pandas/api/types
.venv_c_mirror_backup/Lib/site-packages/pandas/api/typing
.venv_c_mirror_backup/Lib/site-packages/pandas/arrays
.venv_c_mirror_backup/Lib/site-packages/pandas/compat
.venv_c_mirror_backup/Lib/site-packages/pandas/compat/numpy
.venv_c_mirror_backup/Lib/site-packages/pandas/core
.venv_c_mirror_backup/Lib/site-packages/pandas/core/_numba
.venv_c_mirror_backup/Lib/site-packages/pandas/core/_numba/kernels
.venv_c_mirror_backup/Lib/site-packages/pandas/core/array_algos
.venv_c_mirror_backup/Lib/site-packages/pandas/core/arrays
.venv_c_mirror_backup/Lib/site-packages/pandas/core/arrays/arrow
.venv_c_mirror_backup/Lib/site-packages/pandas/core/arrays/sparse
.venv_c_mirror_backup/Lib/site-packages/pandas/core/computation
.venv_c_mirror_backup/Lib/site-packages/pandas/core/dtypes
.venv_c_mirror_backup/Lib/site-packages/pandas/core/groupby
.venv_c_mirror_backup/Lib/site-packages/pandas/core/indexers
.venv_c_mirror_backup/Lib/site-packages/pandas/core/indexes
.venv_c_mirror_backup/Lib/site-packages/pandas/core/interchange
.venv_c_mirror_backup/Lib/site-packages/pandas/core/internals
.venv_c_mirror_backup/Lib/site-packages/pandas/core/methods
.venv_c_mirror_backup/Lib/site-packages/pandas/core/ops
.venv_c_mirror_backup/Lib/site-packages/pandas/core/reshape
.venv_c_mirror_backup/Lib/site-packages/pandas/core/sparse
.venv_c_mirror_backup/Lib/site-packages/pandas/core/strings
.venv_c_mirror_backup/Lib/site-packages/pandas/core/tools
.venv_c_mirror_backup/Lib/site-packages/pandas/core/util
.venv_c_mirror_backup/Lib/site-packages/pandas/core/window
.venv_c_mirror_backup/Lib/site-packages/pandas/errors
.venv_c_mirror_backup/Lib/site-packages/pandas/io
.venv_c_mirror_backup/Lib/site-packages/pandas/io/clipboard
.venv_c_mirror_backup/Lib/site-packages/pandas/io/excel
.venv_c_mirror_backup/Lib/site-packages/pandas/io/formats
.venv_c_mirror_backup/Lib/site-packages/pandas/io/formats/templates
.venv_c_mirror_backup/Lib/site-packages/pandas/io/json
.venv_c_mirror_backup/Lib/site-packages/pandas/io/parsers
.venv_c_mirror_backup/Lib/site-packages/pandas/io/sas
.venv_c_mirror_backup/Lib/site-packages/pandas/plotting
.venv_c_mirror_backup/Lib/site-packages/pandas/plotting/_matplotlib
.venv_c_mirror_backup/Lib/site-packages/pandas/tests
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/api
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/apply
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arithmetic
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/boolean
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/categorical
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/datetimes
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/floating
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/integer
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/interval
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/masked
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/numpy_
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/period
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/sparse
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/string_
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/timedeltas
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/base
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/computation
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/config
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/construction
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/copy_view
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/copy_view/index
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/dtypes
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/dtypes/cast
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/array_with_attr
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/base
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/date
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/decimal
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/json
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/list
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/constructors
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/indexing
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/generic
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/aggregate
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/methods
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/transform
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/base_class
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/categorical
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimelike_
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/methods
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/interval
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/multi
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/numeric
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/object
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/period
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/period/methods
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/ranges
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/string
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/timedeltas
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/timedeltas/methods
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexing
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexing/interval
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexing/multiindex
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/interchange
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/internals
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/excel
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/formats
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/formats/style
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/json
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/common
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/dtypes
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/usecols
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/pytables
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/sas
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/xml
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/libs
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/plotting
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/plotting/frame
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/reductions
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/resample
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/reshape
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/reshape/concat
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/reshape/merge
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/interval
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/period
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/timedelta
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/timedelta/methods
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/timestamp
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/timestamp/methods
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/accessors
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/indexing
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/strings
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tools
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tseries
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tseries/frequencies
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tseries/holiday
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tseries/offsets
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tslibs
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/util
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/window
.venv_c_mirror_backup/Lib/site-packages/pandas/tests/window/moments
.venv_c_mirror_backup/Lib/site-packages/pandas/tseries
.venv_c_mirror_backup/Lib/site-packages/pandas/util
.venv_c_mirror_backup/Lib/site-packages/pandas/util/version
.venv_c_mirror_backup/Lib/site-packages/pandas-2.3.3.dist-info
.venv_c_mirror_backup/Lib/site-packages/pandas.libs
.venv_c_mirror_backup/Lib/site-packages/pip
.venv_c_mirror_backup/Lib/site-packages/pip/_internal
.venv_c_mirror_backup/Lib/site-packages/pip/_internal/cli
.venv_c_mirror_backup/Lib/site-packages/pip/_internal/commands
.venv_c_mirror_backup/Lib/site-packages/pip/_internal/distributions
.venv_c_mirror_backup/Lib/site-packages/pip/_internal/index
.venv_c_mirror_backup/Lib/site-packages/pip/_internal/locations
.venv_c_mirror_backup/Lib/site-packages/pip/_internal/metadata
.venv_c_mirror_backup/Lib/site-packages/pip/_internal/metadata/importlib
.venv_c_mirror_backup/Lib/site-packages/pip/_internal/models
.venv_c_mirror_backup/Lib/site-packages/pip/_internal/network
.venv_c_mirror_backup/Lib/site-packages/pip/_internal/operations
.venv_c_mirror_backup/Lib/site-packages/pip/_internal/operations/build
.venv_c_mirror_backup/Lib/site-packages/pip/_internal/operations/install
.venv_c_mirror_backup/Lib/site-packages/pip/_internal/req
.venv_c_mirror_backup/Lib/site-packages/pip/_internal/resolution
.venv_c_mirror_backup/Lib/site-packages/pip/_internal/resolution/legacy
.venv_c_mirror_backup/Lib/site-packages/pip/_internal/resolution/resolvelib
.venv_c_mirror_backup/Lib/site-packages/pip/_internal/utils
.venv_c_mirror_backup/Lib/site-packages/pip/_internal/vcs
.venv_c_mirror_backup/Lib/site-packages/pip/_vendor
.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/cachecontrol
.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/cachecontrol/caches
.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/certifi
.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/distlib
.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/distro
.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/idna
.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/msgpack
.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/packaging
.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/packaging/licenses
.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/pkg_resources
.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/platformdirs
.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/pygments
.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/pygments/filters
.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/pygments/formatters
.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/pygments/lexers
.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/pygments/styles
.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/pyproject_hooks
.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/pyproject_hooks/_in_process
.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/requests
.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/resolvelib
.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/resolvelib/resolvers
.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich
.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/tomli
.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/tomli_w
.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/truststore
.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3
.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/contrib
.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/contrib/emscripten
.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/http2
.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/util
.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info
.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses
.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/src
.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/src/pip
.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/src/pip/_vendor
.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/src/pip/_vendor/cachecontrol
.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/src/pip/_vendor/certifi
.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/src/pip/_vendor/distlib
.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/src/pip/_vendor/distro
.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/src/pip/_vendor/idna
.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/src/pip/_vendor/msgpack
.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/src/pip/_vendor/packaging
.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/src/pip/_vendor/pkg_resources
.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/src/pip/_vendor/platformdirs
.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/src/pip/_vendor/pygments
.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/src/pip/_vendor/pyproject_hooks
.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/src/pip/_vendor/requests
.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/src/pip/_vendor/resolvelib
.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/src/pip/_vendor/rich
.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/src/pip/_vendor/tomli
.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/src/pip/_vendor/tomli_w
.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/src/pip/_vendor/truststore
.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/src/pip/_vendor/urllib3
.venv_c_mirror_backup/Lib/site-packages/pyarrow
.venv_c_mirror_backup/Lib/site-packages/pyarrow/include
.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow
.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/acero
.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/adapters
.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/adapters/orc
.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/adapters/tensorflow
.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/array
.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/c
.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/compute
.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/compute/row
.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/csv
.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/dataset
.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/engine
.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/engine/substrait
.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/extension
.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/filesystem
.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/flight
.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/io
.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/ipc
.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/json
.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/python
.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/python/vendored
.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/telemetry
.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/tensor
.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/testing
.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util
.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/vendored
.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/vendored/datetime
.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/vendored/double-conversion
.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/vendored/pcg
.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/vendored/portable-snippets
.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/vendored/safeint
.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/vendored/xxhash
.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet
.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/api
.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/arrow
.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/encryption
.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/geospatial
.venv_c_mirror_backup/Lib/site-packages/pyarrow/includes
.venv_c_mirror_backup/Lib/site-packages/pyarrow/interchange
.venv_c_mirror_backup/Lib/site-packages/pyarrow/parquet
.venv_c_mirror_backup/Lib/site-packages/pyarrow/src
.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow
.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python
.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/vendored
.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests
.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/data
.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/data/feather
.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/data/orc
.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/data/parquet
.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/interchange
.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/parquet
.venv_c_mirror_backup/Lib/site-packages/pyarrow/vendored
.venv_c_mirror_backup/Lib/site-packages/pyarrow-26.0.0.dist-info
.venv_c_mirror_backup/Lib/site-packages/pyarrow-26.0.0.dist-info/licenses
.venv_c_mirror_backup/Lib/site-packages/pyarrow.libs
.venv_c_mirror_backup/Lib/site-packages/python_dateutil-2.9.0.post0.dist-info
.venv_c_mirror_backup/Lib/site-packages/pytz
.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo
.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa
.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America
.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Argentina
.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Indiana
.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Kentucky
.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/North_Dakota
.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Antarctica
.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Arctic
.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia
.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Atlantic
.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Australia
.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Brazil
.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Canada
.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Chile
.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Etc
.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe
.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Indian
.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Mexico
.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific
.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/US
.venv_c_mirror_backup/Lib/site-packages/pytz-2026.5.dist-info
.venv_c_mirror_backup/Lib/site-packages/six-1.17.0.dist-info
.venv_c_mirror_backup/Lib/site-packages/tzdata
.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo
.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa
.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America
.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Argentina
.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Indiana
.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Kentucky
.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/North_Dakota
.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Antarctica
.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Arctic
.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia
.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Atlantic
.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Australia
.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Brazil
.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Canada
.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Chile
.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Etc
.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe
.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Indian
.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Mexico
.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific
.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/US
.venv_c_mirror_backup/Lib/site-packages/tzdata-2026.5.dist-info
.venv_c_mirror_backup/Lib/site-packages/tzdata-2026.5.dist-info/licenses
.venv_c_mirror_backup/Lib/site-packages/tzdata-2026.5.dist-info/licenses/licenses
.venv_c_mirror_backup/Scripts
config
data
data/interim
data/processed
data/raw
docs
logs
reports
scripts
src
tests
```

文件共 5077 个：

| 文件 | 大小 |
|---|---|
| `.gitignore` | 444 B |
| `.venv_c_mirror_backup/.gitignore` | 71 B |
| `.venv_c_mirror_backup/Lib/site-packages/dateutil/__init__.py` | 620 B |
| `.venv_c_mirror_backup/Lib/site-packages/dateutil/_common.py` | 932 B |
| `.venv_c_mirror_backup/Lib/site-packages/dateutil/_version.py` | 166 B |
| `.venv_c_mirror_backup/Lib/site-packages/dateutil/easter.py` | 2.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/dateutil/parser/__init__.py` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/dateutil/parser/_parser.py` | 57.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/dateutil/parser/isoparser.py` | 12.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/dateutil/relativedelta.py` | 24.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/dateutil/rrule.py` | 65.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/dateutil/tz/__init__.py` | 444 B |
| `.venv_c_mirror_backup/Lib/site-packages/dateutil/tz/_common.py` | 12.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/dateutil/tz/_factories.py` | 2.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/dateutil/tz/tz.py` | 61.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/dateutil/tz/win.py` | 12.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/dateutil/tzwin.py` | 59 B |
| `.venv_c_mirror_backup/Lib/site-packages/dateutil/utils.py` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/dateutil/zoneinfo/__init__.py` | 5.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/dateutil/zoneinfo/dateutil-zoneinfo.tar.gz` | 152.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/dateutil/zoneinfo/rebuild.py` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/__config__.py` | 5.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/__config__.pyi` | 2.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/__init__.cython-30.pxd` | 49.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/__init__.pxd` | 399 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/__init__.py` | 25.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/__init__.pyi` | 286.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_array_api_info.py` | 10.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_array_api_info.pyi` | 4.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_configtool.py` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_configtool.pyi` | 25 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/__init__.py` | 6.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/__init__.pyi` | 10.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/_add_newdocs.py` | 217.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/_add_newdocs.pyi` | 136 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/_add_newdocs_scalars.py` | 13.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/_add_newdocs_scalars.pyi` | 565 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/_asarray.py` | 3.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/_asarray.pyi` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/_dtype.py` | 10.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/_dtype.pyi` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/_dtype_ctypes.py` | 3.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/_dtype_ctypes.pyi` | 3.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/_exceptions.py` | 5.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/_exceptions.pyi` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/_internal.py` | 29.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/_internal.pyi` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/_methods.py` | 9.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/_methods.pyi` | 531 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/_multiarray_tests.cp313-win_amd64.lib` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/_multiarray_tests.cp313-win_amd64.pyd` | 63.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/_multiarray_umath.cp313-win_amd64.lib` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/_multiarray_umath.cp313-win_amd64.pyd` | 3.7 MB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/_operand_flag_tests.cp313-win_amd64.lib` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/_operand_flag_tests.cp313-win_amd64.pyd` | 12.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/_rational_tests.cp313-win_amd64.lib` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/_rational_tests.cp313-win_amd64.pyd` | 42.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/_simd.cp313-win_amd64.lib` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/_simd.cp313-win_amd64.pyd` | 812.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/_simd.pyi` | 1013 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/_string_helpers.py` | 2.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/_string_helpers.pyi` | 370 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/_struct_ufunc_tests.cp313-win_amd64.lib` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/_struct_ufunc_tests.cp313-win_amd64.pyd` | 14.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/_type_aliases.py` | 3.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/_type_aliases.pyi` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/_ufunc_config.py` | 15.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/_ufunc_config.pyi` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/_umath_tests.cp313-win_amd64.lib` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/_umath_tests.cp313-win_amd64.pyd` | 33.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/_umath_tests.pyi` | 2.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/arrayprint.py` | 65.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/arrayprint.pyi` | 4.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/cversions.py` | 360 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/defchararray.py` | 38.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/defchararray.pyi` | 28.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/einsumfunc.py` | 58.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/einsumfunc.pyi` | 5.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/fromnumeric.py` | 144.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/fromnumeric.pyi` | 96.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/function_base.py` | 19.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/function_base.pyi` | 11.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/getlimits.py` | 14.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/getlimits.pyi` | 3.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/include/numpy/__multiarray_api.c` | 13.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/include/numpy/__multiarray_api.h` | 64.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/include/numpy/__ufunc_api.c` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/include/numpy/__ufunc_api.h` | 13.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/include/numpy/_neighborhood_iterator_imp.h` | 2.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/include/numpy/_numpyconfig.h` | 902 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/include/numpy/_public_dtype_api_table.h` | 4.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/include/numpy/arrayobject.h` | 211 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/include/numpy/arrayscalars.h` | 5.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/include/numpy/dtype_api.h` | 22.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/include/numpy/halffloat.h` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/include/numpy/ndarrayobject.h` | 11.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/include/numpy/ndarraytypes.h` | 71.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/include/numpy/npy_2_compat.h` | 15.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/include/numpy/npy_2_complexcompat.h` | 885 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/include/numpy/npy_3kcompat.h` | 10.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/include/numpy/npy_common.h` | 33.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/include/numpy/npy_cpu.h` | 4.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/include/numpy/npy_endian.h` | 2.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/include/numpy/npy_math.h` | 19.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/include/numpy/npy_no_deprecated_api.h` | 698 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/include/numpy/npy_os.h` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/include/numpy/numpyconfig.h` | 7.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/include/numpy/random/bitgen.h` | 508 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/include/numpy/random/distributions.h` | 9.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/include/numpy/random/libdivide.h` | 80.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/include/numpy/random/LICENSE.txt` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/include/numpy/ufuncobject.h` | 12.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/include/numpy/utils.h` | 4.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/lib/npymath.lib` | 153.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/lib/pkgconfig/numpy.pc` | 198 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/memmap.py` | 12.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/memmap.pyi` | 2.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/multiarray.py` | 57.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/multiarray.pyi` | 57.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/numeric.py` | 81.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/numeric.pyi` | 35.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/numerictypes.py` | 15.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/numerictypes.pyi` | 3.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/overrides.py` | 7.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/overrides.pyi` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/printoptions.py` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/printoptions.pyi` | 626 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/records.py` | 37.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/records.pyi` | 9.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/shape_base.py` | 32.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/shape_base.pyi` | 6.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/strings.py` | 51.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/strings.pyi` | 11.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/_locales.py` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/_natype.py` | 4.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/data/astype_copy.pkl` | 716 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/data/generate_umath_validation_data.cpp` | 5.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/data/recarray_from_file.fits` | 8.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/data/umath-validation-set-arccos.csv` | 61.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/data/umath-validation-set-arccosh.csv` | 61.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/data/umath-validation-set-arcsin.csv` | 61.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/data/umath-validation-set-arcsinh.csv` | 60.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/data/umath-validation-set-arctan.csv` | 60.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/data/umath-validation-set-arctanh.csv` | 61.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/data/umath-validation-set-cbrt.csv` | 60.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/data/umath-validation-set-cos.csv` | 59.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/data/umath-validation-set-cosh.csv` | 60.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/data/umath-validation-set-exp.csv` | 17.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/data/umath-validation-set-exp2.csv` | 58.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/data/umath-validation-set-expm1.csv` | 60.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/data/umath-validation-set-log.csv` | 11.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/data/umath-validation-set-log10.csv` | 68.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/data/umath-validation-set-log1p.csv` | 60.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/data/umath-validation-set-log2.csv` | 68.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/data/umath-validation-set-README.txt` | 982 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/data/umath-validation-set-sin.csv` | 58.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/data/umath-validation-set-sinh.csv` | 60.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/data/umath-validation-set-tan.csv` | 60.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/data/umath-validation-set-tanh.csv` | 60.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/examples/cython/checks.pyx` | 11.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/examples/cython/meson.build` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/examples/cython/setup.py` | 898 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/examples/limited_api/limited_api.c` | 14.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/examples/limited_api/limited_api_cython.pyx` | 5.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/examples/limited_api/meson.build` | 3.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/examples/limited_api/setup.py` | 461 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test__exceptions.py` | 2.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_abc.py` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_api.py` | 24.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_argparse.py` | 2.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_array_api_info.py` | 3.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_array_coercion.py` | 36.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_array_interface.py` | 7.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_arraymethod.py` | 3.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_arrayobject.py` | 6.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_arrayprint.py` | 52.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_casting_floatingpoint_errors.py` | 5.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_casting_unittests.py` | 41.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_conversion_utils.py` | 6.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_cpu_dispatcher.py` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_cpu_features.py` | 18.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_custom_dtypes.py` | 20.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_cython.py` | 12.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_datetime.py` | 142.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_defchararray.py` | 31.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_deprecations.py` | 19.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_dlpack.py` | 8.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_dtype.py` | 84.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_einsum.py` | 58.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_errstate.py` | 5.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_extint128.py` | 5.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_finfo.py` | 2.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_function_base.py` | 17.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_getlimits.py` | 6.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_half.py` | 25.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_hashtable.py` | 5.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_indexerrors.py` | 4.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_indexing.py` | 65.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_item_selection.py` | 7.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_limited_api.py` | 9.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_longdouble.py` | 12.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_mem_overlap.py` | 29.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_mem_policy.py` | 16.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_memmap.py` | 10.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_multiarray.py` | 443.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_multiprocessing.py` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_multithreading.py` | 23.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_nditer.py` | 139.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_nep50_promotions.py` | 10.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_numeric.py` | 160.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_numerictypes.py` | 24.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_overrides.py` | 27.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_print.py` | 6.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_protocols.py` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_records.py` | 23.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_regression.py` | 95.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_scalar_ctors.py` | 6.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_scalar_methods.py` | 13.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_scalarbuffer.py` | 5.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_scalarinherit.py` | 2.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_scalarmath.py` | 46.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_scalarprint.py` | 19.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_shape_base.py` | 32.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_simd.py` | 49.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_simd_module.py` | 4.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_stringdtype.py` | 99.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_strings.py` | 60.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_ufunc.py` | 142.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_umath.py` | 202.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_umath_accuracy.py` | 4.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_umath_complex.py` | 23.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/tests/test_unicode.py` | 13.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/umath.py` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_core/umath.pyi` | 3.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_distributor_init.py` | 436 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_distributor_init.pyi` | 28 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_expired_attrs_2_0.py` | 3.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_expired_attrs_2_0.pyi` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_globals.py` | 4.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_globals.pyi` | 297 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_pyinstaller/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_pyinstaller/__init__.pyi` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_pyinstaller/hook-numpy.py` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_pyinstaller/hook-numpy.pyi` | 156 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_pyinstaller/tests/__init__.py` | 345 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_pyinstaller/tests/pyinstaller-smoke.py` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_pyinstaller/tests/test_pyinstaller.py` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_pytesttester.py` | 5.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_pytesttester.pyi` | 521 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_typing/__init__.py` | 4.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_typing/_add_docstring.py` | 4.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_typing/_array_like.py` | 3.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_typing/_char_codes.py` | 6.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_typing/_dtype_like.py` | 3.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_typing/_extended_precision.py` | 449 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_typing/_nbit.py` | 553 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_typing/_nbit_base.py` | 3.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_typing/_nbit_base.pyi` | 811 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_typing/_nested_sequence.py` | 2.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_typing/_scalars.py` | 893 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_typing/_shape.py` | 254 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_typing/_ufunc.py` | 163 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_typing/_ufunc.pyi` | 29.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_utils/__init__.py` | 3.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_utils/__init__.pyi` | 655 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_utils/_conversions.py` | 347 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_utils/_conversions.pyi` | 122 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_utils/_inspect.py` | 7.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_utils/_inspect.pyi` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_utils/_pep440.py` | 14.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/_utils/_pep440.pyi` | 3.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/char/__init__.py` | 859 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/char/__init__.pyi` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/conftest.py` | 8.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/core/__init__.py` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/core/__init__.pyi` | 795 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/core/_dtype.py` | 333 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/core/_dtype.pyi` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/core/_dtype_ctypes.py` | 361 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/core/_dtype_ctypes.pyi` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/core/_internal.py` | 976 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/core/_internal.pyi` | 21 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/core/_multiarray_umath.py` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/core/_utils.py` | 944 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/core/arrayprint.py` | 349 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/core/arrayprint.pyi` | 116 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/core/defchararray.py` | 357 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/core/defchararray.pyi` | 120 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/core/einsumfunc.py` | 349 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/core/einsumfunc.pyi` | 116 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/core/fromnumeric.py` | 353 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/core/fromnumeric.pyi` | 118 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/core/function_base.py` | 361 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/core/function_base.pyi` | 122 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/core/getlimits.py` | 345 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/core/getlimits.pyi` | 114 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/core/multiarray.py` | 818 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/core/multiarray.pyi` | 116 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/core/numeric.py` | 372 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/core/numeric.pyi` | 110 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/core/numerictypes.py` | 357 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/core/numerictypes.pyi` | 120 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/core/overrides.py` | 345 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/core/overrides.pyi` | 532 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/core/records.py` | 337 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/core/records.pyi` | 110 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/core/shape_base.py` | 349 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/core/shape_base.pyi` | 116 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/core/umath.py` | 329 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/core/umath.pyi` | 106 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/ctypeslib/__init__.py` | 206 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/ctypeslib/__init__.pyi` | 382 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/ctypeslib/_ctypeslib.py` | 19.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/ctypeslib/_ctypeslib.pyi` | 8.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/doc/ufuncs.py` | 5.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/dtypes.py` | 2.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/dtypes.pyi` | 15.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/exceptions.py` | 7.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/exceptions.pyi` | 821 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/__init__.py` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/__init__.pyi` | 118 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/__main__.py` | 135 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/__version__.py` | 49 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/__version__.pyi` | 46 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/_backends/__init__.py` | 194 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/_backends/__init__.pyi` | 128 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/_backends/_backend.py` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/_backends/_backend.pyi` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/_backends/_meson.py` | 8.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/_backends/_meson.pyi` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/_backends/meson.build.template` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/_isocbind.py` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/_isocbind.pyi` | 352 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/_src_pyf.py` | 7.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/_src_pyf.pyi` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/auxfuncs.py` | 27.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/auxfuncs.pyi` | 8.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/capi_maps.py` | 29.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/capi_maps.pyi` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/cb_rules.py` | 24.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/cb_rules.pyi` | 512 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/cfuncs.py` | 54.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/cfuncs.pyi` | 810 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/common_rules.py` | 5.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/common_rules.pyi` | 332 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/crackfortran.py` | 147.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/crackfortran.pyi` | 10.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/diagnose.py` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/diagnose.pyi` | 24 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/f2py2e.py` | 27.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/f2py2e.pyi` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/f90mod_rules.py` | 10.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/f90mod_rules.pyi` | 467 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/func2subr.py` | 10.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/func2subr.pyi` | 393 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/rules.py` | 63.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/rules.pyi` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/setup.cfg` | 50 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/src/fortranobject.c` | 47.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/src/fortranobject.h` | 5.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/symbolic.py` | 53.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/symbolic.pyi` | 6.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/__init__.py` | 345 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/abstract_interface/foo.f90` | 692 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/abstract_interface/gh18403_mod.f90` | 111 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/array_from_pyobj/wrapmodule.c` | 8.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/assumed_shape/.f2py_f2cmap` | 30 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/assumed_shape/foo_free.f90` | 494 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/assumed_shape/foo_mod.f90` | 540 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/assumed_shape/foo_use.f90` | 288 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/assumed_shape/precision.f90` | 134 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/block_docstring/foo.f` | 103 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/callback/foo.f` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/callback/gh17797.f90` | 155 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/callback/gh18335.f90` | 523 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/callback/gh25211.f` | 189 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/callback/gh25211.pyf` | 465 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/callback/gh26681.f90` | 584 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/cli/gh_22819.pyf` | 148 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/cli/hi77.f` | 74 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/cli/hiworld.f90` | 54 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/common/block.f` | 235 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/common/gh19161.f90` | 203 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/crackfortran/accesstype.f90` | 221 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/crackfortran/common_with_division.f` | 511 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/crackfortran/data_common.f` | 201 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/crackfortran/data_multiplier.f` | 202 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/crackfortran/data_stmts.f90` | 713 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/crackfortran/data_with_comments.f` | 183 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/crackfortran/foo_deps.f90` | 134 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/crackfortran/gh15035.f` | 391 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/crackfortran/gh17859.f` | 352 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/crackfortran/gh22648.pyf` | 248 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/crackfortran/gh23533.f` | 131 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/crackfortran/gh23598.f90` | 105 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/crackfortran/gh23598Warn.f90` | 216 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/crackfortran/gh23879.f90` | 364 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/crackfortran/gh27697.f90` | 376 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/crackfortran/gh2848.f90` | 295 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/crackfortran/operators.f90` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/crackfortran/privatemod.f90` | 185 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/crackfortran/publicmod.f90` | 177 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/crackfortran/pubprivmod.f90` | 175 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/crackfortran/unicode_comment.f90` | 102 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/f2cmap/.f2py_f2cmap` | 83 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/f2cmap/isoFortranEnvMap.f90` | 307 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/inplace/foo.f` | 1008 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/isocintrin/isoCtests.f90` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/kind/foo.f90` | 367 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/mixed/foo.f` | 90 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/mixed/foo_fixed.f90` | 187 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/mixed/foo_free.f90` | 147 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/modules/gh25337/data.f90` | 188 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/modules/gh25337/use_data.f90` | 185 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/modules/gh26920/two_mods_with_no_public_entities.f90` | 423 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/modules/gh26920/two_mods_with_one_public_routine.f90` | 424 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/modules/module_data_docstring.f90` | 236 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/modules/use_modules.f90` | 418 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/negative_bounds/issue_20853.f90` | 164 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/parameter/constant_array.f90` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/parameter/constant_both.f90` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/parameter/constant_compound.f90` | 484 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/parameter/constant_integer.f90` | 634 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/parameter/constant_non_compound.f90` | 632 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/parameter/constant_real.f90` | 633 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/quoted_character/foo.f` | 496 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/regression/AB.inc` | 17 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/regression/assignOnlyModule.f90` | 633 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/regression/complex_struct_compat.f90` | 243 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/regression/complex_struct_compat.pyf` | 418 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/regression/datonly.f90` | 409 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/regression/f77comments.f` | 652 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/regression/f77fixedform.f95` | 144 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/regression/f90continuation.f90` | 285 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/regression/incfile.f90` | 97 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/regression/inout.f90` | 286 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/regression/lower_f2py_fortran.f90` | 105 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/regression/mod_derived_types.f90` | 589 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/return_character/foo77.f` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/return_character/foo90.f90` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/return_complex/foo77.f` | 1018 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/return_complex/foo90.f90` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/return_integer/foo77.f` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/return_integer/foo90.f90` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/return_logical/foo77.f` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/return_logical/foo90.f90` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/return_real/foo77.f` | 978 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/return_real/foo90.f90` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/routines/funcfortranname.f` | 128 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/routines/funcfortranname.pyf` | 451 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/routines/subrout.f` | 94 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/routines/subrout.pyf` | 332 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/size/foo.f90` | 859 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/string/char.f90` | 647 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/string/fixed_string.f90` | 729 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/string/gh24008.f` | 225 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/string/gh24662.f90` | 204 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/string/gh25286.f90` | 318 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/string/gh25286.pyf` | 393 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/string/gh25286_bc.pyf` | 396 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/string/scalar_string.f90` | 185 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/string/string.f` | 260 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/src/value_attrspec/gh21665.f90` | 199 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/test_abstract_interface.py` | 837 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/test_array_from_pyobj.py` | 26.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/test_assumed_shape.py` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/test_block_docstring.py` | 455 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/test_callback.py` | 7.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/test_capi_maps.py` | 406 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/test_character.py` | 22.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/test_common.py` | 686 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/test_crackfortran.py` | 16.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/test_data.py` | 2.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/test_docs.py` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/test_f2cmap.py` | 440 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/test_f2py2e.py` | 29.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/test_inplace.py` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/test_isoc.py` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/test_kind.py` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/test_mixed.py` | 744 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/test_modules.py` | 2.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/test_parameter.py` | 4.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/test_pyf_src.py` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/test_quoted_character.py` | 622 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/test_regression.py` | 6.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/test_return_character.py` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/test_return_complex.py` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/test_return_integer.py` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/test_return_logical.py` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/test_return_real.py` | 3.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/test_routines.py` | 824 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/test_semicolon_split.py` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/test_size.py` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/test_string.py` | 3.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/test_symbolic.py` | 18.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/test_value_attrspec.py` | 341 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/tests/util.py` | 12.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/use_rules.py` | 3.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/f2py/use_rules.pyi` | 433 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/fft/__init__.py` | 8.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/fft/__init__.pyi` | 642 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/fft/_helper.py` | 6.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/fft/_helper.pyi` | 4.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/fft/_pocketfft.py` | 62.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/fft/_pocketfft.pyi` | 34.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/fft/_pocketfft_umath.cp313-win_amd64.lib` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/fft/_pocketfft_umath.cp313-win_amd64.pyd` | 270.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/fft/tests/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/fft/tests/test_helper.py` | 6.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/fft/tests/test_pocketfft.py` | 25.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/__init__.py` | 2.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/__init__.pyi` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_array_utils_impl.py` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_array_utils_impl.pyi` | 512 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_arraypad_impl.py` | 33.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_arraypad_impl.pyi` | 2.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_arraysetops_impl.py` | 37.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_arraysetops_impl.pyi` | 14.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_arrayterator_impl.py` | 7.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_arrayterator_impl.pyi` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_datasource.py` | 22.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_datasource.pyi` | 1008 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_format_impl.py` | 37.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_format_impl.pyi` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_function_base_impl.py` | 195.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_function_base_impl.pyi` | 77.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_histograms_impl.py` | 38.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_histograms_impl.pyi` | 10.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_index_tricks_impl.py` | 31.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_index_tricks_impl.pyi` | 11.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_iotools.py` | 31.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_iotools.pyi` | 3.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_nanfunctions_impl.py` | 71.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_nanfunctions_impl.pyi` | 864 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_npyio_impl.py` | 96.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_npyio_impl.pyi` | 9.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_polynomial_impl.py` | 44.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_polynomial_impl.pyi` | 10.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_scimath_impl.py` | 15.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_scimath_impl.pyi` | 2.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_shape_base_impl.py` | 38.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_shape_base_impl.pyi` | 7.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_stride_tricks_impl.py` | 21.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_stride_tricks_impl.pyi` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_twodim_base_impl.py` | 35.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_twodim_base_impl.pyi` | 13.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_type_check_impl.py` | 20.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_type_check_impl.pyi` | 13.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_ufunclike_impl.py` | 6.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_ufunclike_impl.pyi` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_user_array_impl.py` | 8.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_user_array_impl.pyi` | 9.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_utils_impl.py` | 17.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_utils_impl.pyi` | 638 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_version.py` | 4.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/_version.pyi` | 790 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/array_utils.py` | 151 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/array_utils.pyi` | 197 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/format.py` | 501 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/format.pyi` | 876 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/introspect.py` | 2.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/introspect.pyi` | 155 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/mixins.py` | 7.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/mixins.pyi` | 3.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/npyio.py` | 69 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/npyio.pyi` | 121 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/recfunctions.py` | 59.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/recfunctions.pyi` | 13.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/scimath.py` | 182 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/scimath.pyi` | 245 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/stride_tricks.py` | 89 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/stride_tricks.pyi` | 128 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/tests/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/tests/data/py2-np0-objarr.npy` | 258 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/tests/data/py2-objarr.npy` | 258 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/tests/data/py2-objarr.npz` | 366 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/tests/data/py3-objarr.npy` | 325 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/tests/data/py3-objarr.npz` | 453 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/tests/data/python3.npy` | 96 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/tests/data/win64python2.npy` | 96 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/tests/test__datasource.py` | 10.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/tests/test__iotools.py` | 13.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/tests/test__version.py` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/tests/test_array_utils.py` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/tests/test_arraypad.py` | 56.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/tests/test_arraysetops.py` | 46.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/tests/test_arrayterator.py` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/tests/test_format.py` | 41.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/tests/test_function_base.py` | 180.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/tests/test_histograms.py` | 34.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/tests/test_index_tricks.py` | 24.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/tests/test_io.py` | 106.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/tests/test_loadtxt.py` | 39.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/tests/test_mixins.py` | 7.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/tests/test_nanfunctions.py` | 54.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/tests/test_packbits.py` | 17.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/tests/test_polynomial.py` | 12.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/tests/test_recfunctions.py` | 44.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/tests/test_regression.py` | 7.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/tests/test_shape_base.py` | 27.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/tests/test_stride_tricks.py` | 30.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/tests/test_twodim_base.py` | 19.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/tests/test_type_check.py` | 14.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/tests/test_ufunclike.py` | 4.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/tests/test_utils.py` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/user_array.py` | 64 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/lib/user_array.pyi` | 82 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/linalg/__init__.py` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/linalg/__init__.pyi` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/linalg/_linalg.py` | 116.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/linalg/_linalg.pyi` | 58.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/linalg/_umath_linalg.cp313-win_amd64.lib` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/linalg/_umath_linalg.cp313-win_amd64.pyd` | 110.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/linalg/_umath_linalg.pyi` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/linalg/lapack_lite.cp313-win_amd64.lib` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/linalg/lapack_lite.cp313-win_amd64.pyd` | 18.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/linalg/lapack_lite.pyi` | 2.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/linalg/tests/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/linalg/tests/test_deprecations.py` | 637 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/linalg/tests/test_linalg.py` | 88.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/linalg/tests/test_regression.py` | 7.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/ma/__init__.py` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/ma/__init__.pyi` | 7.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/ma/API_CHANGES.txt` | 3.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/ma/core.py` | 294.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/ma/core.pyi` | 164.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/ma/extras.py` | 68.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/ma/extras.pyi` | 24.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/ma/LICENSE` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/ma/mrecords.py` | 25.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/ma/mrecords.pyi` | 11.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/ma/README.rst` | 9.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/ma/tests/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/ma/tests/test_arrayobject.py` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/ma/tests/test_core.py` | 235.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/ma/tests/test_deprecations.py` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/ma/tests/test_extras.py` | 75.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/ma/tests/test_mrecords.py` | 19.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/ma/tests/test_old_ma.py` | 33.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/ma/tests/test_regression.py` | 2.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/ma/tests/test_subclassing.py` | 17.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/ma/testutils.py` | 10.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/ma/testutils.pyi` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/matlib.py` | 10.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/matlib.pyi` | 10.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/matrixlib/__init__.py` | 255 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/matrixlib/__init__.pyi` | 202 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/matrixlib/defmatrix.py` | 31.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/matrixlib/defmatrix.pyi` | 10.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/matrixlib/tests/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/matrixlib/tests/test_defmatrix.py` | 15.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/matrixlib/tests/test_interaction.py` | 11.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/matrixlib/tests/test_masked_matrix.py` | 8.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/matrixlib/tests/test_matrix_linalg.py` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/matrixlib/tests/test_multiarray.py` | 572 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/matrixlib/tests/test_numeric.py` | 465 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/matrixlib/tests/test_regression.py` | 965 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/polynomial/__init__.py` | 6.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/polynomial/__init__.pyi` | 743 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/polynomial/_polybase.py` | 39.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/polynomial/_polybase.pyi` | 7.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/polynomial/_polytypes.pyi` | 17.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/polynomial/chebyshev.py` | 64.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/polynomial/chebyshev.pyi` | 5.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/polynomial/hermite.py` | 57.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/polynomial/hermite.pyi` | 2.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/polynomial/hermite_e.py` | 54.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/polynomial/hermite_e.pyi` | 2.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/polynomial/laguerre.py` | 54.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/polynomial/laguerre.pyi` | 2.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/polynomial/legendre.py` | 53.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/polynomial/legendre.pyi` | 2.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/polynomial/polynomial.py` | 55.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/polynomial/polynomial.pyi` | 3.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/polynomial/polyutils.py` | 22.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/polynomial/polyutils.pyi` | 10.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/polynomial/tests/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/polynomial/tests/test_chebyshev.py` | 21.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/polynomial/tests/test_classes.py` | 19.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/polynomial/tests/test_hermite.py` | 19.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/polynomial/tests/test_hermite_e.py` | 19.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/polynomial/tests/test_laguerre.py` | 18.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/polynomial/tests/test_legendre.py` | 19.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/polynomial/tests/test_polynomial.py` | 24.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/polynomial/tests/test_polyutils.py` | 3.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/polynomial/tests/test_printing.py` | 21.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/polynomial/tests/test_symbol.py` | 5.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/py.typed` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/__init__.pxd` | 445 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/__init__.py` | 7.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/__init__.pyi` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/_bounded_integers.cp313-win_amd64.lib` | 17.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/_bounded_integers.cp313-win_amd64.pyd` | 204.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/_bounded_integers.pxd` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/_bounded_integers.pyi` | 25 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/_common.cp313-win_amd64.lib` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/_common.cp313-win_amd64.pyd` | 170.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/_common.pxd` | 5.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/_common.pyi` | 474 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/_examples/cffi/extending.py` | 926 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/_examples/cffi/parse.py` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/_examples/cython/extending.pyx` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/_examples/cython/extending_distributions.pyx` | 3.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/_examples/cython/meson.build` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/_examples/numba/extending.py` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/_examples/numba/extending_distributions.py` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/_generator.cp313-win_amd64.lib` | 18.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/_generator.cp313-win_amd64.pyd` | 608.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/_generator.pyi` | 35.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/_mt19937.cp313-win_amd64.lib` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/_mt19937.cp313-win_amd64.pyd` | 90.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/_mt19937.pyi` | 882 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/_pcg64.cp313-win_amd64.lib` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/_pcg64.cp313-win_amd64.pyd` | 101.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/_pcg64.pyi` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/_philox.cp313-win_amd64.lib` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/_philox.cp313-win_amd64.pyd` | 86.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/_philox.pyi` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/_pickle.py` | 2.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/_pickle.pyi` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/_sfc64.cp313-win_amd64.lib` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/_sfc64.cp313-win_amd64.pyd` | 61.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/_sfc64.pyi` | 749 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/bit_generator.cp313-win_amd64.lib` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/bit_generator.cp313-win_amd64.pyd` | 168.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/bit_generator.pxd` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/bit_generator.pyi` | 3.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/c_distributions.pxd` | 6.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/lib/npyrandom.lib` | 146.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/LICENSE.md` | 3.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/mtrand.cp313-win_amd64.lib` | 16.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/mtrand.cp313-win_amd64.pyd` | 509.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/mtrand.pyi` | 27.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/tests/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/tests/data/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/tests/data/generator_pcg64_np121.pkl.gz` | 203 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/tests/data/generator_pcg64_np126.pkl.gz` | 208 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/tests/data/mt19937-testset-1.csv` | 16.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/tests/data/mt19937-testset-2.csv` | 16.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/tests/data/pcg64-testset-1.csv` | 24.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/tests/data/pcg64-testset-2.csv` | 24.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/tests/data/pcg64dxsm-testset-1.csv` | 24.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/tests/data/pcg64dxsm-testset-2.csv` | 24.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/tests/data/philox-testset-1.csv` | 24.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/tests/data/philox-testset-2.csv` | 24.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/tests/data/sfc64-testset-1.csv` | 24.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/tests/data/sfc64-testset-2.csv` | 24.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/tests/data/sfc64_np126.pkl.gz` | 290 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/tests/test_direct.py` | 21.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/tests/test_extending.py` | 4.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/tests/test_generator_mt19937.py` | 119.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/tests/test_generator_mt19937_regressions.py` | 9.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/tests/test_random.py` | 71.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/tests/test_randomstate.py` | 88.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/tests/test_randomstate_regression.py` | 9.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/tests/test_regression.py` | 6.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/tests/test_seed_sequence.py` | 4.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/random/tests/test_smoke.py` | 30.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/rec/__init__.py` | 85 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/rec/__init__.pyi` | 370 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/strings/__init__.py` | 85 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/strings/__init__.pyi` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/testing/__init__.py` | 603 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/testing/__init__.pyi` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/testing/_private/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/testing/_private/__init__.pyi` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/testing/_private/extbuild.py` | 7.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/testing/_private/extbuild.pyi` | 678 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/testing/_private/utils.py` | 101.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/testing/_private/utils.pyi` | 14.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/testing/overrides.py` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/testing/overrides.pyi` | 406 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/testing/print_coercion_tables.py` | 6.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/testing/print_coercion_tables.pyi` | 846 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/testing/tests/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/testing/tests/test_utils.py` | 81.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/tests/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/tests/test__all__.py` | 232 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/tests/test_configtool.py` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/tests/test_ctypeslib.py` | 13.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/tests/test_lazyloading.py` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/tests/test_matlib.py` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/tests/test_numpy_config.py` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/tests/test_numpy_version.py` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/tests/test_public_api.py` | 25.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/tests/test_reloading.py` | 2.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/tests/test_scripts.py` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/tests/test_warnings.py` | 2.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/__init__.py` | 6.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/__init__.pyi` | 293 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/mypy_plugin.py` | 6.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/arithmetic.pyi` | 3.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/array_constructors.pyi` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/array_like.pyi` | 511 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/array_pad.pyi` | 143 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/arrayprint.pyi` | 543 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/arrayterator.pyi` | 477 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/bitwise_ops.pyi` | 397 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/char.pyi` | 2.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/chararray.pyi` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/comparisons.pyi` | 763 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/constants.pyi` | 81 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/datasource.pyi` | 436 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/dtype.pyi` | 322 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/einsumfunc.pyi` | 470 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/flatiter.pyi` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/fromnumeric.pyi` | 5.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/histograms.pyi` | 388 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/index_tricks.pyi` | 536 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/lib_function_base.pyi` | 2.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/lib_polynomial.pyi` | 966 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/lib_utils.pyi` | 101 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/lib_version.pyi` | 160 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/linalg.pyi` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/ma.pyi` | 6.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/memmap.pyi` | 174 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/modules.pyi` | 620 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/multiarray.pyi` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/ndarray.pyi` | 392 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/ndarray_misc.pyi` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/nditer.pyi` | 265 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/nested_sequence.pyi` | 481 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/npyio.pyi` | 626 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/numerictypes.pyi` | 129 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/random.pyi` | 2.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/rec.pyi` | 758 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/scalars.pyi` | 2.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/shape.pyi` | 139 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/shape_base.pyi` | 165 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/stride_tricks.pyi` | 339 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/strings.pyi` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/testing.pyi` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/twodim_base.pyi` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/type_check.pyi` | 394 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/ufunc_config.pyi` | 610 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/ufunclike.pyi` | 670 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/ufuncs.pyi` | 522 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/fail/warnings_and_errors.pyi` | 205 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/misc/extended_precision.pyi` | 331 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/mypy.ini` | 222 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/pass/arithmetic.py` | 8.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/pass/array_constructors.py` | 2.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/pass/array_like.py` | 976 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/pass/arrayprint.py` | 876 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/pass/arrayterator.py` | 422 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/pass/bitwise_ops.py` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/pass/comparisons.py` | 3.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/pass/dtype.py` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/pass/einsumfunc.py` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/pass/flatiter.py` | 288 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/pass/fromnumeric.py` | 4.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/pass/index_tricks.py` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/pass/lib_user_array.py` | 640 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/pass/lib_utils.py` | 336 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/pass/lib_version.py` | 317 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/pass/literal.py` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/pass/ma.py` | 4.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/pass/mod.py` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/pass/modules.py` | 670 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/pass/multiarray.py` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/pass/ndarray_conversion.py` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/pass/ndarray_misc.py` | 3.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/pass/ndarray_shape_manipulation.py` | 855 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/pass/nditer.py` | 67 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/pass/numeric.py` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/pass/numerictypes.py` | 348 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/pass/random.py` | 61.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/pass/recfunctions.py` | 5.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/pass/scalars.py` | 4.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/pass/shape.py` | 458 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/pass/simple.py` | 2.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/pass/ufunc_config.py` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/pass/ufunclike.py` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/pass/ufuncs.py` | 438 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/pass/warnings_and_errors.py` | 167 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/arithmetic.pyi` | 27.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/array_api_info.pyi` | 3.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/array_constructors.pyi` | 17.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/arraypad.pyi` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/arrayprint.pyi` | 797 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/arraysetops.pyi` | 4.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/arrayterator.pyi` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/bitwise_ops.pyi` | 4.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/char.pyi` | 11.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/chararray.pyi` | 5.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/comparisons.pyi` | 7.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/constants.pyi` | 347 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/ctypeslib.pyi` | 4.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/datasource.pyi` | 606 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/dtype.pyi` | 7.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/einsumfunc.pyi` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/emath.pyi` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/fft.pyi` | 8.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/flatiter.pyi` | 3.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/fromnumeric.pyi` | 31.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/getlimits.pyi` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/histograms.pyi` | 4.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/index_tricks.pyi` | 6.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/lib_function_base.pyi` | 20.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/lib_polynomial.pyi` | 5.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/lib_utils.pyi` | 453 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/lib_version.pyi` | 592 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/linalg.pyi` | 29.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/ma.pyi` | 50.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/matrix.pyi` | 2.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/memmap.pyi` | 792 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/mod.pyi` | 7.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/modules.pyi` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/multiarray.pyi` | 15.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/nbit_base_example.pyi` | 537 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/ndarray_assignability.pyi` | 2.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/ndarray_conversion.pyi` | 3.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/ndarray_misc.pyi` | 20.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/ndarray_shape_manipulation.pyi` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/nditer.pyi` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/nested_sequence.pyi` | 637 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/npyio.pyi` | 3.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/numeric.pyi` | 9.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/numerictypes.pyi` | 584 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/polynomial_polybase.pyi` | 7.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/polynomial_polyutils.pyi` | 10.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/polynomial_series.pyi` | 6.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/random.pyi` | 89.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/rec.pyi` | 3.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/scalars.pyi` | 11.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/shape.pyi` | 275 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/shape_base.pyi` | 4.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/stride_tricks.pyi` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/strings.pyi` | 9.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/testing.pyi` | 10.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/twodim_base.pyi` | 8.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/type_check.pyi` | 4.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/ufunc_config.pyi` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/ufunclike.pyi` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/ufuncs.pyi` | 6.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/data/reveal/warnings_and_errors.pyi` | 460 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/test_isfile.py` | 989 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/test_runtime.py` | 3.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/typing/tests/test_typing.py` | 6.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/version.py` | 304 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy/version.pyi` | 278 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/DELVEWHEEL` | 462 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/entry_points.txt` | 220 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/INSTALLER` | 4 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/LICENSE.txt` | 44.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/_core/include/numpy/libdivide/LICENSE.txt` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/_core/src/common/pythoncapi-compat/COPYING` | 704 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/_core/src/highway/LICENSE` | 20.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/_core/src/multiarray/dragon4_LICENSE.txt` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/_core/src/npysort/x86-simd-sort/LICENSE.md` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/_core/src/umath/svml/LICENSE` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/fft/pocketfft/LICENSE.md` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/linalg/lapack_lite/LICENSE.txt` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/ma/LICENSE` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/random/LICENSE.md` | 3.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/random/src/distributions/LICENSE.md` | 2.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/random/src/mt19937/LICENSE.md` | 2.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/random/src/pcg64/LICENSE.md` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/random/src/philox/LICENSE.md` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/random/src/sfc64/LICENSE.md` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/licenses/numpy/random/src/splitmix64/LICENSE.md` | 340 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/METADATA` | 6.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/RECORD` | 110.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy-2.5.4.dist-info/WHEEL` | 85 B |
| `.venv_c_mirror_backup/Lib/site-packages/numpy.libs/libscipy_openblas64_-ed4f167a5330424524f45258e7ca2c8d.dll` | 19.6 MB |
| `.venv_c_mirror_backup/Lib/site-packages/numpy.libs/msvcp140-a4c2229bdc2a2a630acdc095b4d86008.dll` | 561.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/__init__.py` | 8.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_config/__init__.py` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_config/config.py` | 24.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_config/dates.py` | 668 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_config/display.py` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_config/localization.py` | 5.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/__init__.py` | 673 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/algos.cp313-win_amd64.lib` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/algos.cp313-win_amd64.pyd` | 1.6 MB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/algos.pyi` | 14.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/arrays.cp313-win_amd64.lib` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/arrays.cp313-win_amd64.pyd` | 90.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/arrays.pyi` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/byteswap.cp313-win_amd64.lib` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/byteswap.cp313-win_amd64.pyd` | 41.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/byteswap.pyi` | 423 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/groupby.cp313-win_amd64.lib` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/groupby.cp313-win_amd64.pyd` | 1.9 MB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/groupby.pyi` | 7.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/hashing.cp313-win_amd64.lib` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/hashing.cp313-win_amd64.pyd` | 152.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/hashing.pyi` | 181 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/hashtable.cp313-win_amd64.lib` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/hashtable.cp313-win_amd64.pyd` | 1.7 MB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/hashtable.pyi` | 7.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/index.cp313-win_amd64.lib` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/index.cp313-win_amd64.pyd` | 662.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/index.pyi` | 3.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/indexing.cp313-win_amd64.lib` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/indexing.cp313-win_amd64.pyd` | 49.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/indexing.pyi` | 427 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/internals.cp313-win_amd64.lib` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/internals.cp313-win_amd64.pyd` | 294.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/internals.pyi` | 2.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/interval.cp313-win_amd64.lib` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/interval.cp313-win_amd64.pyd` | 1004.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/interval.pyi` | 5.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/join.cp313-win_amd64.lib` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/join.cp313-win_amd64.pyd` | 1002.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/join.pyi` | 2.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/json.cp313-win_amd64.lib` | 2.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/json.cp313-win_amd64.pyd` | 50.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/json.pyi` | 496 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/lib.cp313-win_amd64.lib` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/lib.cp313-win_amd64.pyd` | 613.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/lib.pyi` | 7.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/missing.cp313-win_amd64.lib` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/missing.cp313-win_amd64.pyd` | 152.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/missing.pyi` | 524 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/ops.cp313-win_amd64.lib` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/ops.cp313-win_amd64.pyd` | 187.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/ops.pyi` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/ops_dispatch.cp313-win_amd64.lib` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/ops_dispatch.cp313-win_amd64.pyd` | 44.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/ops_dispatch.pyi` | 124 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/pandas_datetime.cp313-win_amd64.lib` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/pandas_datetime.cp313-win_amd64.pyd` | 31.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/pandas_parser.cp313-win_amd64.lib` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/pandas_parser.cp313-win_amd64.pyd` | 29.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/parsers.cp313-win_amd64.lib` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/parsers.cp313-win_amd64.pyd` | 350.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/parsers.pyi` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/properties.cp313-win_amd64.lib` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/properties.cp313-win_amd64.pyd` | 62.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/properties.pyi` | 717 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/reshape.cp313-win_amd64.lib` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/reshape.cp313-win_amd64.pyd` | 223.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/reshape.pyi` | 419 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/sas.cp313-win_amd64.lib` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/sas.cp313-win_amd64.pyd` | 183.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/sas.pyi` | 224 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/sparse.cp313-win_amd64.lib` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/sparse.cp313-win_amd64.pyd` | 733.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/sparse.pyi` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/testing.cp313-win_amd64.lib` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/testing.cp313-win_amd64.pyd` | 78.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/testing.pyi` | 243 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslib.cp313-win_amd64.lib` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslib.cp313-win_amd64.pyd` | 234.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslib.pyi` | 969 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/__init__.py` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/base.cp313-win_amd64.lib` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/base.cp313-win_amd64.pyd` | 45.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/ccalendar.cp313-win_amd64.lib` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/ccalendar.cp313-win_amd64.pyd` | 59.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/ccalendar.pyi` | 502 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/conversion.cp313-win_amd64.lib` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/conversion.cp313-win_amd64.pyd` | 210.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/conversion.pyi` | 300 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/dtypes.cp313-win_amd64.lib` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/dtypes.cp313-win_amd64.pyd` | 141.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/dtypes.pyi` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/fields.cp313-win_amd64.lib` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/fields.cp313-win_amd64.pyd` | 251.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/fields.pyi` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/nattype.cp313-win_amd64.lib` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/nattype.cp313-win_amd64.pyd` | 184.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/nattype.pyi` | 4.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/np_datetime.cp313-win_amd64.lib` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/np_datetime.cp313-win_amd64.pyd` | 104.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/np_datetime.pyi` | 831 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/offsets.cp313-win_amd64.lib` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/offsets.cp313-win_amd64.pyd` | 761.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/offsets.pyi` | 8.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/parsing.cp313-win_amd64.lib` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/parsing.cp313-win_amd64.pyd` | 291.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/parsing.pyi` | 914 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/period.cp313-win_amd64.lib` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/period.cp313-win_amd64.pyd` | 370.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/period.pyi` | 3.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/strptime.cp313-win_amd64.lib` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/strptime.cp313-win_amd64.pyd` | 271.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/strptime.pyi` | 349 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/timedeltas.cp313-win_amd64.lib` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/timedeltas.cp313-win_amd64.pyd` | 430.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/timedeltas.pyi` | 4.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/timestamps.cp313-win_amd64.lib` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/timestamps.cp313-win_amd64.pyd` | 470.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/timestamps.pyi` | 7.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/timezones.cp313-win_amd64.lib` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/timezones.cp313-win_amd64.pyd` | 199.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/timezones.pyi` | 600 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/tzconversion.cp313-win_amd64.lib` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/tzconversion.cp313-win_amd64.pyd` | 223.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/tzconversion.pyi` | 560 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/vectorized.cp313-win_amd64.lib` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/vectorized.cp313-win_amd64.pyd` | 176.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/tslibs/vectorized.pyi` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/window/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/window/aggregations.cp313-win_amd64.lib` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/window/aggregations.cp313-win_amd64.pyd` | 314.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/window/aggregations.pyi` | 4.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/window/indexers.cp313-win_amd64.lib` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/window/indexers.cp313-win_amd64.pyd` | 150.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/window/indexers.pyi` | 319 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/writers.cp313-win_amd64.lib` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/writers.cp313-win_amd64.pyd` | 180.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_libs/writers.pyi` | 516 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_testing/__init__.py` | 17.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_testing/_hypothesis.py` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_testing/_io.py` | 4.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_testing/_warnings.py` | 8.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_testing/asserters.py` | 47.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_testing/compat.py` | 658 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_testing/contexts.py` | 6.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_typing.py` | 13.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_version.py` | 23.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/_version_meson.py` | 79 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/api/__init__.py` | 219 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/api/extensions/__init__.py` | 685 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/api/indexers/__init__.py` | 357 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/api/interchange/__init__.py` | 230 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/api/types/__init__.py` | 447 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/api/typing/__init__.py` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/arrays/__init__.py` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/compat/__init__.py` | 4.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/compat/_constants.py` | 617 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/compat/_optional.py` | 5.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/compat/compressors.py` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/compat/numpy/__init__.py` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/compat/numpy/function.py` | 13.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/compat/pickle_compat.py` | 7.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/compat/pyarrow.py` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/conftest.py` | 49.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/_numba/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/_numba/executor.py` | 7.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/_numba/extensions.py` | 18.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/_numba/kernels/__init__.py` | 520 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/_numba/kernels/mean_.py` | 5.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/_numba/kernels/min_max_.py` | 3.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/_numba/kernels/shared.py` | 611 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/_numba/kernels/sum_.py` | 6.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/_numba/kernels/var_.py` | 6.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/accessor.py` | 9.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/algorithms.py` | 53.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/api.py` | 2.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/apply.py` | 65.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/array_algos/__init__.py` | 408 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/array_algos/datetimelike_accumulations.py` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/array_algos/masked_accumulations.py` | 2.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/array_algos/masked_reductions.py` | 4.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/array_algos/putmask.py` | 4.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/array_algos/quantile.py` | 6.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/array_algos/replace.py` | 4.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/array_algos/take.py` | 20.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/array_algos/transforms.py` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/arraylike.py` | 17.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/arrays/__init__.py` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/arrays/_arrow_string_mixins.py` | 13.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/arrays/_mixins.py` | 17.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/arrays/_ranges.py` | 6.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/arrays/_utils.py` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/arrays/arrow/__init__.py` | 221 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/arrays/arrow/_arrow_utils.py` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/arrays/arrow/accessors.py` | 13.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/arrays/arrow/array.py` | 102.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/arrays/arrow/extension_types.py` | 5.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/arrays/base.py` | 83.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/arrays/boolean.py` | 12.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/arrays/categorical.py` | 98.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/arrays/datetimelike.py` | 88.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/arrays/datetimes.py` | 90.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/arrays/floating.py` | 4.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/arrays/integer.py` | 6.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/arrays/interval.py` | 62.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/arrays/masked.py` | 55.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/arrays/numeric.py` | 9.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/arrays/numpy_.py` | 17.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/arrays/period.py` | 40.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/arrays/sparse/__init__.py` | 356 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/arrays/sparse/accessor.py` | 12.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/arrays/sparse/array.py` | 63.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/arrays/sparse/scipy_sparse.py` | 6.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/arrays/string_.py` | 38.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/arrays/string_arrow.py` | 19.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/arrays/timedeltas.py` | 36.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/base.py` | 40.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/common.py` | 17.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/computation/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/computation/align.py` | 6.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/computation/api.py` | 65 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/computation/check.py` | 226 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/computation/common.py` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/computation/engines.py` | 3.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/computation/eval.py` | 13.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/computation/expr.py` | 24.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/computation/expressions.py` | 7.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/computation/ops.py` | 14.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/computation/parsing.py` | 6.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/computation/pytables.py` | 20.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/computation/scope.py` | 10.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/config_init.py` | 26.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/construction.py` | 25.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/dtypes/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/dtypes/api.py` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/dtypes/astype.py` | 9.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/dtypes/base.py` | 16.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/dtypes/cast.py` | 61.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/dtypes/common.py` | 46.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/dtypes/concat.py` | 12.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/dtypes/dtypes.py` | 74.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/dtypes/generic.py` | 4.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/dtypes/inference.py` | 8.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/dtypes/missing.py` | 23.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/flags.py` | 3.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/frame.py` | 437.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/generic.py` | 465.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/groupby/__init__.py` | 301 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/groupby/base.py` | 2.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/groupby/categorical.py` | 3.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/groupby/generic.py` | 94.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/groupby/groupby.py` | 192.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/groupby/grouper.py` | 37.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/groupby/indexing.py` | 9.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/groupby/numba_.py` | 4.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/groupby/ops.py` | 37.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/indexers/__init__.py` | 736 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/indexers/objects.py` | 14.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/indexers/utils.py` | 15.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/indexes/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/indexes/accessors.py` | 18.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/indexes/api.py` | 10.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/indexes/base.py` | 261.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/indexes/category.py` | 15.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/indexes/datetimelike.py` | 27.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/indexes/datetimes.py` | 37.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/indexes/extension.py` | 5.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/indexes/frozen.py` | 3.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/indexes/interval.py` | 37.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/indexes/multi.py` | 140.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/indexes/period.py` | 18.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/indexes/range.py` | 38.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/indexes/timedeltas.py` | 10.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/indexing.py` | 96.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/interchange/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/interchange/buffer.py` | 3.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/interchange/column.py` | 17.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/interchange/dataframe.py` | 3.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/interchange/dataframe_protocol.py` | 15.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/interchange/from_dataframe.py` | 17.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/interchange/utils.py` | 4.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/internals/__init__.py` | 2.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/internals/api.py` | 4.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/internals/array_manager.py` | 42.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/internals/base.py` | 10.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/internals/blocks.py` | 98.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/internals/concat.py` | 18.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/internals/construction.py` | 33.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/internals/managers.py` | 80.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/internals/ops.py` | 5.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/methods/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/methods/describe.py` | 11.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/methods/selectn.py` | 7.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/methods/to_dict.py` | 8.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/missing.py` | 34.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/nanops.py` | 49.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/ops/__init__.py` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/ops/array_ops.py` | 18.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/ops/common.py` | 3.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/ops/dispatch.py` | 635 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/ops/docstrings.py` | 18.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/ops/invalid.py` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/ops/mask_ops.py` | 5.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/ops/missing.py` | 5.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/resample.py` | 92.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/reshape/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/reshape/api.py` | 680 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/reshape/concat.py` | 27.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/reshape/encoding.py` | 18.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/reshape/melt.py` | 17.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/reshape/merge.py` | 97.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/reshape/pivot.py` | 28.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/reshape/reshape.py` | 33.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/reshape/tile.py` | 21.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/reshape/util.py` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/roperator.py` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/sample.py` | 4.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/series.py` | 208.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/shared_docs.py` | 29.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/sorting.py` | 22.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/sparse/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/sparse/api.py` | 143 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/strings/__init__.py` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/strings/accessor.py` | 111.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/strings/base.py` | 5.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/strings/object_array.py` | 16.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/tools/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/tools/datetimes.py` | 42.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/tools/numeric.py` | 10.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/tools/timedeltas.py` | 8.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/tools/times.py` | 5.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/util/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/util/hashing.py` | 9.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/util/numba_.py` | 2.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/window/__init__.py` | 450 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/window/common.py` | 6.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/window/doc.py` | 4.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/window/ewm.py` | 34.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/window/expanding.py` | 27.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/window/numba_.py` | 10.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/window/online.py` | 3.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/core/window/rolling.py` | 93.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/errors/__init__.py` | 26.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/__init__.py` | 293 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/_util.py` | 2.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/api.py` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/clipboard/__init__.py` | 23.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/clipboards.py` | 6.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/common.py` | 39.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/excel/__init__.py` | 486 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/excel/_base.py` | 57.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/excel/_calamine.py` | 3.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/excel/_odfreader.py` | 8.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/excel/_odswriter.py` | 10.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/excel/_openpyxl.py` | 19.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/excel/_pyxlsb.py` | 4.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/excel/_util.py` | 7.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/excel/_xlrd.py` | 4.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/excel/_xlsxwriter.py` | 9.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/feather_format.py` | 3.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/formats/__init__.py` | 238 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/formats/_color_data.py` | 4.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/formats/console.py` | 2.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/formats/css.py` | 12.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/formats/csvs.py` | 10.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/formats/excel.py` | 32.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/formats/format.py` | 64.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/formats/html.py` | 23.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/formats/info.py` | 31.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/formats/printing.py` | 17.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/formats/string.py` | 6.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/formats/style.py` | 152.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/formats/style_render.py` | 88.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/formats/templates/html.tpl` | 412 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/formats/templates/html_style.tpl` | 694 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/formats/templates/html_table.tpl` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/formats/templates/latex.tpl` | 127 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/formats/templates/latex_longtable.tpl` | 2.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/formats/templates/latex_table.tpl` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/formats/templates/string.tpl` | 344 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/formats/xml.py` | 15.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/gbq.py` | 9.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/html.py` | 38.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/json/__init__.py` | 270 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/json/_json.py` | 47.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/json/_normalize.py` | 16.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/json/_table_schema.py` | 11.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/orc.py` | 7.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/parquet.py` | 23.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/parsers/__init__.py` | 204 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/parsers/arrow_parser_wrapper.py` | 10.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/parsers/base_parser.py` | 48.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/parsers/c_parser_wrapper.py` | 13.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/parsers/python_parser.py` | 47.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/parsers/readers.py` | 85.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/pickle.py` | 6.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/pytables.py` | 177.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/sas/__init__.py` | 69 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/sas/sas7bdat.py` | 27.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/sas/sas_constants.py` | 8.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/sas/sas_xport.py` | 14.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/sas/sasreader.py` | 4.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/spss.py` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/sql.py` | 99.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/stata.py` | 132.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/io/xml.py` | 37.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/plotting/__init__.py` | 2.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/plotting/_core.py` | 65.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/plotting/_matplotlib/__init__.py` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/plotting/_matplotlib/boxplot.py` | 18.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/plotting/_matplotlib/converter.py` | 36.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/plotting/_matplotlib/core.py` | 70.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/plotting/_matplotlib/groupby.py` | 4.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/plotting/_matplotlib/hist.py` | 16.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/plotting/_matplotlib/misc.py` | 13.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/plotting/_matplotlib/style.py` | 8.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/plotting/_matplotlib/timeseries.py` | 11.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/plotting/_matplotlib/tools.py` | 15.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/plotting/_misc.py` | 20.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/pyproject.toml` | 24.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/testing.py` | 313 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/api/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/api/test_api.py` | 9.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/api/test_types.py` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/apply/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/apply/common.py` | 298 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/apply/test_frame_apply.py` | 53.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/apply/test_frame_apply_relabeling.py` | 3.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/apply/test_frame_transform.py` | 7.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/apply/test_invalid_arg.py` | 10.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/apply/test_numba.py` | 4.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/apply/test_series_apply.py` | 21.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/apply/test_series_apply_relabeling.py` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/apply/test_series_transform.py` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/apply/test_str.py` | 10.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arithmetic/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arithmetic/common.py` | 4.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arithmetic/conftest.py` | 3.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arithmetic/test_array_ops.py` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arithmetic/test_categorical.py` | 742 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arithmetic/test_datetime64.py` | 88.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arithmetic/test_interval.py` | 10.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arithmetic/test_numeric.py` | 54.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arithmetic/test_object.py` | 13.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arithmetic/test_period.py` | 58.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arithmetic/test_timedelta64.py` | 77.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/boolean/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/boolean/test_arithmetic.py` | 4.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/boolean/test_astype.py` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/boolean/test_comparison.py` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/boolean/test_construction.py` | 12.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/boolean/test_function.py` | 4.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/boolean/test_indexing.py` | 361 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/boolean/test_logical.py` | 9.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/boolean/test_ops.py` | 975 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/boolean/test_reduction.py` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/boolean/test_repr.py` | 437 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/categorical/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/categorical/test_algos.py` | 2.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/categorical/test_analytics.py` | 13.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/categorical/test_api.py` | 19.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/categorical/test_astype.py` | 5.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/categorical/test_constructors.py` | 30.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/categorical/test_dtypes.py` | 5.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/categorical/test_indexing.py` | 12.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/categorical/test_map.py` | 5.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/categorical/test_missing.py` | 7.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/categorical/test_operators.py` | 15.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/categorical/test_replace.py` | 4.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/categorical/test_repr.py` | 26.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/categorical/test_sorting.py` | 4.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/categorical/test_subclass.py` | 903 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/categorical/test_take.py` | 3.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/categorical/test_warnings.py` | 682 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/datetimes/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/datetimes/test_constructors.py` | 10.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/datetimes/test_cumulative.py` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/datetimes/test_reductions.py` | 5.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/floating/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/floating/conftest.py` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/floating/test_arithmetic.py` | 8.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/floating/test_astype.py` | 4.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/floating/test_comparison.py` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/floating/test_concat.py` | 573 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/floating/test_construction.py` | 6.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/floating/test_contains.py` | 204 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/floating/test_function.py` | 6.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/floating/test_repr.py` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/floating/test_to_numpy.py` | 4.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/integer/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/integer/conftest.py` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/integer/test_arithmetic.py` | 10.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/integer/test_comparison.py` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/integer/test_concat.py` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/integer/test_construction.py` | 7.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/integer/test_dtypes.py` | 8.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/integer/test_function.py` | 6.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/integer/test_indexing.py` | 498 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/integer/test_reduction.py` | 4.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/integer/test_repr.py` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/interval/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/interval/test_astype.py` | 776 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/interval/test_formats.py` | 317 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/interval/test_interval.py` | 7.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/interval/test_interval_pyarrow.py` | 5.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/interval/test_overlaps.py` | 3.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/masked/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/masked/test_arithmetic.py` | 8.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/masked/test_arrow_compat.py` | 7.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/masked/test_function.py` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/masked/test_indexing.py` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/masked_shared.py` | 5.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/numpy_/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/numpy_/test_indexing.py` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/numpy_/test_numpy.py` | 9.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/period/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/period/test_arrow_compat.py` | 3.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/period/test_astype.py` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/period/test_constructors.py` | 5.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/period/test_reductions.py` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/sparse/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/sparse/test_accessor.py` | 8.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/sparse/test_arithmetics.py` | 19.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/sparse/test_array.py` | 17.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/sparse/test_astype.py` | 4.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/sparse/test_combine_concat.py` | 2.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/sparse/test_constructors.py` | 10.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/sparse/test_dtype.py` | 6.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/sparse/test_indexing.py` | 10.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/sparse/test_libsparse.py` | 18.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/sparse/test_reductions.py` | 9.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/sparse/test_unary.py` | 2.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/string_/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/string_/test_concat.py` | 2.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/string_/test_string.py` | 30.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/string_/test_string_arrow.py` | 9.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/test_array.py` | 16.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/test_datetimelike.py` | 45.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/test_datetimes.py` | 28.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/test_ndarray_backed.py` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/test_period.py` | 5.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/test_timedeltas.py` | 10.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/timedeltas/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/timedeltas/test_constructors.py` | 4.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/timedeltas/test_cumulative.py` | 692 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/arrays/timedeltas/test_reductions.py` | 6.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/base/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/base/common.py` | 266 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/base/test_constructors.py` | 5.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/base/test_conversion.py` | 18.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/base/test_fillna.py` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/base/test_misc.py` | 5.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/base/test_transpose.py` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/base/test_unique.py` | 4.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/base/test_value_counts.py` | 11.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/computation/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/computation/test_compat.py` | 872 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/computation/test_eval.py` | 70.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/config/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/config/test_config.py` | 15.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/config/test_localization.py` | 4.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/construction/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/construction/test_extract_array.py` | 637 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/copy_view/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/copy_view/index/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/copy_view/index/test_datetimeindex.py` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/copy_view/index/test_index.py` | 5.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/copy_view/index/test_periodindex.py` | 653 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/copy_view/index/test_timedeltaindex.py` | 661 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/copy_view/test_array.py` | 6.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/copy_view/test_astype.py` | 9.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/copy_view/test_chained_assignment_deprecation.py` | 8.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/copy_view/test_clip.py` | 3.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/copy_view/test_constructors.py` | 13.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/copy_view/test_core_functionalities.py` | 3.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/copy_view/test_functions.py` | 15.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/copy_view/test_indexing.py` | 42.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/copy_view/test_internals.py` | 4.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/copy_view/test_interp_fillna.py` | 15.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/copy_view/test_methods.py` | 70.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/copy_view/test_replace.py` | 17.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/copy_view/test_setitem.py` | 4.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/copy_view/test_util.py` | 385 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/copy_view/util.py` | 899 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/dtypes/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/dtypes/cast/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/dtypes/cast/test_can_hold_element.py` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/dtypes/cast/test_construct_from_scalar.py` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/dtypes/cast/test_construct_ndarray.py` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/dtypes/cast/test_construct_object_arr.py` | 717 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/dtypes/cast/test_dict_compat.py` | 476 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/dtypes/cast/test_downcast.py` | 2.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/dtypes/cast/test_find_common_type.py` | 5.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/dtypes/cast/test_infer_datetimelike.py` | 603 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/dtypes/cast/test_infer_dtype.py` | 5.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/dtypes/cast/test_maybe_box_native.py` | 996 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/dtypes/cast/test_promote.py` | 20.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/dtypes/test_common.py` | 28.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/dtypes/test_concat.py` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/dtypes/test_dtypes.py` | 42.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/dtypes/test_generic.py` | 4.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/dtypes/test_inference.py` | 69.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/dtypes/test_missing.py` | 30.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/array_with_attr/__init__.py` | 149 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/array_with_attr/array.py` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/array_with_attr/test_array_with_attr.py` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/base/__init__.py` | 4.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/base/accumulate.py` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/base/base.py` | 35 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/base/casting.py` | 3.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/base/constructors.py` | 5.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/base/dim2.py` | 11.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/base/dtype.py` | 3.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/base/getitem.py` | 15.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/base/groupby.py` | 6.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/base/index.py` | 517 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/base/interface.py` | 5.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/base/io.py` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/base/methods.py` | 26.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/base/missing.py` | 6.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/base/ops.py` | 10.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/base/printing.py` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/base/reduce.py` | 5.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/base/reshaping.py` | 13.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/base/setitem.py` | 14.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/conftest.py` | 4.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/date/__init__.py` | 118 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/date/array.py` | 5.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/decimal/__init__.py` | 191 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/decimal/array.py` | 9.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/decimal/test_decimal.py` | 19.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/json/__init__.py` | 146 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/json/array.py` | 8.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/json/test_json.py` | 17.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/list/__init__.py` | 146 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/list/array.py` | 3.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/list/test_list.py` | 671 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/test_arrow.py` | 115.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/test_categorical.py` | 6.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/test_common.py` | 2.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/test_datetime.py` | 4.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/test_extension.py` | 559 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/test_interval.py` | 3.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/test_masked.py` | 14.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/test_numpy.py` | 15.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/test_period.py` | 3.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/test_sparse.py` | 17.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/extension/test_string.py` | 9.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/common.py` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/conftest.py` | 2.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/constructors/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/constructors/test_from_dict.py` | 7.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/constructors/test_from_records.py` | 18.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/indexing/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/indexing/test_coercion.py` | 6.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/indexing/test_delitem.py` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/indexing/test_get.py` | 662 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/indexing/test_get_value.py` | 679 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/indexing/test_getitem.py` | 14.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/indexing/test_indexing.py` | 69.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/indexing/test_insert.py` | 4.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/indexing/test_mask.py` | 4.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/indexing/test_set_value.py` | 2.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/indexing/test_setitem.py` | 54.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/indexing/test_take.py` | 3.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/indexing/test_where.py` | 37.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/indexing/test_xs.py` | 15.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/__init__.py` | 229 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_add_prefix_suffix.py` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_align.py` | 17.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_asfreq.py` | 9.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_asof.py` | 6.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_assign.py` | 2.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_astype.py` | 31.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_at_time.py` | 4.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_between_time.py` | 7.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_clip.py` | 7.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_combine.py` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_combine_first.py` | 19.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_compare.py` | 9.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_convert_dtypes.py` | 7.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_copy.py` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_count.py` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_cov_corr.py` | 17.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_describe.py` | 14.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_diff.py` | 9.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_dot.py` | 4.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_drop.py` | 19.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_drop_duplicates.py` | 14.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_droplevel.py` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_dropna.py` | 10.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_dtypes.py` | 4.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_duplicated.py` | 3.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_equals.py` | 2.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_explode.py` | 8.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_fillna.py` | 32.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_filter.py` | 5.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_first_and_last.py` | 5.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_first_valid_index.py` | 2.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_get_numeric_data.py` | 3.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_head_tail.py` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_infer_objects.py` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_info.py` | 17.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_interpolate.py` | 19.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_is_homogeneous_dtype.py` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_isetitem.py` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_isin.py` | 7.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_iterrows.py` | 338 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_join.py` | 17.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_map.py` | 5.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_matmul.py` | 3.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_nlargest.py` | 8.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_pct_change.py` | 6.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_pipe.py` | 1023 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_pop.py` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_quantile.py` | 35.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_rank.py` | 17.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_reindex.py` | 47.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_reindex_like.py` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_rename.py` | 15.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_rename_axis.py` | 4.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_reorder_levels.py` | 2.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_replace.py` | 61.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_reset_index.py` | 28.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_round.py` | 7.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_sample.py` | 13.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_select_dtypes.py` | 17.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_set_axis.py` | 4.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_set_index.py` | 25.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_shift.py` | 27.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_size.py` | 571 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_sort_index.py` | 34.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_sort_values.py` | 32.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_swapaxes.py` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_swaplevel.py` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_to_csv.py` | 50.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_to_dict.py` | 18.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_to_dict_of_blocks.py` | 2.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_to_numpy.py` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_to_period.py` | 2.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_to_records.py` | 18.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_to_timestamp.py` | 5.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_transpose.py` | 6.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_truncate.py` | 5.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_tz_convert.py` | 4.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_tz_localize.py` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_update.py` | 6.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_value_counts.py` | 5.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/methods/test_values.py` | 9.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/test_alter_axes.py` | 873 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/test_api.py` | 12.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/test_arithmetic.py` | 71.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/test_arrow_interface.py` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/test_block_internals.py` | 15.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/test_constructors.py` | 121.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/test_cumulative.py` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/test_iteration.py` | 5.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/test_logical_ops.py` | 7.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/test_nonunique_indexes.py` | 11.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/test_npfuncs.py` | 2.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/test_query_eval.py` | 54.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/test_reductions.py` | 74.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/test_repr.py` | 16.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/test_stack_unstack.py` | 95.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/test_subclass.py` | 27.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/test_ufunc.py` | 10.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/test_unary.py` | 6.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/frame/test_validate.py` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/generic/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/generic/test_duplicate_labels.py` | 14.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/generic/test_finalize.py` | 28.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/generic/test_frame.py` | 7.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/generic/test_generic.py` | 17.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/generic/test_label_or_level_utils.py` | 10.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/generic/test_series.py` | 5.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/generic/test_to_xarray.py` | 4.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/__init__.py` | 659 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/aggregate/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/aggregate/test_aggregate.py` | 54.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/aggregate/test_cython.py` | 12.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/aggregate/test_numba.py` | 13.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/aggregate/test_other.py` | 20.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/conftest.py` | 4.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/methods/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/methods/test_corrwith.py` | 615 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/methods/test_describe.py` | 9.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/methods/test_groupby_shift_diff.py` | 7.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/methods/test_is_monotonic.py` | 2.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/methods/test_nlargest_nsmallest.py` | 3.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/methods/test_nth.py` | 27.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/methods/test_quantile.py` | 16.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/methods/test_rank.py` | 23.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/methods/test_sample.py` | 5.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/methods/test_size.py` | 4.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/methods/test_skew.py` | 841 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/methods/test_value_counts.py` | 39.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/test_all_methods.py` | 3.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/test_api.py` | 8.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/test_apply.py` | 53.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/test_apply_mutate.py` | 4.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/test_bin_groupby.py` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/test_categorical.py` | 73.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/test_counting.py` | 13.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/test_cumulative.py` | 10.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/test_filters.py` | 21.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/test_groupby.py` | 106.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/test_groupby_dropna.py` | 23.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/test_groupby_subclass.py` | 4.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/test_grouping.py` | 44.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/test_index_as_string.py` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/test_indexing.py` | 9.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/test_libgroupby.py` | 10.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/test_missing.py` | 5.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/test_numba.py` | 3.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/test_numeric_only.py` | 18.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/test_pipe.py` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/test_raises.py` | 23.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/test_reductions.py` | 39.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/test_timegrouper.py` | 34.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/transform/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/transform/test_numba.py` | 9.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/groupby/transform/test_transform.py` | 56.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/base_class/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/base_class/test_constructors.py` | 2.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/base_class/test_formats.py` | 6.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/base_class/test_indexing.py` | 3.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/base_class/test_pickle.py` | 309 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/base_class/test_reshape.py` | 3.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/base_class/test_setops.py` | 8.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/base_class/test_where.py` | 341 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/categorical/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/categorical/test_append.py` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/categorical/test_astype.py` | 2.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/categorical/test_category.py` | 14.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/categorical/test_constructors.py` | 5.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/categorical/test_equals.py` | 3.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/categorical/test_fillna.py` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/categorical/test_formats.py` | 6.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/categorical/test_indexing.py` | 14.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/categorical/test_map.py` | 4.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/categorical/test_reindex.py` | 2.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/categorical/test_setops.py` | 462 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/conftest.py` | 987 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimelike_/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimelike_/test_drop_duplicates.py` | 2.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimelike_/test_equals.py` | 6.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimelike_/test_indexing.py` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimelike_/test_is_monotonic.py` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimelike_/test_nat.py` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimelike_/test_sort_values.py` | 11.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimelike_/test_value_counts.py` | 3.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/methods/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/methods/test_asof.py` | 738 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/methods/test_astype.py` | 12.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/methods/test_delete.py` | 4.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/methods/test_factorize.py` | 4.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/methods/test_fillna.py` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/methods/test_insert.py` | 9.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/methods/test_isocalendar.py` | 908 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/methods/test_map.py` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/methods/test_normalize.py` | 3.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/methods/test_repeat.py` | 2.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/methods/test_resolution.py` | 785 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/methods/test_round.py` | 7.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/methods/test_shift.py` | 5.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/methods/test_snap.py` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/methods/test_to_frame.py` | 998 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/methods/test_to_julian_date.py` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/methods/test_to_period.py` | 7.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/methods/test_to_pydatetime.py` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/methods/test_to_series.py` | 493 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/methods/test_tz_convert.py` | 11.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/methods/test_tz_localize.py` | 14.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/methods/test_unique.py` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/test_arithmetic.py` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/test_constructors.py` | 42.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/test_date_range.py` | 59.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/test_datetime.py` | 7.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/test_formats.py` | 12.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/test_freq_attr.py` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/test_indexing.py` | 24.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/test_iter.py` | 2.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/test_join.py` | 4.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/test_npfuncs.py` | 384 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/test_ops.py` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/test_partial_slicing.py` | 16.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/test_pickle.py` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/test_reindex.py` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/test_scalar_compat.py` | 10.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/test_setops.py` | 23.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/datetimes/test_timezones.py` | 7.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/interval/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/interval/test_astype.py` | 8.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/interval/test_constructors.py` | 19.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/interval/test_equals.py` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/interval/test_formats.py` | 3.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/interval/test_indexing.py` | 24.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/interval/test_interval.py` | 33.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/interval/test_interval_range.py` | 13.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/interval/test_interval_tree.py` | 7.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/interval/test_join.py` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/interval/test_pickle.py` | 435 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/interval/test_setops.py` | 8.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/multi/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/multi/conftest.py` | 698 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/multi/test_analytics.py` | 6.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/multi/test_astype.py` | 924 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/multi/test_compat.py` | 3.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/multi/test_constructors.py` | 26.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/multi/test_conversion.py` | 6.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/multi/test_copy.py` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/multi/test_drop.py` | 5.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/multi/test_duplicates.py` | 11.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/multi/test_equivalence.py` | 8.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/multi/test_formats.py` | 9.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/multi/test_get_level_values.py` | 3.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/multi/test_get_set.py` | 12.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/multi/test_indexing.py` | 35.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/multi/test_integrity.py` | 8.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/multi/test_isin.py` | 3.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/multi/test_join.py` | 8.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/multi/test_lexsort.py` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/multi/test_missing.py` | 3.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/multi/test_monotonic.py` | 6.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/multi/test_names.py` | 6.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/multi/test_partial_indexing.py` | 4.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/multi/test_pickle.py` | 259 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/multi/test_reindex.py` | 5.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/multi/test_reshape.py` | 6.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/multi/test_setops.py` | 24.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/multi/test_sorting.py` | 10.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/multi/test_take.py` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/numeric/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/numeric/test_astype.py` | 3.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/numeric/test_indexing.py` | 22.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/numeric/test_join.py` | 14.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/numeric/test_numeric.py` | 18.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/numeric/test_setops.py` | 5.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/object/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/object/test_astype.py` | 368 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/object/test_indexing.py` | 6.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/period/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/period/methods/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/period/methods/test_asfreq.py` | 6.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/period/methods/test_astype.py` | 5.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/period/methods/test_factorize.py` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/period/methods/test_fillna.py` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/period/methods/test_insert.py` | 482 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/period/methods/test_is_full.py` | 570 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/period/methods/test_repeat.py` | 772 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/period/methods/test_shift.py` | 4.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/period/methods/test_to_timestamp.py` | 4.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/period/test_constructors.py` | 26.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/period/test_formats.py` | 12.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/period/test_freq_attr.py` | 646 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/period/test_indexing.py` | 27.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/period/test_join.py` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/period/test_monotonic.py` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/period/test_partial_slicing.py` | 7.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/period/test_period.py` | 7.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/period/test_period_range.py` | 8.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/period/test_pickle.py` | 692 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/period/test_resolution.py` | 571 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/period/test_scalar_compat.py` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/period/test_searchsorted.py` | 2.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/period/test_setops.py` | 12.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/period/test_tools.py` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/ranges/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/ranges/test_constructors.py` | 5.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/ranges/test_indexing.py` | 5.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/ranges/test_join.py` | 6.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/ranges/test_range.py` | 20.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/ranges/test_setops.py` | 17.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/string/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/string/test_astype.py` | 722 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/string/test_indexing.py` | 7.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/test_any_index.py` | 5.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/test_base.py` | 59.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/test_common.py` | 17.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/test_datetimelike.py` | 5.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/test_engines.py` | 6.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/test_frozen.py` | 3.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/test_index_new.py` | 14.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/test_indexing.py` | 11.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/test_numpy_compat.py` | 5.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/test_old_base.py` | 39.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/test_setops.py` | 32.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/test_subclass.py` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/timedeltas/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/timedeltas/methods/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/timedeltas/methods/test_astype.py` | 6.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/timedeltas/methods/test_factorize.py` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/timedeltas/methods/test_fillna.py` | 597 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/timedeltas/methods/test_insert.py` | 4.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/timedeltas/methods/test_repeat.py` | 926 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/timedeltas/methods/test_shift.py` | 2.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/timedeltas/test_arithmetic.py` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/timedeltas/test_constructors.py` | 10.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/timedeltas/test_delete.py` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/timedeltas/test_formats.py` | 3.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/timedeltas/test_freq_attr.py` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/timedeltas/test_indexing.py` | 11.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/timedeltas/test_join.py` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/timedeltas/test_ops.py` | 393 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/timedeltas/test_pickle.py` | 302 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/timedeltas/test_scalar_compat.py` | 4.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/timedeltas/test_searchsorted.py` | 967 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/timedeltas/test_setops.py` | 9.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/timedeltas/test_timedelta.py` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexes/timedeltas/test_timedelta_range.py` | 6.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexing/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexing/common.py` | 1021 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexing/conftest.py` | 2.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexing/interval/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexing/interval/test_interval.py` | 7.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexing/interval/test_interval_new.py` | 7.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexing/multiindex/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexing/multiindex/test_chaining_and_caching.py` | 2.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexing/multiindex/test_datetime.py` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexing/multiindex/test_getitem.py` | 12.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexing/multiindex/test_iloc.py` | 4.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexing/multiindex/test_indexing_slow.py` | 3.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexing/multiindex/test_loc.py` | 32.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexing/multiindex/test_multiindex.py` | 7.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexing/multiindex/test_partial.py` | 8.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexing/multiindex/test_setitem.py` | 19.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexing/multiindex/test_slice.py` | 26.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexing/multiindex/test_sorted.py` | 5.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexing/test_at.py` | 7.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexing/test_categorical.py` | 19.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexing/test_chaining_and_caching.py` | 22.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexing/test_check_indexer.py` | 3.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexing/test_coercion.py` | 31.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexing/test_datetime.py` | 5.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexing/test_floats.py` | 20.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexing/test_iat.py` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexing/test_iloc.py` | 52.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexing/test_indexers.py` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexing/test_indexing.py` | 39.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexing/test_loc.py` | 118.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexing/test_na_indexing.py` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexing/test_partial.py` | 24.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/indexing/test_scalar.py` | 9.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/interchange/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/interchange/test_impl.py` | 19.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/interchange/test_spec_conformance.py` | 5.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/interchange/test_utils.py` | 2.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/internals/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/internals/test_api.py` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/internals/test_internals.py` | 48.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/internals/test_managers.py` | 3.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/conftest.py` | 5.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/excel/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/excel/test_odf.py` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/excel/test_odswriter.py` | 3.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/excel/test_openpyxl.py` | 14.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/excel/test_readers.py` | 61.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/excel/test_style.py` | 11.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/excel/test_writers.py` | 53.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/excel/test_xlrd.py` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/excel/test_xlsxwriter.py` | 2.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/formats/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/formats/style/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/formats/style/test_bar.py` | 11.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/formats/style/test_exceptions.py` | 1002 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/formats/style/test_format.py` | 20.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/formats/style/test_highlight.py` | 6.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/formats/style/test_html.py` | 31.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/formats/style/test_matplotlib.py` | 11.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/formats/style/test_non_unique.py` | 4.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/formats/style/test_style.py` | 56.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/formats/style/test_to_latex.py` | 32.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/formats/style/test_to_string.py` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/formats/style/test_tooltip.py` | 2.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/formats/test_console.py` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/formats/test_css.py` | 8.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/formats/test_eng_formatting.py` | 8.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/formats/test_format.py` | 81.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/formats/test_ipython_compat.py` | 3.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/formats/test_printing.py` | 4.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/formats/test_to_csv.py` | 26.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/formats/test_to_excel.py` | 15.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/formats/test_to_html.py` | 37.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/formats/test_to_latex.py` | 40.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/formats/test_to_markdown.py` | 2.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/formats/test_to_string.py` | 38.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/generate_legacy_storage_files.py` | 10.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/json/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/json/conftest.py` | 205 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/json/test_compression.py` | 4.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/json/test_deprecated_kwargs.py` | 690 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/json/test_json_table_schema.py` | 30.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/json/test_json_table_schema_ext_dtype.py` | 9.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/json/test_normalize.py` | 30.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/json/test_pandas.py` | 75.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/json/test_readlines.py` | 18.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/json/test_ujson.py` | 35.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/common/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/common/test_chunksize.py` | 11.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/common/test_common_basic.py` | 30.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/common/test_data_list.py` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/common/test_decimal.py` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/common/test_file_buffer_url.py` | 13.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/common/test_float.py` | 2.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/common/test_index.py` | 8.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/common/test_inf.py` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/common/test_ints.py` | 7.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/common/test_iterator.py` | 3.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/common/test_read_errors.py` | 9.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/common/test_verbose.py` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/conftest.py` | 8.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/dtypes/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/dtypes/test_categorical.py` | 9.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/dtypes/test_dtypes_basic.py` | 18.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/dtypes/test_empty.py` | 5.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/test_c_parser_only.py` | 20.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/test_comment.py` | 7.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/test_compression.py` | 6.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/test_concatenate_chunks.py` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/test_converters.py` | 7.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/test_dialect.py` | 5.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/test_encoding.py` | 10.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/test_header.py` | 20.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/test_index_col.py` | 11.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/test_mangle_dupes.py` | 5.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/test_multi_thread.py` | 4.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/test_na_values.py` | 21.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/test_network.py` | 12.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/test_parse_dates.py` | 68.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/test_python_parser_only.py` | 15.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/test_quoting.py` | 6.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/test_read_fwf.py` | 29.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/test_skiprows.py` | 9.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/test_textreader.py` | 10.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/test_unsupported.py` | 7.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/test_upcast.py` | 3.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/usecols/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/usecols/test_parse_dates.py` | 5.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/usecols/test_strings.py` | 2.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/parser/usecols/test_usecols_basic.py` | 17.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/pytables/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/pytables/common.py` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/pytables/conftest.py` | 136 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/pytables/test_append.py` | 36.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/pytables/test_categorical.py` | 6.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/pytables/test_compat.py` | 2.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/pytables/test_complex.py` | 5.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/pytables/test_errors.py` | 8.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/pytables/test_file_handling.py` | 15.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/pytables/test_keys.py` | 2.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/pytables/test_put.py` | 13.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/pytables/test_pytables_missing.py` | 345 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/pytables/test_read.py` | 13.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/pytables/test_retain_attributes.py` | 2.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/pytables/test_round_trip.py` | 18.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/pytables/test_select.py` | 36.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/pytables/test_store.py` | 36.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/pytables/test_subclass.py` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/pytables/test_time_series.py` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/pytables/test_timezones.py` | 11.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/sas/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/sas/test_byteswap.py` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/sas/test_sas.py` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/sas/test_sas7bdat.py` | 14.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/sas/test_xport.py` | 5.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/test_clipboard.py` | 12.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/test_common.py` | 23.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/test_compression.py` | 12.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/test_feather.py` | 10.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/test_fsspec.py` | 10.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/test_gbq.py` | 401 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/test_gcs.py` | 7.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/test_html.py` | 55.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/test_http_headers.py` | 4.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/test_orc.py` | 13.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/test_parquet.py` | 51.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/test_pickle.py` | 20.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/test_s3.py` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/test_spss.py` | 6.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/test_sql.py` | 141.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/test_stata.py` | 90.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/xml/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/xml/conftest.py` | 850 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/xml/test_to_xml.py` | 34.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/xml/test_xml.py` | 59.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/io/xml/test_xml_dtypes.py` | 13.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/libs/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/libs/test_hashtable.py` | 25.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/libs/test_join.py` | 10.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/libs/test_lib.py` | 10.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/libs/test_libalgos.py` | 5.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/plotting/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/plotting/common.py` | 16.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/plotting/conftest.py` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/plotting/frame/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/plotting/frame/test_frame.py` | 97.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/plotting/frame/test_frame_color.py` | 27.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/plotting/frame/test_frame_groupby.py` | 2.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/plotting/frame/test_frame_legend.py` | 10.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/plotting/frame/test_frame_subplots.py` | 28.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/plotting/frame/test_hist_box_by.py` | 10.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/plotting/test_backend.py` | 3.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/plotting/test_boxplot_method.py` | 29.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/plotting/test_common.py` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/plotting/test_converter.py` | 12.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/plotting/test_datetimelike.py` | 65.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/plotting/test_groupby.py` | 5.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/plotting/test_hist_method.py` | 34.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/plotting/test_misc.py` | 24.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/plotting/test_series.py` | 34.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/plotting/test_style.py` | 5.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/reductions/__init__.py` | 125 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/reductions/test_reductions.py` | 57.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/reductions/test_stat_reductions.py` | 9.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/resample/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/resample/conftest.py` | 3.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/resample/test_base.py` | 13.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/resample/test_datetime_index.py` | 72.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/resample/test_period_index.py` | 40.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/resample/test_resample_api.py` | 33.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/resample/test_resampler_grouper.py` | 23.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/resample/test_time_grouper.py` | 11.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/resample/test_timedelta.py` | 7.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/reshape/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/reshape/concat/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/reshape/concat/conftest.py` | 162 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/reshape/concat/test_append.py` | 14.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/reshape/concat/test_append_common.py` | 27.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/reshape/concat/test_categorical.py` | 9.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/reshape/concat/test_concat.py` | 31.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/reshape/concat/test_dataframe.py` | 8.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/reshape/concat/test_datetimes.py` | 21.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/reshape/concat/test_empty.py` | 10.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/reshape/concat/test_index.py` | 17.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/reshape/concat/test_invalid.py` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/reshape/concat/test_series.py` | 5.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/reshape/concat/test_sort.py` | 4.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/reshape/merge/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/reshape/merge/test_join.py` | 37.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/reshape/merge/test_merge.py` | 103.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/reshape/merge/test_merge_asof.py` | 118.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/reshape/merge/test_merge_cross.py` | 3.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/reshape/merge/test_merge_index_as_string.py` | 5.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/reshape/merge/test_merge_ordered.py` | 7.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/reshape/merge/test_multi.py` | 30.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/reshape/test_crosstab.py` | 31.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/reshape/test_cut.py` | 24.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/reshape/test_from_dummies.py` | 13.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/reshape/test_get_dummies.py` | 27.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/reshape/test_melt.py` | 41.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/reshape/test_pivot.py` | 91.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/reshape/test_pivot_multilevel.py` | 7.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/reshape/test_qcut.py` | 8.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/reshape/test_union_categoricals.py` | 14.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/reshape/test_util.py` | 2.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/interval/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/interval/test_arithmetic.py` | 5.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/interval/test_constructors.py` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/interval/test_contains.py` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/interval/test_formats.py` | 344 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/interval/test_interval.py` | 2.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/interval/test_overlaps.py` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/period/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/period/test_arithmetic.py` | 16.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/period/test_asfreq.py` | 37.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/period/test_period.py` | 39.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/test_na_scalar.py` | 7.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/test_nat.py` | 19.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/timedelta/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/timedelta/methods/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/timedelta/methods/test_as_unit.py` | 2.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/timedelta/methods/test_round.py` | 6.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/timedelta/test_arithmetic.py` | 37.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/timedelta/test_constructors.py` | 21.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/timedelta/test_formats.py` | 4.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/timedelta/test_timedelta.py` | 22.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/timestamp/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/timestamp/methods/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/timestamp/methods/test_as_unit.py` | 2.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/timestamp/methods/test_normalize.py` | 831 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/timestamp/methods/test_replace.py` | 6.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/timestamp/methods/test_round.py` | 12.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/timestamp/methods/test_timestamp_method.py` | 1017 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/timestamp/methods/test_to_julian_date.py` | 810 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/timestamp/methods/test_to_pydatetime.py` | 2.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/timestamp/methods/test_tz_convert.py` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/timestamp/methods/test_tz_localize.py` | 12.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/timestamp/test_arithmetic.py` | 10.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/timestamp/test_comparisons.py` | 9.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/timestamp/test_constructors.py` | 38.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/timestamp/test_formats.py` | 6.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/timestamp/test_timestamp.py` | 30.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/scalar/timestamp/test_timezones.py` | 666 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/accessors/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/accessors/test_cat_accessor.py` | 9.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/accessors/test_dt_accessor.py` | 29.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/accessors/test_list_accessor.py` | 3.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/accessors/test_sparse_accessor.py` | 296 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/accessors/test_str_accessor.py` | 853 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/accessors/test_struct_accessor.py` | 5.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/indexing/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/indexing/test_datetime.py` | 14.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/indexing/test_delitem.py` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/indexing/test_get.py` | 5.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/indexing/test_getitem.py` | 23.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/indexing/test_indexing.py` | 16.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/indexing/test_mask.py` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/indexing/test_set_value.py` | 991 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/indexing/test_setitem.py` | 58.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/indexing/test_take.py` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/indexing/test_where.py` | 13.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/indexing/test_xs.py` | 2.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/__init__.py` | 225 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_add_prefix_suffix.py` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_align.py` | 8.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_argsort.py` | 2.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_asof.py` | 6.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_astype.py` | 25.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_autocorr.py` | 1015 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_between.py` | 2.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_case_when.py` | 4.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_clip.py` | 5.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_combine.py` | 627 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_combine_first.py` | 5.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_compare.py` | 4.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_convert_dtypes.py` | 9.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_copy.py` | 3.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_count.py` | 938 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_cov_corr.py` | 5.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_describe.py` | 6.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_diff.py` | 2.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_drop.py` | 3.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_drop_duplicates.py` | 9.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_dropna.py` | 3.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_dtypes.py` | 209 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_duplicated.py` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_equals.py` | 4.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_explode.py` | 5.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_fillna.py` | 39.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_get_numeric_data.py` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_head_tail.py` | 343 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_infer_objects.py` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_info.py` | 5.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_interpolate.py` | 33.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_is_monotonic.py` | 838 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_is_unique.py` | 953 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_isin.py` | 8.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_isna.py` | 940 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_item.py` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_map.py` | 18.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_matmul.py` | 2.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_nlargest.py` | 8.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_nunique.py` | 481 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_pct_change.py` | 4.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_pop.py` | 295 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_quantile.py` | 8.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_rank.py` | 19.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_reindex.py` | 14.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_reindex_like.py` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_rename.py` | 6.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_rename_axis.py` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_repeat.py` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_replace.py` | 31.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_reset_index.py` | 7.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_round.py` | 2.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_searchsorted.py` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_set_name.py` | 595 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_size.py` | 566 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_sort_index.py` | 12.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_sort_values.py` | 9.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_to_csv.py` | 6.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_to_dict.py` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_to_frame.py` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_to_numpy.py` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_tolist.py` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_truncate.py` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_tz_localize.py` | 4.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_unique.py` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_unstack.py` | 5.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_update.py` | 5.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_value_counts.py` | 9.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_values.py` | 747 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/methods/test_view.py` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/test_api.py` | 10.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/test_arithmetic.py` | 32.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/test_constructors.py` | 83.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/test_cumulative.py` | 7.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/test_formats.py` | 16.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/test_iteration.py` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/test_logical_ops.py` | 20.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/test_missing.py` | 3.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/test_npfuncs.py` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/test_reductions.py` | 6.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/test_subclass.py` | 2.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/test_ufunc.py` | 14.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/test_unary.py` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/series/test_validate.py` | 668 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/strings/__init__.py` | 587 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/strings/conftest.py` | 3.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/strings/test_api.py` | 6.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/strings/test_case_justify.py` | 13.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/strings/test_cat.py` | 13.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/strings/test_extract.py` | 25.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/strings/test_find_replace.py` | 45.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/strings/test_get_dummies.py` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/strings/test_split_partition.py` | 22.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/strings/test_string_array.py` | 3.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/strings/test_strings.py` | 29.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/test_aggregation.py` | 2.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/test_algos.py` | 76.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/test_common.py` | 7.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/test_downstream.py` | 10.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/test_errors.py` | 2.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/test_expressions.py` | 13.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/test_flags.py` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/test_multilevel.py` | 11.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/test_nanops.py` | 41.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/test_optional_dependency.py` | 3.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/test_register_accessor.py` | 2.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/test_sorting.py` | 16.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/test_take.py` | 11.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tools/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tools/test_to_datetime.py` | 144.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tools/test_to_numeric.py` | 28.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tools/test_to_time.py` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tools/test_to_timedelta.py` | 12.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tseries/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tseries/frequencies/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tseries/frequencies/test_freq_code.py` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tseries/frequencies/test_frequencies.py` | 821 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tseries/frequencies/test_inference.py` | 14.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tseries/holiday/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tseries/holiday/test_calendar.py` | 3.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tseries/holiday/test_federal.py` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tseries/holiday/test_holiday.py` | 10.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tseries/holiday/test_observance.py` | 2.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tseries/offsets/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tseries/offsets/common.py` | 900 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tseries/offsets/test_business_day.py` | 6.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tseries/offsets/test_business_hour.py` | 57.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tseries/offsets/test_business_month.py` | 6.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tseries/offsets/test_business_quarter.py` | 12.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tseries/offsets/test_business_year.py` | 6.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tseries/offsets/test_common.py` | 7.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tseries/offsets/test_custom_business_day.py` | 3.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tseries/offsets/test_custom_business_hour.py` | 12.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tseries/offsets/test_custom_business_month.py` | 13.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tseries/offsets/test_dst.py` | 8.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tseries/offsets/test_easter.py` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tseries/offsets/test_fiscal.py` | 26.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tseries/offsets/test_index.py` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tseries/offsets/test_month.py` | 22.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tseries/offsets/test_offsets.py` | 39.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tseries/offsets/test_offsets_properties.py` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tseries/offsets/test_quarter.py` | 11.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tseries/offsets/test_ticks.py` | 11.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tseries/offsets/test_week.py` | 12.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tseries/offsets/test_year.py` | 10.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tslibs/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tslibs/test_api.py` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tslibs/test_array_to_datetime.py` | 11.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tslibs/test_ccalendar.py` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tslibs/test_conversion.py` | 4.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tslibs/test_fields.py` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tslibs/test_libfrequencies.py` | 717 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tslibs/test_liboffsets.py` | 5.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tslibs/test_np_datetime.py` | 7.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tslibs/test_npy_units.py` | 922 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tslibs/test_parse_iso8601.py` | 4.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tslibs/test_parsing.py` | 13.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tslibs/test_period.py` | 3.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tslibs/test_resolution.py` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tslibs/test_strptime.py` | 3.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tslibs/test_timedeltas.py` | 4.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tslibs/test_timezones.py` | 4.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tslibs/test_to_offset.py` | 5.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/tslibs/test_tzconversion.py` | 953 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/util/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/util/conftest.py` | 476 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/util/test_assert_almost_equal.py` | 16.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/util/test_assert_attr_equal.py` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/util/test_assert_categorical_equal.py` | 2.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/util/test_assert_extension_array_equal.py` | 3.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/util/test_assert_frame_equal.py` | 13.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/util/test_assert_index_equal.py` | 9.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/util/test_assert_interval_array_equal.py` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/util/test_assert_numpy_array_equal.py` | 6.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/util/test_assert_produces_warning.py` | 8.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/util/test_assert_series_equal.py` | 14.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/util/test_deprecate.py` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/util/test_deprecate_kwarg.py` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/util/test_deprecate_nonkeyword_arguments.py` | 3.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/util/test_doc.py` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/util/test_hashing.py` | 13.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/util/test_numba.py` | 308 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/util/test_rewrite_warning.py` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/util/test_shares_memory.py` | 852 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/util/test_show_versions.py` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/util/test_util.py` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/util/test_validate_args.py` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/util/test_validate_args_and_kwargs.py` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/util/test_validate_inclusive.py` | 896 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/util/test_validate_kwargs.py` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/window/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/window/conftest.py` | 3.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/window/moments/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/window/moments/conftest.py` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/window/moments/test_moments_consistency_ewm.py` | 7.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/window/moments/test_moments_consistency_expanding.py` | 5.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/window/moments/test_moments_consistency_rolling.py` | 7.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/window/test_api.py` | 12.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/window/test_apply.py` | 9.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/window/test_base_indexer.py` | 15.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/window/test_cython_aggregations.py` | 3.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/window/test_dtypes.py` | 5.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/window/test_ewm.py` | 22.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/window/test_expanding.py` | 23.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/window/test_groupby.py` | 45.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/window/test_numba.py` | 16.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/window/test_online.py` | 3.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/window/test_pairwise.py` | 15.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/window/test_rolling.py` | 59.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/window/test_rolling_functions.py` | 17.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/window/test_rolling_quantile.py` | 5.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/window/test_rolling_skew_kurt.py` | 7.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/window/test_timeseries_window.py` | 23.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tests/window/test_win_type.py` | 17.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tseries/__init__.py` | 293 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tseries/api.py` | 234 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tseries/frequencies.py` | 17.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tseries/holiday.py` | 18.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/tseries/offsets.py` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/util/__init__.py` | 827 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/util/_decorators.py` | 16.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/util/_doctools.py` | 6.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/util/_exceptions.py` | 2.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/util/_print_versions.py` | 4.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/util/_test_decorators.py` | 5.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/util/_tester.py` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/util/_validators.py` | 14.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas/util/version/__init__.py` | 16.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas-2.3.3.dist-info/DELVEWHEEL` | 399 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas-2.3.3.dist-info/entry_points.txt` | 69 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas-2.3.3.dist-info/INSTALLER` | 4 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas-2.3.3.dist-info/LICENSE` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas-2.3.3.dist-info/METADATA` | 19.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas-2.3.3.dist-info/RECORD` | 242.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pandas-2.3.3.dist-info/REQUESTED` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas-2.3.3.dist-info/WHEEL` | 85 B |
| `.venv_c_mirror_backup/Lib/site-packages/pandas.libs/msvcp140-a4c2229bdc2a2a630acdc095b4d86008.dll` | 561.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/__init__.py` | 355 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/__main__.py` | 874 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/__pip-runner__.py` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/__init__.py` | 511 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/build_env.py` | 21.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/cache.py` | 10.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/cli/__init__.py` | 131 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/cli/autocompletion.py` | 7.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/cli/base_command.py` | 9.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/cli/cmdoptions.py` | 36.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/cli/command_context.py` | 817 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/cli/index_command.py` | 6.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/cli/main.py` | 3.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/cli/main_parser.py` | 4.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/cli/parser.py` | 13.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/cli/progress_bars.py` | 4.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/cli/req_command.py` | 17.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/cli/spinners.py` | 7.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/cli/status_codes.py` | 116 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/commands/__init__.py` | 3.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/commands/cache.py` | 8.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/commands/check.py` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/commands/completion.py` | 4.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/commands/configuration.py` | 9.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/commands/debug.py` | 6.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/commands/download.py` | 5.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/commands/freeze.py` | 3.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/commands/hash.py` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/commands/help.py` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/commands/index.py` | 5.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/commands/inspect.py` | 3.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/commands/install.py` | 32.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/commands/list.py` | 13.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/commands/lock.py` | 5.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/commands/search.py` | 5.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/commands/show.py` | 7.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/commands/uninstall.py` | 3.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/commands/wheel.py` | 5.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/configuration.py` | 14.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/distributions/__init__.py` | 858 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/distributions/base.py` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/distributions/installed.py` | 929 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/distributions/sdist.py` | 6.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/distributions/wheel.py` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/exceptions.py` | 31.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/index/__init__.py` | 29 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/index/collector.py` | 15.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/index/package_finder.py` | 40.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/index/sources.py` | 8.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/locations/__init__.py` | 13.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/locations/_distutils.py` | 5.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/locations/_sysconfig.py` | 7.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/locations/base.py` | 2.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/main.py` | 338 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/metadata/__init__.py` | 5.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/metadata/_json.py` | 2.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/metadata/base.py` | 24.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/metadata/importlib/__init__.py` | 135 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/metadata/importlib/_compat.py` | 2.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/metadata/importlib/_dists.py` | 8.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/metadata/importlib/_envs.py` | 5.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/metadata/pkg_resources.py` | 10.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/models/__init__.py` | 62 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/models/candidate.py` | 720 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/models/direct_url.py` | 944 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/models/format_control.py` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/models/index.py` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/models/installation_report.py` | 2.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/models/link.py` | 21.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/models/release_control.py` | 3.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/models/scheme.py` | 558 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/models/search_scope.py` | 4.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/models/selection_prefs.py` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/models/target_python.py` | 4.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/models/wheel.py` | 2.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/network/__init__.py` | 49 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/network/auth.py` | 20.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/network/cache.py` | 4.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/network/download.py` | 12.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/network/lazy_wheel.py` | 7.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/network/session.py` | 19.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/network/utils.py` | 4.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/network/xmlrpc.py` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/operations/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/operations/build/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/operations/build/build_tracker.py` | 4.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/operations/build/metadata.py` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/operations/build/metadata_editable.py` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/operations/build/wheel.py` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/operations/build/wheel_editable.py` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/operations/check.py` | 5.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/operations/freeze.py` | 9.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/operations/install/__init__.py` | 50 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/operations/install/wheel.py` | 27.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/operations/prepare.py` | 28.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/pyproject.py` | 4.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/req/__init__.py` | 3.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/req/constructors.py` | 22.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/req/pep723.py` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/req/req_dependency_group.py` | 3.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/req/req_file.py` | 20.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/req/req_install.py` | 31.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/req/req_set.py` | 2.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/req/req_uninstall.py` | 23.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/resolution/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/resolution/base.py` | 577 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/resolution/legacy/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/resolution/legacy/resolver.py` | 23.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/resolution/resolvelib/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/resolution/resolvelib/base.py` | 5.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/resolution/resolvelib/candidates.py` | 20.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/resolution/resolvelib/factory.py` | 35.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/resolution/resolvelib/found_candidates.py` | 5.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/resolution/resolvelib/provider.py` | 11.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/resolution/resolvelib/reporter.py` | 3.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/resolution/resolvelib/requirements.py` | 8.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/resolution/resolvelib/resolver.py` | 13.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/self_outdated_check.py` | 7.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/utils/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/utils/_jaraco_text.py` | 3.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/utils/_log.py` | 1015 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/utils/appdirs.py` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/utils/compat.py` | 2.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/utils/compatibility_tags.py` | 6.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/utils/datetime.py` | 868 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/utils/deprecation.py` | 4.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/utils/direct_url_helpers.py` | 3.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/utils/egg_link.py` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/utils/entrypoints.py` | 3.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/utils/filesystem.py` | 6.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/utils/filetypes.py` | 689 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/utils/glibc.py` | 3.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/utils/hashes.py` | 4.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/utils/logging.py` | 13.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/utils/misc.py` | 23.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/utils/packaging.py` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/utils/pylock.py` | 9.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/utils/retry.py` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/utils/subprocess.py` | 8.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/utils/temp_dir.py` | 9.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/utils/unpacking.py` | 13.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/utils/urls.py` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/utils/virtualenv.py` | 3.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/utils/wheel.py` | 4.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/vcs/__init__.py` | 596 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/vcs/bazaar.py` | 3.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/vcs/git.py` | 18.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/vcs/mercurial.py` | 5.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/vcs/subversion.py` | 11.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/vcs/versioncontrol.py` | 22.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_internal/wheel_builder.py` | 8.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/__init__.py` | 4.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/cachecontrol/__init__.py` | 820 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/cachecontrol/_cmd.py` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/cachecontrol/adapter.py` | 6.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/cachecontrol/cache.py` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/cachecontrol/caches/__init__.py` | 303 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/cachecontrol/caches/file_cache.py` | 4.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/cachecontrol/caches/redis_cache.py` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/cachecontrol/controller.py` | 18.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/cachecontrol/filewrapper.py` | 4.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/cachecontrol/heuristics.py` | 4.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/cachecontrol/LICENSE.txt` | 558 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/cachecontrol/py.typed` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/cachecontrol/serialize.py` | 5.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/cachecontrol/wrapper.py` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/certifi/__init__.py` | 94 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/certifi/__main__.py` | 255 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/certifi/cacert.pem` | 266.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/certifi/core.py` | 3.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/certifi/LICENSE` | 989 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/certifi/py.typed` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/distlib/__init__.py` | 625 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/distlib/compat.py` | 40.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/distlib/LICENSE.txt` | 14.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/distlib/resources.py` | 10.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/distlib/scripts.py` | 18.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/distlib/t32.exe` | 95.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/distlib/t64-arm.exe` | 178.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/distlib/t64.exe` | 105.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/distlib/util.py` | 65.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/distlib/w32.exe` | 89.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/distlib/w64-arm.exe` | 164.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/distlib/w64.exe` | 99.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/distro/__init__.py` | 981 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/distro/__main__.py` | 64 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/distro/distro.py` | 48.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/distro/LICENSE` | 11.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/distro/py.typed` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/idna/__init__.py` | 868 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/idna/codec.py` | 3.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/idna/compat.py` | 316 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/idna/core.py` | 12.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/idna/idnadata.py` | 77.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/idna/intranges.py` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/idna/LICENSE.md` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/idna/package_data.py` | 21 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/idna/py.typed` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/idna/uts46data.py` | 238.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/msgpack/__init__.py` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/msgpack/COPYING` | 614 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/msgpack/exceptions.py` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/msgpack/ext.py` | 5.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/msgpack/fallback.py` | 31.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/packaging/__init__.py` | 494 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/packaging/_elffile.py` | 3.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/packaging/_manylinux.py` | 9.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/packaging/_musllinux.py` | 2.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/packaging/_parser.py` | 11.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/packaging/_structures.py` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/packaging/_tokenizer.py` | 5.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/packaging/dependency_groups.py` | 10.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/packaging/direct_url.py` | 10.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/packaging/errors.py` | 2.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/packaging/LICENSE` | 197 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/packaging/LICENSE.APACHE` | 9.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/packaging/LICENSE.BSD` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/packaging/licenses/__init__.py` | 7.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/packaging/licenses/_spdx.py` | 49.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/packaging/markers.py` | 16.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/packaging/metadata.py` | 37.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/packaging/py.typed` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/packaging/pylock.py` | 33.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/packaging/requirements.py` | 4.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/packaging/specifiers.py` | 69.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/packaging/tags.py` | 33.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/packaging/utils.py` | 9.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/packaging/version.py` | 37.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/pkg_resources/__init__.py` | 121.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/pkg_resources/LICENSE` | 1023 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/platformdirs/__init__.py` | 21.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/platformdirs/__main__.py` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/platformdirs/android.py` | 8.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/platformdirs/api.py` | 9.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/platformdirs/LICENSE` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/platformdirs/macos.py` | 6.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/platformdirs/py.typed` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/platformdirs/unix.py` | 10.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/platformdirs/version.py` | 704 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/platformdirs/windows.py` | 10.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/pygments/__init__.py` | 2.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/pygments/__main__.py` | 353 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/pygments/console.py` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/pygments/filter.py` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/pygments/filters/__init__.py` | 39.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/pygments/formatter.py` | 4.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/pygments/formatters/__init__.py` | 5.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/pygments/formatters/_mapping.py` | 4.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/pygments/lexer.py` | 34.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/pygments/lexers/__init__.py` | 11.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/pygments/lexers/_mapping.py` | 75.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/pygments/lexers/python.py` | 52.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/pygments/LICENSE` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/pygments/modeline.py` | 1005 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/pygments/plugin.py` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/pygments/regexopt.py` | 3.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/pygments/scanner.py` | 3.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/pygments/sphinxext.py` | 7.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/pygments/style.py` | 6.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/pygments/styles/__init__.py` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/pygments/styles/_mapping.py` | 3.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/pygments/token.py` | 6.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/pygments/unistring.py` | 61.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/pygments/util.py` | 9.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/pyproject_hooks/__init__.py` | 691 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/pyproject_hooks/_impl.py` | 14.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/pyproject_hooks/_in_process/__init__.py` | 557 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/pyproject_hooks/_in_process/_in_process.py` | 11.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/pyproject_hooks/LICENSE` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/pyproject_hooks/py.typed` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/README.rst` | 9.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/requests/__init__.py` | 4.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/requests/__version__.py` | 435 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/requests/_internal_utils.py` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/requests/adapters.py` | 25.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/requests/api.py` | 6.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/requests/auth.py` | 9.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/requests/certs.py` | 442 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/requests/compat.py` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/requests/cookies.py` | 18.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/requests/exceptions.py` | 4.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/requests/help.py` | 3.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/requests/hooks.py` | 734 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/requests/LICENSE` | 9.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/requests/models.py` | 34.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/requests/packages.py` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/requests/sessions.py` | 29.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/requests/status_codes.py` | 4.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/requests/structures.py` | 2.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/requests/utils.py` | 32.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/resolvelib/__init__.py` | 541 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/resolvelib/LICENSE` | 751 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/resolvelib/providers.py` | 8.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/resolvelib/py.typed` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/resolvelib/reporters.py` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/resolvelib/resolvers/__init__.py` | 640 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/resolvelib/resolvers/abstract.py` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/resolvelib/resolvers/criterion.py` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/resolvelib/resolvers/exceptions.py` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/resolvelib/resolvers/resolution.py` | 23.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/resolvelib/structs.py` | 6.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/__init__.py` | 5.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/__main__.py` | 7.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/_cell_widths.py` | 10.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/_emoji_codes.py` | 136.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/_emoji_replace.py` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/_export_format.py` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/_extension.py` | 265 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/_fileno.py` | 799 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/_inspect.py` | 9.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/_log_render.py` | 3.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/_loop.py` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/_null_file.py` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/_palettes.py` | 6.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/_pick.py` | 423 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/_ratio.py` | 5.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/_spinners.py` | 19.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/_stack.py` | 351 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/_timer.py` | 417 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/_win32_console.py` | 22.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/_windows.py` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/_windows_renderer.py` | 2.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/_wrap.py` | 3.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/abc.py` | 890 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/align.py` | 10.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/ansi.py` | 6.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/bar.py` | 3.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/box.py` | 10.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/cells.py` | 5.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/color.py` | 17.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/color_triplet.py` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/columns.py` | 7.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/console.py` | 98.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/constrain.py` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/containers.py` | 5.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/control.py` | 6.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/default_styles.py` | 8.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/diagnose.py` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/emoji.py` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/errors.py` | 642 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/file_proxy.py` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/filesize.py` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/highlighter.py` | 9.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/json.py` | 4.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/jupyter.py` | 3.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/layout.py` | 13.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/LICENSE` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/live.py` | 14.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/live_render.py` | 3.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/logging.py` | 12.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/markup.py` | 8.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/measure.py` | 5.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/padding.py` | 4.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/pager.py` | 828 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/palette.py` | 3.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/panel.py` | 10.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/pretty.py` | 35.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/progress.py` | 59.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/progress_bar.py` | 8.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/prompt.py` | 12.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/protocol.py` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/py.typed` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/region.py` | 166 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/repr.py` | 4.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/rule.py` | 4.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/scope.py` | 2.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/screen.py` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/segment.py` | 24.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/spinner.py` | 4.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/status.py` | 4.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/style.py` | 26.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/styled.py` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/syntax.py` | 35.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/table.py` | 39.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/terminal_theme.py` | 3.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/text.py` | 46.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/theme.py` | 3.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/themes.py` | 102 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/traceback.py` | 35.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/rich/tree.py` | 9.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/tomli/__init__.py` | 314 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/tomli/_parser.py` | 25.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/tomli/_re.py` | 3.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/tomli/_types.py` | 254 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/tomli/LICENSE` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/tomli/py.typed` | 26 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/tomli_w/__init__.py` | 169 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/tomli_w/_writer.py` | 6.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/tomli_w/LICENSE` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/tomli_w/py.typed` | 26 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/truststore/__init__.py` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/truststore/_api.py` | 11.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/truststore/_macos.py` | 20.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/truststore/_openssl.py` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/truststore/_ssl_constants.py` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/truststore/_windows.py` | 17.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/truststore/LICENSE` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/truststore/py.typed` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/__init__.py` | 6.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/_base_connection.py` | 5.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/_collections.py` | 17.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/_request_methods.py` | 9.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/_version.py` | 704 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/connection.py` | 41.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/connectionpool.py` | 42.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/contrib/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/contrib/emscripten/__init__.py` | 870 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/contrib/emscripten/connection.py` | 8.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/contrib/emscripten/emscripten_fetch_worker.js` | 3.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/contrib/emscripten/fetch.py` | 23.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/contrib/emscripten/request.py` | 566 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/contrib/emscripten/response.py` | 9.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/contrib/pyopenssl.py` | 19.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/contrib/socks.py` | 7.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/exceptions.py` | 9.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/fields.py` | 10.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/filepost.py` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/http2/__init__.py` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/http2/connection.py` | 12.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/http2/probe.py` | 2.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/LICENSE.txt` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/poolmanager.py` | 23.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/py.typed` | 93 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/response.py` | 51.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/util/__init__.py` | 1001 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/util/connection.py` | 4.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/util/proxy.py` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/util/request.py` | 7.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/util/response.py` | 3.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/util/retry.py` | 18.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/util/ssl_.py` | 19.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/util/ssl_match_hostname.py` | 5.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/util/ssltransport.py` | 8.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/util/timeout.py` | 10.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/util/url.py` | 14.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/util/util.py` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/urllib3/util/wait.py` | 4.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip/_vendor/vendor.txt` | 316 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip/py.typed` | 286 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/entry_points.txt` | 84 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/INSTALLER` | 4 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/AUTHORS.txt` | 11.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/LICENSE.txt` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/src/pip/_vendor/cachecontrol/LICENSE.txt` | 558 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/src/pip/_vendor/certifi/LICENSE` | 989 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/src/pip/_vendor/distlib/LICENSE.txt` | 14.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/src/pip/_vendor/distro/LICENSE` | 11.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/src/pip/_vendor/idna/LICENSE.md` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/src/pip/_vendor/msgpack/COPYING` | 614 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/src/pip/_vendor/packaging/LICENSE` | 197 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/src/pip/_vendor/packaging/LICENSE.APACHE` | 9.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/src/pip/_vendor/packaging/LICENSE.BSD` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/src/pip/_vendor/pkg_resources/LICENSE` | 1023 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/src/pip/_vendor/platformdirs/LICENSE` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/src/pip/_vendor/pygments/LICENSE` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/src/pip/_vendor/pyproject_hooks/LICENSE` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/src/pip/_vendor/requests/LICENSE` | 9.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/src/pip/_vendor/resolvelib/LICENSE` | 751 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/src/pip/_vendor/rich/LICENSE` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/src/pip/_vendor/tomli/LICENSE` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/src/pip/_vendor/tomli_w/LICENSE` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/src/pip/_vendor/truststore/LICENSE` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/licenses/src/pip/_vendor/urllib3/LICENSE.txt` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/METADATA` | 4.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/RECORD` | 65.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/REQUESTED` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pip-26.1.2.dist-info/WHEEL` | 82 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/__init__.pxd` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/__init__.py` | 19.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_acero.cp313-win_amd64.pyd` | 189.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_acero.pxd` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_acero.pyx` | 23.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_azurefs.cp313-win_amd64.pyd` | 88.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_azurefs.pyx` | 8.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_compute.cp313-win_amd64.pyd` | 765.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_compute.pxd` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_compute.pyx` | 117.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_compute_docstrings.py` | 8.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_csv.cp313-win_amd64.pyd` | 273.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_csv.pxd` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_csv.pyx` | 61.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_cuda.pxd` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_cuda.pyx` | 35.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_dataset.cp313-win_amd64.pyd` | 663.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_dataset.pxd` | 5.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_dataset.pyx` | 165.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_dataset_orc.cp313-win_amd64.pyd` | 68.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_dataset_orc.pyx` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_dataset_parquet.cp313-win_amd64.pyd` | 245.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_dataset_parquet.pxd` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_dataset_parquet.pyx` | 43.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_dataset_parquet_encryption.cp313-win_amd64.pyd` | 90.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_dataset_parquet_encryption.pyx` | 7.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_dlpack.pxi` | 2.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_feather.cp313-win_amd64.pyd` | 78.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_feather.pyx` | 3.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_flight.cp313-win_amd64.pyd` | 736.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_flight.pyx` | 115.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_fs.cp313-win_amd64.pyd` | 303.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_fs.pxd` | 2.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_fs.pyx` | 53.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_gcsfs.cp313-win_amd64.pyd` | 91.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_gcsfs.pyx` | 9.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_generated_version.py` | 546 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_hdfs.cp313-win_amd64.pyd` | 96.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_hdfs.pyx` | 6.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_json.cp313-win_amd64.pyd` | 101.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_json.pxd` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_json.pyx` | 13.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_orc.cp313-win_amd64.pyd` | 137.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_orc.pxd` | 5.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_orc.pyx` | 15.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_parquet.cp313-win_amd64.pyd` | 404.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_parquet.pxd` | 5.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_parquet.pyx` | 84.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_parquet_encryption.cp313-win_amd64.pyd` | 242.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_parquet_encryption.pxd` | 3.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_parquet_encryption.pyx` | 36.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_pyarrow_cpp_tests.cp313-win_amd64.pyd` | 72.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_pyarrow_cpp_tests.pxd` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_pyarrow_cpp_tests.pyx` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_s3fs.cp313-win_amd64.pyd` | 137.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_s3fs.pyx` | 20.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_substrait.cp313-win_amd64.pyd` | 138.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/_substrait.pyx` | 15.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/acero.py` | 15.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/array.pxi` | 179.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/arrow.dll` | 17.8 MB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/arrow.lib` | 4.0 MB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/arrow_acero.dll` | 1.2 MB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/arrow_acero.lib` | 282.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/arrow_compute.dll` | 9.6 MB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/arrow_compute.lib` | 179.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/arrow_dataset.dll` | 1.3 MB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/arrow_dataset.lib` | 403.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/arrow_flight.dll` | 14.0 MB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/arrow_flight.lib` | 530.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/arrow_python.dll` | 1.2 MB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/arrow_python.lib` | 166.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/arrow_python_flight.dll` | 63.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/arrow_python_flight.lib` | 57.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/arrow_python_parquet_encryption.dll` | 31.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/arrow_python_parquet_encryption.lib` | 20.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/arrow_s3.dll` | 3.7 MB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/arrow_s3.lib` | 48.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/arrow_substrait.dll` | 2.6 MB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/arrow_substrait.lib` | 108.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/benchmark.pxi` | 889 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/benchmark.py` | 877 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/builder.pxi` | 4.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/cffi.py` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/compat.pxi` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/compute.py` | 25.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/config.pxi` | 4.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/conftest.py` | 10.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/csv.py` | 996 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/cuda.py` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/dataset.py` | 40.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/device.pxi` | 5.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/error.pxi` | 9.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/feather.py` | 11.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/flight.py` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/fs.py` | 15.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/gandiva.pyx` | 24.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/acero/accumulation_queue.h` | 6.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/acero/aggregate_node.h` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/acero/api.h` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/acero/asof_join_node.h` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/acero/backpressure_handler.h` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/acero/benchmark_util.h` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/acero/bloom_filter.h` | 12.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/acero/exec_plan.h` | 35.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/acero/hash_join.h` | 3.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/acero/hash_join_dict.h` | 15.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/acero/hash_join_node.h` | 4.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/acero/map_node.h` | 2.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/acero/options.h` | 37.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/acero/order_by_impl.h` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/acero/partition_util.h` | 7.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/acero/query_context.h` | 6.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/acero/schema_util.h` | 8.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/acero/task_util.h` | 3.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/acero/test_nodes.h` | 2.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/acero/time_series_util.h` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/acero/tpch_node.h` | 2.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/acero/type_fwd.h` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/acero/util.h` | 6.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/acero/visibility.h` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/adapters/orc/adapter.h` | 11.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/adapters/orc/options.h` | 3.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/adapters/tensorflow/convert.h` | 3.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/api.h` | 2.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/array/array_base.h` | 13.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/array/array_binary.h` | 11.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/array/array_decimal.h` | 3.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/array/array_dict.h` | 7.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/array/array_nested.h` | 38.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/array/array_primitive.h` | 8.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/array/array_run_end.h` | 5.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/array/builder_adaptive.h` | 6.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/array/builder_base.h` | 13.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/array/builder_binary.h` | 34.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/array/builder_decimal.h` | 5.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/array/builder_dict.h` | 30.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/array/builder_nested.h` | 31.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/array/builder_primitive.h` | 26.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/array/builder_run_end.h` | 11.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/array/builder_time.h` | 2.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/array/builder_union.h` | 10.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/array/concatenate.h` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/array/data.h` | 30.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/array/diff.h` | 3.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/array/statistics.h` | 6.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/array/util.h` | 3.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/array/validate.h` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/array.h` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/buffer.h` | 25.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/buffer_builder.h` | 17.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/builder.h` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/c/abi.h` | 20.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/c/bridge.h` | 21.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/c/dlpack.h` | 5.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/c/dlpack_abi.h` | 23.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/c/helpers.h` | 6.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/chunk_resolver.h` | 12.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/chunked_array.h` | 11.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/compare.h` | 9.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/compute/api.h` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/compute/api_aggregate.h` | 22.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/compute/api_scalar.h` | 72.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/compute/api_vector.h` | 39.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/compute/cast.h` | 4.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/compute/exec.h` | 18.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/compute/expression.h` | 11.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/compute/function.h` | 16.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/compute/function_options.h` | 3.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/compute/initialize.h` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/compute/kernel.h` | 32.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/compute/ordering.h` | 4.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/compute/registry.h` | 4.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/compute/row/grouper.h` | 7.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/compute/type_fwd.h` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/compute/util.h` | 9.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/compute/visibility.h` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/config.h` | 4.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/csv/api.h` | 929 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/csv/chunker.h` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/csv/column_builder.h` | 2.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/csv/column_decoder.h` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/csv/converter.h` | 3.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/csv/invalid_row.h` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/csv/options.h` | 8.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/csv/parser.h` | 9.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/csv/reader.h` | 4.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/csv/test_common.h` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/csv/type_fwd.h` | 1012 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/csv/writer.h` | 3.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/dataset/api.h` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/dataset/dataset.h` | 20.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/dataset/dataset_writer.h` | 4.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/dataset/discovery.h` | 11.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/dataset/file_base.h` | 20.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/dataset/file_csv.h` | 5.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/dataset/file_ipc.h` | 4.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/dataset/file_json.h` | 3.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/dataset/file_orc.h` | 2.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/dataset/file_parquet.h` | 16.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/dataset/parquet_encryption_config.h` | 3.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/dataset/partition.h` | 16.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/dataset/plan.h` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/dataset/projector.h` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/dataset/scanner.h` | 26.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/dataset/type_fwd.h` | 3.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/dataset/visibility.h` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/datum.h` | 12.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/device.h` | 15.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/device_allocation_type_set.h` | 3.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/engine/api.h` | 908 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/engine/substrait/api.h` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/engine/substrait/extension_set.h` | 21.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/engine/substrait/extension_types.h` | 3.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/engine/substrait/options.h` | 5.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/engine/substrait/relation.h` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/engine/substrait/serde.h` | 16.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/engine/substrait/test_plan_builder.h` | 3.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/engine/substrait/test_util.h` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/engine/substrait/type_fwd.h` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/engine/substrait/util.h` | 3.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/engine/substrait/visibility.h` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/extension/bool8.h` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/extension/fixed_shape_tensor.h` | 5.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/extension/json.h` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/extension/opaque.h` | 2.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/extension/parquet_variant.h` | 2.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/extension/uuid.h` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/extension/variable_shape_tensor.h` | 4.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/extension_type.h` | 6.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/filesystem/api.h` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/filesystem/azurefs.h` | 15.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/filesystem/filesystem.h` | 33.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/filesystem/filesystem_library.h` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/filesystem/gcsfs.h` | 10.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/filesystem/hdfs.h` | 4.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/filesystem/localfs.h` | 5.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/filesystem/mockfs.h` | 4.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/filesystem/path_util.h` | 5.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/filesystem/s3_test_util.h` | 3.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/filesystem/s3_visibility.h` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/filesystem/s3fs.h` | 19.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/filesystem/test_util.h` | 11.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/filesystem/type_fwd.h` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/flight/api.h` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/flight/client.h` | 17.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/flight/client_auth.h` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/flight/client_cookie_middleware.h` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/flight/client_middleware.h` | 3.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/flight/client_tracing_middleware.h` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/flight/middleware.h` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/flight/otel_logging.h` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/flight/platform.h` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/flight/server.h` | 13.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/flight/server_auth.h` | 4.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/flight/server_middleware.h` | 3.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/flight/server_tracing_middleware.h` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/flight/test_auth_handlers.h` | 3.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/flight/test_definitions.h` | 13.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/flight/test_flight_server.h` | 3.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/flight/test_util.h` | 6.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/flight/transport.h` | 12.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/flight/transport_server.h` | 5.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/flight/type_fwd.h` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/flight/types.h` | 47.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/flight/types_async.h` | 2.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/flight/visibility.h` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/io/api.h` | 993 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/io/buffered.h` | 5.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/io/caching.h` | 6.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/io/compressed.h` | 3.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/io/concurrency.h` | 8.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/io/file.h` | 7.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/io/interfaces.h` | 15.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/io/memory.h` | 6.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/io/mman.h` | 4.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/io/slow.h` | 4.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/io/stdio.h` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/io/test_common.h` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/io/transform.h` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/io/type_fwd.h` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/ipc/api.h` | 996 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/ipc/dictionary.h` | 6.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/ipc/feather.h` | 6.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/ipc/message.h` | 21.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/ipc/options.h` | 7.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/ipc/reader.h` | 24.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/ipc/test_common.h` | 6.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/ipc/type_fwd.h` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/ipc/util.h` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/ipc/writer.h` | 19.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/json/api.h` | 900 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/json/chunked_builder.h` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/json/chunker.h` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/json/converter.h` | 3.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/json/from_string.h` | 4.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/json/options.h` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/json/parser.h` | 3.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/json/rapidjson_defs.h` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/json/reader.h` | 5.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/json/test_common.h` | 10.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/json/type_fwd.h` | 968 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/memory_pool.h` | 12.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/memory_pool_test.h` | 3.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/pretty_print.h` | 5.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/python/api.h` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/python/arrow_to_pandas.h` | 6.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/python/async.h` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/python/benchmark.h` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/python/common.h` | 15.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/python/config.h` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/python/csv.h` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/python/datetime.h` | 8.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/python/decimal.h` | 6.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/python/extension_type.h` | 3.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/python/filesystem.h` | 5.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/python/flight.h` | 14.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/python/gdb.h` | 1001 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/python/helpers.h` | 5.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/python/inference.h` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/python/io.h` | 3.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/python/ipc.h` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/python/iterators.h` | 7.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/python/lib.h` | 4.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/python/lib_api.h` | 20.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/python/numpy_convert.h` | 4.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/python/numpy_init.h` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/python/numpy_interop.h` | 3.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/python/numpy_to_arrow.h` | 2.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/python/parquet_encryption.h` | 5.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/python/platform.h` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/python/pyarrow.h` | 2.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/python/pyarrow_api.h` | 886 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/python/pyarrow_lib.h` | 882 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/python/python_test.h` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/python/python_to_arrow.h` | 2.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/python/type_traits.h` | 10.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/python/udf.h` | 3.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/python/util.h` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/python/vendored/pythoncapi_compat.h` | 41.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/python/visibility.h` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/record_batch.h` | 19.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/result.h` | 18.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/scalar.h` | 38.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/sparse_tensor.h` | 25.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/status.h` | 17.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/stl.h` | 19.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/stl_allocator.h` | 5.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/stl_iterator.h` | 10.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/table.h` | 15.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/table_builder.h` | 3.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/telemetry/logging.h` | 3.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/tensor/converter.h` | 2.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/tensor.h` | 10.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/testing/async_test_util.h` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/testing/builder.h` | 9.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/testing/examplefs.h` | 1009 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/testing/executor_util.h` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/testing/extension_type.h` | 9.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/testing/fixed_width_test_util.h` | 3.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/testing/future_util.h` | 6.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/testing/generator.h` | 13.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/testing/gtest_compat.h` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/testing/gtest_util.h` | 24.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/testing/matchers.h` | 16.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/testing/math.h` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/testing/process.h` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/testing/random.h` | 38.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/testing/uniform_real.h` | 3.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/testing/util.h` | 6.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/testing/visibility.h` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/type.h` | 97.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/type_fwd.h` | 23.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/type_traits.h` | 57.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/algorithm.h` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/align_util.h` | 11.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/aligned_storage.h` | 4.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/async_generator.h` | 82.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/async_generator_fwd.h` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/async_util.h` | 19.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/base64.h` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/basic_decimal.h` | 33.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/benchmark_util.h` | 7.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/binary_view_util.h` | 4.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/bit_block_counter.h` | 20.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/bit_run_reader.h` | 21.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/bit_util.h` | 13.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/bitmap.h` | 17.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/bitmap_builders.h` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/bitmap_generate.h` | 3.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/bitmap_ops.h` | 12.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/bitmap_reader.h` | 8.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/bitmap_visit.h` | 3.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/bitmap_writer.h` | 9.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/byte_size.h` | 4.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/cancel.h` | 3.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/checked_cast.h` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/compare.h` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/compression.h` | 8.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/concurrent_map.h` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/config.h` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/converter.h` | 14.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/cpu_info.h` | 4.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/crc32.h` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/debug.h` | 1000 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/decimal.h` | 20.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/delimiting.h` | 7.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/endian.h` | 8.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/float16.h` | 7.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/formatting.h` | 22.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/functional.h` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/future.h` | 31.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/hash_util.h` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/hashing.h` | 34.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/int_util.h` | 4.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/int_util_overflow.h` | 8.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/io_util.h` | 14.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/iterator.h` | 18.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/key_value_metadata.h` | 3.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/launder.h` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/list_util.h` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/logger.h` | 6.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/logging.h` | 9.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/macros.h` | 9.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/math_constants.h` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/mutex.h` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/parallel.h` | 3.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/pcg_random.h` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/prefetch.h` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/queue.h` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/range.h` | 8.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/ree_util.h` | 22.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/regex.h` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/rows_to_batches.h` | 7.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/secure_string.h` | 2.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/simd.h` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/small_vector.h` | 14.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/string.h` | 5.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/string_util.h` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/task_group.h` | 4.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/test_common.h` | 3.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/thread_pool.h` | 25.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/time.h` | 3.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/tracing.h` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/type_fwd.h` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/type_traits.h` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/ubsan.h` | 3.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/union_util.h` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/unreachable.h` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/uri.h` | 3.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/utf8.h` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/value_parsing.h` | 30.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/vector.h` | 5.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/visibility.h` | 3.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/windows_compatibility.h` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/util/windows_fixup.h` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/vendored/datetime/date.h` | 240.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/vendored/datetime/ios.h` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/vendored/datetime/tz.h` | 86.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/vendored/datetime/tz_private.h` | 10.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/vendored/datetime/visibility.h` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/vendored/datetime.h` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/vendored/double-conversion/bignum-dtoa.h` | 4.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/vendored/double-conversion/bignum.h` | 6.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/vendored/double-conversion/cached-powers.h` | 3.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/vendored/double-conversion/diy-fp.h` | 5.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/vendored/double-conversion/double-conversion.h` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/vendored/double-conversion/double-to-string.h` | 23.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/vendored/double-conversion/fast-dtoa.h` | 4.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/vendored/double-conversion/fixed-dtoa.h` | 2.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/vendored/double-conversion/ieee.h` | 15.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/vendored/double-conversion/string-to-double.h` | 10.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/vendored/double-conversion/strtod.h` | 3.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/vendored/double-conversion/utils.h` | 15.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/vendored/pcg/pcg_extras.hpp` | 20.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/vendored/pcg/pcg_random.hpp` | 73.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/vendored/pcg/pcg_uint128.hpp` | 29.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/vendored/portable-snippets/debug-trap.h` | 3.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/vendored/ProducerConsumerQueue.h` | 6.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/vendored/safeint/safe_math.h` | 77.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/vendored/safeint/safe_math_impl.h` | 62.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/vendored/strptime.h` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/vendored/xxhash/xxhash.h` | 280.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/vendored/xxhash.h` | 862 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/visit_array_inline.h` | 2.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/visit_data_inline.h` | 12.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/visit_scalar_inline.h` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/visit_type_inline.h` | 5.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/visitor.h` | 8.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/arrow/visitor_generate.h` | 3.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/api/io.h` | 867 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/api/reader.h` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/api/schema.h` | 876 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/api/writer.h` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/arrow/reader.h` | 15.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/arrow/schema.h` | 6.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/arrow/test_util.h` | 18.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/arrow/writer.h` | 7.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/benchmark_util.h` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/bloom_filter.h` | 17.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/bloom_filter_reader.h` | 2.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/bloom_filter_writer.h` | 4.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/column_page.h` | 7.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/column_reader.h` | 20.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/column_scanner.h` | 8.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/column_writer.h` | 13.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/encoding.h` | 18.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/encryption/crypto_factory.h` | 7.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/encryption/encryption.h` | 16.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/encryption/file_key_material_store.h` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/encryption/file_key_unwrapper.h` | 4.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/encryption/file_key_wrapper.h` | 3.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/encryption/file_system_key_material_store.h` | 3.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/encryption/key_encryption_key.h` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/encryption/key_material.h` | 6.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/encryption/key_metadata.h` | 4.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/encryption/key_toolkit.h` | 4.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/encryption/kms_client.h` | 3.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/encryption/kms_client_factory.h` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/encryption/local_wrap_kms_client.h` | 4.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/encryption/test_encryption_util.h` | 5.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/encryption/test_in_memory_kms.h` | 4.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/encryption/two_level_cache_with_expiration.h` | 4.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/encryption/type_fwd.h` | 983 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/exception.h` | 6.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/file_reader.h` | 11.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/file_writer.h` | 10.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/geospatial/statistics.h` | 8.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/hasher.h` | 5.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/index_location.h` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/level_comparison.h` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/level_comparison_inc.h` | 2.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/level_conversion.h` | 8.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/level_conversion_inc.h` | 14.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/metadata.h` | 21.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/page_index.h` | 17.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/parquet_version.h` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/platform.h` | 4.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/printer.h` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/properties.h` | 65.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/schema.h` | 18.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/size_statistics.h` | 4.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/statistics.h` | 18.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/stream_reader.h` | 8.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/stream_writer.h` | 7.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/test_util.h` | 33.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/type_fwd.h` | 3.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/types.h` | 27.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/visit_type_inline.h` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/windows_compatibility.h` | 918 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/windows_fixup.h` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/include/parquet/xxhasher.h` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/includes/__init__.pxd` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/includes/common.pxd` | 5.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/includes/libarrow.pxd` | 121.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/includes/libarrow_acero.pxd` | 5.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/includes/libarrow_cuda.pxd` | 4.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/includes/libarrow_dataset.pxd` | 17.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/includes/libarrow_dataset_parquet.pxd` | 4.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/includes/libarrow_feather.pxd` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/includes/libarrow_flight.pxd` | 24.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/includes/libarrow_fs.pxd` | 15.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/includes/libarrow_python.pxd` | 11.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/includes/libarrow_substrait.pxd` | 4.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/includes/libgandiva.pxd` | 11.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/includes/libparquet.pxd` | 28.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/includes/libparquet_encryption.pxd` | 8.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/interchange/__init__.py` | 865 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/interchange/buffer.py` | 3.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/interchange/column.py` | 19.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/interchange/dataframe.py` | 8.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/interchange/from_dataframe.py` | 19.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/io.pxi` | 88.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/ipc.pxi` | 46.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/ipc.py` | 9.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/json.py` | 888 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/jvm.py` | 9.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/lib.cp313-win_amd64.pyd` | 3.4 MB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/lib.pxd` | 18.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/lib.pyx` | 6.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/memory.pxi` | 8.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/orc.py` | 12.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/pandas-shim.pxi` | 7.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/pandas_compat.py` | 45.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/parquet/__init__.py` | 842 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/parquet/core.py` | 99.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/parquet/encryption.py` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/parquet.dll` | 6.8 MB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/parquet.lib` | 851.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/public-api.pxi` | 14.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/scalar.pxi` | 56.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/api.h` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/arrow_to_pandas.cc` | 98.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/arrow_to_pandas.h` | 6.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/arrow_to_python_internal.h` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/async.h` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/benchmark.cc` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/benchmark.h` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/CMakeLists.txt` | 874 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/common.cc` | 7.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/common.h` | 15.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/config.cc` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/config.h` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/config_internal.h.cmake` | 910 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/csv.cc` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/csv.h` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/datetime.cc` | 23.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/datetime.h` | 8.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/decimal.cc` | 9.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/decimal.h` | 6.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/extension_type.cc` | 7.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/extension_type.h` | 3.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/filesystem.cc` | 6.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/filesystem.h` | 5.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/flight.cc` | 14.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/flight.h` | 14.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/gdb.cc` | 25.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/gdb.h` | 1001 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/helpers.cc` | 18.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/helpers.h` | 5.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/inference.cc` | 27.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/inference.h` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/io.cc` | 12.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/io.h` | 3.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/ipc.cc` | 4.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/ipc.h` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/iterators.h` | 7.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/numpy_convert.cc` | 21.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/numpy_convert.h` | 4.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/numpy_init.cc` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/numpy_init.h` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/numpy_internal.h` | 5.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/numpy_interop.h` | 3.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/numpy_to_arrow.cc` | 34.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/numpy_to_arrow.h` | 2.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/parquet_encryption.cc` | 4.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/parquet_encryption.h` | 5.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/platform.h` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/pyarrow.cc` | 3.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/pyarrow.h` | 2.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/pyarrow_api.h` | 886 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/pyarrow_lib.h` | 882 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/python_test.cc` | 33.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/python_test.h` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/python_to_arrow.cc` | 50.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/python_to_arrow.h` | 2.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/type_traits.h` | 10.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/udf.cc` | 29.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/udf.h` | 3.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/util.cc` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/util.h` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/vendored/CMakeLists.txt` | 855 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/vendored/pythoncapi_compat.h` | 41.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/src/arrow/python/visibility.h` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/substrait.py` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/table.pxi` | 211.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tensor.pxi` | 52.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/arrow_16597.py` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/arrow_39313.py` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/arrow_7980.py` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/bound_function_visit_strings.pyx` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/conftest.py` | 10.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/data/feather/v0.17.0.version.2-compression.lz4.feather` | 594 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/data/orc/decimal.jsn.gz` | 18.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/data/orc/decimal.orc` | 16.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/data/orc/README.md` | 954 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/data/orc/TestOrcFile.emptyFile.jsn.gz` | 50 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/data/orc/TestOrcFile.emptyFile.orc` | 523 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/data/orc/TestOrcFile.test1.jsn.gz` | 323 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/data/orc/TestOrcFile.test1.orc` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/data/orc/TestOrcFile.testDate1900.jsn.gz` | 178.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/data/orc/TestOrcFile.testDate1900.orc` | 30.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/data/parquet/v0.7.1.all-named-index.parquet` | 3.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/data/parquet/v0.7.1.column-metadata-handling.parquet` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/data/parquet/v0.7.1.parquet` | 4.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/data/parquet/v0.7.1.some-named-index.parquet` | 3.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/extensions.pyx` | 3.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/interchange/__init__.py` | 801 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/interchange/test_conversion.py` | 16.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/interchange/test_interchange_spec.py` | 9.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/pandas_examples.py` | 5.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/pandas_threaded_import.py` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/parquet/__init__.py` | 955 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/parquet/common.py` | 6.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/parquet/conftest.py` | 3.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/parquet/encryption.py` | 5.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/parquet/test_basic.py` | 40.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/parquet/test_compliant_nested_type.py` | 3.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/parquet/test_data_types.py` | 20.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/parquet/test_dataset.py` | 44.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/parquet/test_datetime.py` | 16.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/parquet/test_encryption.py` | 43.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/parquet/test_metadata.py` | 30.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/parquet/test_pandas.py` | 23.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/parquet/test_parquet_file.py` | 14.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/parquet/test_parquet_writer.py` | 18.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/pyarrow_cython_example.pyx` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/read_record_batch.py` | 978 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/strategies.py` | 16.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_acero.py` | 21.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_adhoc_memory_leak.py` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_array.py` | 161.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_builder.py` | 2.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_cffi.py` | 27.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_compute.py` | 174.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_convert_builtin.py` | 83.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_cpp_internals.py` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_csv.py` | 85.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_cuda.py` | 36.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_cuda_numba_interop.py` | 8.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_cython.py` | 7.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_dataset.py` | 221.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_dataset_encryption.py` | 17.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_deprecations.py` | 914 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_device.py` | 2.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_dlpack.py` | 18.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_exec_plan.py` | 10.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_extension_type.py` | 82.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_feather.py` | 27.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_flight.py` | 105.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_flight_async.py` | 2.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_fs.py` | 74.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_gandiva.py` | 15.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_gdb.py` | 48.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_io.py` | 65.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_ipc.py` | 47.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_json.py` | 24.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_jvm.py` | 15.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_memory.py` | 9.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_misc.py` | 7.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_orc.py` | 21.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_pandas.py` | 196.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_scalars.py` | 33.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_schema.py` | 23.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_sparse_tensor.py` | 17.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_strategies.py` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_substrait.py` | 33.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_table.py` | 130.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_tensor.py` | 6.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_types.py` | 45.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_udf.py` | 30.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_util.py` | 5.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/test_without_numpy.py` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/util.py` | 13.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/tests/wsgi_examples.py` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/types.pxi` | 165.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/types.py` | 9.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/util.py` | 9.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/vendored/__init__.py` | 801 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/vendored/docscrape.py` | 23.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow/vendored/version.py` | 14.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow-26.0.0.dist-info/DELVEWHEEL` | 303 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow-26.0.0.dist-info/INSTALLER` | 4 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow-26.0.0.dist-info/licenses/LICENSE.txt` | 110.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow-26.0.0.dist-info/licenses/NOTICE.txt` | 2.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow-26.0.0.dist-info/METADATA` | 3.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow-26.0.0.dist-info/RECORD` | 76.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow-26.0.0.dist-info/REQUESTED` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow-26.0.0.dist-info/WHEEL` | 105 B |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow.libs/msvcp140-0fa7eb792d3fbcf2233e4ea47e9144b9.dll` | 544.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pyarrow.libs/msvcp140_atomic_wait-aa4e4b3f35a38f595be5cf8631717b66.dll` | 29.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/python_dateutil-2.9.0.post0.dist-info/INSTALLER` | 4 B |
| `.venv_c_mirror_backup/Lib/site-packages/python_dateutil-2.9.0.post0.dist-info/LICENSE` | 2.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/python_dateutil-2.9.0.post0.dist-info/METADATA` | 8.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/python_dateutil-2.9.0.post0.dist-info/RECORD` | 3.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/python_dateutil-2.9.0.post0.dist-info/top_level.txt` | 9 B |
| `.venv_c_mirror_backup/Lib/site-packages/python_dateutil-2.9.0.post0.dist-info/WHEEL` | 110 B |
| `.venv_c_mirror_backup/Lib/site-packages/python_dateutil-2.9.0.post0.dist-info/zip-safe` | 1 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/__init__.py` | 35.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/exceptions.py` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/lazy.py` | 5.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/reference.py` | 3.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/tzfile.py` | 4.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/tzinfo.py` | 19.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Abidjan` | 148 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Accra` | 148 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Addis_Ababa` | 265 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Algiers` | 735 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Asmara` | 265 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Asmera` | 265 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Bamako` | 148 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Bangui` | 235 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Banjul` | 148 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Bissau` | 194 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Blantyre` | 149 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Brazzaville` | 235 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Bujumbura` | 149 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Cairo` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Casablanca` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Ceuta` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Conakry` | 148 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Dakar` | 148 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Dar_es_Salaam` | 265 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Djibouti` | 265 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Douala` | 235 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/El_Aaiun` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Freetown` | 148 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Gaborone` | 149 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Harare` | 149 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Johannesburg` | 246 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Juba` | 679 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Kampala` | 265 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Khartoum` | 679 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Kigali` | 149 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Kinshasa` | 235 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Lagos` | 235 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Libreville` | 235 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Lome` | 148 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Luanda` | 235 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Lubumbashi` | 149 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Lusaka` | 149 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Malabo` | 235 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Maputo` | 149 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Maseru` | 246 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Mbabane` | 246 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Mogadishu` | 265 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Monrovia` | 208 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Nairobi` | 265 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Ndjamena` | 199 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Niamey` | 235 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Nouakchott` | 148 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Ouagadougou` | 148 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Porto-Novo` | 235 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Sao_Tome` | 254 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Timbuktu` | 148 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Tripoli` | 625 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Tunis` | 689 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Africa/Windhoek` | 955 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Adak` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Anchorage` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Anguilla` | 246 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Antigua` | 246 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Araguaina` | 870 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Argentina/Buenos_Aires` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Argentina/Catamarca` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Argentina/ComodRivadavia` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Argentina/Cordoba` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Argentina/Jujuy` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Argentina/La_Rioja` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Argentina/Mendoza` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Argentina/Rio_Gallegos` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Argentina/Salta` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Argentina/San_Juan` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Argentina/San_Luis` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Argentina/Tucuman` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Argentina/Ushuaia` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Aruba` | 246 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Asuncion` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Atikokan` | 182 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Atka` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Bahia` | 1010 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Bahia_Banderas` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Barbados` | 436 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Belem` | 562 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Belize` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Blanc-Sablon` | 246 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Boa_Vista` | 618 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Bogota` | 232 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Boise` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Buenos_Aires` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Cambridge_Bay` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Campo_Grande` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Cancun` | 864 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Caracas` | 250 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Catamarca` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Cayenne` | 184 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Cayman` | 182 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Chicago` | 3.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Chihuahua` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Ciudad_Juarez` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Coral_Harbour` | 182 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Cordoba` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Costa_Rica` | 316 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Coyhaique` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Creston` | 360 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Cuiaba` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Curacao` | 246 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Danmarkshavn` | 698 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Dawson` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Dawson_Creek` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Denver` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Detroit` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Dominica` | 246 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Edmonton` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Eirunepe` | 642 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/El_Salvador` | 224 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Ensenada` | 2.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Fort_Nelson` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Fort_Wayne` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Fortaleza` | 702 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Glace_Bay` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Godthab` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Goose_Bay` | 3.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Grand_Turk` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Grenada` | 246 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Guadeloupe` | 246 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Guatemala` | 280 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Guayaquil` | 232 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Guyana` | 248 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Halifax` | 3.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Havana` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Hermosillo` | 388 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Indiana/Indianapolis` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Indiana/Knox` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Indiana/Marengo` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Indiana/Petersburg` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Indiana/Tell_City` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Indiana/Vevay` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Indiana/Vincennes` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Indiana/Winamac` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Indianapolis` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Inuvik` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Iqaluit` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Jamaica` | 482 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Jujuy` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Juneau` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Kentucky/Louisville` | 2.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Kentucky/Monticello` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Knox_IN` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Kralendijk` | 246 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/La_Paz` | 218 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Lima` | 392 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Los_Angeles` | 2.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Louisville` | 2.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Lower_Princes` | 246 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Maceio` | 730 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Managua` | 430 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Manaus` | 590 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Marigot` | 246 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Martinique` | 232 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Matamoros` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Mazatlan` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Mendoza` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Menominee` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Merida` | 1004 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Metlakatla` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Mexico_City` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Miquelon` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Moncton` | 3.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Monterrey` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Montevideo` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Montreal` | 3.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Montserrat` | 246 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Nassau` | 3.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/New_York` | 3.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Nipigon` | 3.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Nome` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Noronha` | 702 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/North_Dakota/Beulah` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/North_Dakota/Center` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/North_Dakota/New_Salem` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Nuuk` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Ojinaga` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Panama` | 182 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Pangnirtung` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Paramaribo` | 248 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Phoenix` | 360 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Port-au-Prince` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Port_of_Spain` | 246 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Porto_Acre` | 614 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Porto_Velho` | 562 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Puerto_Rico` | 246 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Punta_Arenas` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Rainy_River` | 2.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Rankin_Inlet` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Recife` | 702 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Regina` | 980 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Resolute` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Rio_Branco` | 614 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Rosario` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Santa_Isabel` | 2.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Santarem` | 588 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Santiago` | 2.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Santo_Domingo` | 458 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Sao_Paulo` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Scoresbysund` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Shiprock` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Sitka` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/St_Barthelemy` | 246 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/St_Johns` | 3.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/St_Kitts` | 246 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/St_Lucia` | 246 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/St_Thomas` | 246 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/St_Vincent` | 246 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Swift_Current` | 560 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Tegucigalpa` | 252 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Thule` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Thunder_Bay` | 3.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Tijuana` | 2.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Toronto` | 3.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Tortola` | 246 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Vancouver` | 2.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Virgin` | 246 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Whitehorse` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Winnipeg` | 2.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Yakutat` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/America/Yellowknife` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Antarctica/Casey` | 423 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Antarctica/Davis` | 283 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Antarctica/DumontDUrville` | 172 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Antarctica/Macquarie` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Antarctica/Mawson` | 185 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Antarctica/McMurdo` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Antarctica/Palmer` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Antarctica/Rothera` | 150 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Antarctica/South_Pole` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Antarctica/Syowa` | 151 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Antarctica/Troll` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Antarctica/Vostok` | 213 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Arctic/Longyearbyen` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Aden` | 151 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Almaty` | 983 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Amman` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Anadyr` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Aqtau` | 969 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Aqtobe` | 997 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Ashgabat` | 605 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Ashkhabad` | 605 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Atyrau` | 977 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Baghdad` | 969 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Bahrain` | 185 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Baku` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Bangkok` | 185 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Barnaul` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Beirut` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Bishkek` | 969 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Brunei` | 469 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Calcutta` | 285 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Chita` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Choibalsan` | 877 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Chongqing` | 561 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Chungking` | 561 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Colombo` | 358 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Dacca` | 323 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Damascus` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Dhaka` | 323 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Dili` | 257 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Dubai` | 151 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Dushanbe` | 577 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Famagusta` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Gaza` | 3.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Harbin` | 561 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Hebron` | 3.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Ho_Chi_Minh` | 329 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Hong_Kong` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Hovd` | 877 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Irkutsk` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Istanbul` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Jakarta` | 383 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Jayapura` | 221 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Jerusalem` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Kabul` | 194 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Kamchatka` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Karachi` | 379 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Kashgar` | 151 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Kathmandu` | 198 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Katmandu` | 198 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Khandyga` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Kolkata` | 285 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Krasnoyarsk` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Kuala_Lumpur` | 401 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Kuching` | 469 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Kuwait` | 151 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Macao` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Macau` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Magadan` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Makassar` | 254 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Manila` | 422 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Muscat` | 151 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Nicosia` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Novokuznetsk` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Novosibirsk` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Omsk` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Oral` | 991 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Phnom_Penh` | 185 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Pontianak` | 353 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Pyongyang` | 237 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Qatar` | 185 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Qostanay` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Qyzylorda` | 1011 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Rangoon` | 254 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Riyadh` | 151 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Saigon` | 329 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Sakhalin` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Samarkand` | 563 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Seoul` | 617 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Shanghai` | 561 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Singapore` | 401 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Srednekolymsk` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Taipei` | 761 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Tashkent` | 577 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Tbilisi` | 1007 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Tehran` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Tel_Aviv` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Thimbu` | 189 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Thimphu` | 189 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Tokyo` | 309 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Tomsk` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Ujung_Pandang` | 254 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Ulaanbaatar` | 877 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Ulan_Bator` | 877 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Urumqi` | 151 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Ust-Nera` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Vientiane` | 185 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Vladivostok` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Yakutsk` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Yangon` | 254 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Yekaterinburg` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Asia/Yerevan` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Atlantic/Azores` | 3.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Atlantic/Bermuda` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Atlantic/Canary` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Atlantic/Cape_Verde` | 256 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Atlantic/Faeroe` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Atlantic/Faroe` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Atlantic/Jan_Mayen` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Atlantic/Madeira` | 3.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Atlantic/Reykjavik` | 148 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Atlantic/South_Georgia` | 150 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Atlantic/St_Helena` | 148 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Atlantic/Stanley` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Australia/ACT` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Australia/Adelaide` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Australia/Brisbane` | 419 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Australia/Broken_Hill` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Australia/Canberra` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Australia/Currie` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Australia/Darwin` | 325 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Australia/Eucla` | 456 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Australia/Hobart` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Australia/LHI` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Australia/Lindeman` | 475 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Australia/Lord_Howe` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Australia/Melbourne` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Australia/North` | 325 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Australia/NSW` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Australia/Perth` | 446 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Australia/Queensland` | 419 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Australia/South` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Australia/Sydney` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Australia/Tasmania` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Australia/Victoria` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Australia/West` | 446 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Australia/Yancowinna` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Brazil/Acre` | 614 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Brazil/DeNoronha` | 702 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Brazil/East` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Brazil/West` | 590 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Canada/Atlantic` | 3.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Canada/Central` | 2.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Canada/Eastern` | 3.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Canada/Mountain` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Canada/Newfoundland` | 3.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Canada/Pacific` | 2.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Canada/Saskatchewan` | 980 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Canada/Yukon` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/CET` | 2.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Chile/Continental` | 2.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Chile/EasterIsland` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/CST6CDT` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Cuba` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/EET` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Egypt` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Eire` | 3.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/EST` | 182 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/EST5EDT` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Etc/GMT` | 114 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Etc/GMT+0` | 114 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Etc/GMT+1` | 116 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Etc/GMT+10` | 117 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Etc/GMT+11` | 117 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Etc/GMT+12` | 117 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Etc/GMT+2` | 116 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Etc/GMT+3` | 116 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Etc/GMT+4` | 116 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Etc/GMT+5` | 116 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Etc/GMT+6` | 116 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Etc/GMT+7` | 116 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Etc/GMT+8` | 116 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Etc/GMT+9` | 116 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Etc/GMT-0` | 114 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Etc/GMT-1` | 117 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Etc/GMT-10` | 118 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Etc/GMT-11` | 118 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Etc/GMT-12` | 118 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Etc/GMT-13` | 118 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Etc/GMT-14` | 118 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Etc/GMT-2` | 117 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Etc/GMT-3` | 117 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Etc/GMT-4` | 117 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Etc/GMT-5` | 117 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Etc/GMT-6` | 117 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Etc/GMT-7` | 117 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Etc/GMT-8` | 117 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Etc/GMT-9` | 117 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Etc/GMT0` | 114 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Etc/Greenwich` | 114 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Etc/UCT` | 114 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Etc/Universal` | 114 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Etc/UTC` | 114 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Etc/Zulu` | 114 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Amsterdam` | 2.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Andorra` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Astrakhan` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Athens` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Belfast` | 3.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Belgrade` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Berlin` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Bratislava` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Brussels` | 2.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Bucharest` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Budapest` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Busingen` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Chisinau` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Copenhagen` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Dublin` | 3.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Gibraltar` | 3.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Guernsey` | 3.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Helsinki` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Isle_of_Man` | 3.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Istanbul` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Jersey` | 3.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Kaliningrad` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Kiev` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Kirov` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Kyiv` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Lisbon` | 3.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Ljubljana` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/London` | 3.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Luxembourg` | 2.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Madrid` | 2.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Malta` | 2.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Mariehamn` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Minsk` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Monaco` | 2.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Moscow` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Nicosia` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Oslo` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Paris` | 2.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Podgorica` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Prague` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Riga` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Rome` | 2.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Samara` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/San_Marino` | 2.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Sarajevo` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Saratov` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Simferopol` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Skopje` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Sofia` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Stockholm` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Tallinn` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Tirane` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Tiraspol` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Ulyanovsk` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Uzhgorod` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Vaduz` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Vatican` | 2.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Vienna` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Vilnius` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Volgograd` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Warsaw` | 2.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Zagreb` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Zaporozhye` | 2.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Europe/Zurich` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Factory` | 116 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/GB` | 3.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/GB-Eire` | 3.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/GMT` | 114 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/GMT+0` | 114 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/GMT-0` | 114 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/GMT0` | 114 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Greenwich` | 114 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Hongkong` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/HST` | 329 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Iceland` | 148 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Indian/Antananarivo` | 265 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Indian/Chagos` | 185 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Indian/Christmas` | 185 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Indian/Cocos` | 254 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Indian/Comoro` | 265 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Indian/Kerguelen` | 185 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Indian/Mahe` | 151 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Indian/Maldives` | 185 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Indian/Mauritius` | 227 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Indian/Mayotte` | 265 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Indian/Reunion` | 151 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Iran` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/iso3166.tab` | 4.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Israel` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Jamaica` | 482 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Japan` | 309 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Kwajalein` | 302 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/leapseconds` | 3.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Libya` | 625 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/MET` | 2.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Mexico/BajaNorte` | 2.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Mexico/BajaSur` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Mexico/General` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/MST` | 360 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/MST7MDT` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Navajo` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/NZ` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/NZ-CHAT` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Apia` | 598 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Auckland` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Bougainville` | 254 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Chatham` | 2.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Chuuk` | 172 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Easter` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Efate` | 524 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Enderbury` | 220 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Fakaofo` | 186 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Fiji` | 564 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Funafuti` | 152 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Galapagos` | 224 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Gambier` | 150 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Guadalcanal` | 152 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Guam` | 494 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Honolulu` | 329 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Johnston` | 329 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Kanton` | 220 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Kiritimati` | 224 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Kosrae` | 337 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Kwajalein` | 302 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Majuro` | 152 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Marquesas` | 159 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Midway` | 175 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Nauru` | 238 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Niue` | 189 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Norfolk` | 866 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Noumea` | 290 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Pago_Pago` | 175 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Palau` | 166 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Pitcairn` | 188 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Pohnpei` | 152 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Ponape` | 152 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Port_Moresby` | 172 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Rarotonga` | 589 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Saipan` | 494 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Samoa` | 175 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Tahiti` | 151 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Tarawa` | 152 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Tongatapu` | 358 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Truk` | 172 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Wake` | 152 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Wallis` | 152 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Pacific/Yap` | 172 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Poland` | 2.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Portugal` | 3.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/PRC` | 561 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/PST8PDT` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/ROC` | 761 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/ROK` | 617 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Singapore` | 401 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Turkey` | 1.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/tzdata.zi` | 102.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/UCT` | 114 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Universal` | 114 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/US/Alaska` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/US/Aleutian` | 2.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/US/Arizona` | 360 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/US/Central` | 3.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/US/East-Indiana` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/US/Eastern` | 3.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/US/Hawaii` | 329 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/US/Indiana-Starke` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/US/Michigan` | 2.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/US/Mountain` | 2.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/US/Pacific` | 2.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/US/Samoa` | 175 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/UTC` | 114 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/W-SU` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/WET` | 3.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/zone.tab` | 18.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/zone1970.tab` | 17.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/zonenow.tab` | 8.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz/zoneinfo/Zulu` | 114 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz-2026.5.dist-info/INSTALLER` | 4 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz-2026.5.dist-info/LICENSE.txt` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz-2026.5.dist-info/METADATA` | 22.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz-2026.5.dist-info/RECORD` | 51.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/pytz-2026.5.dist-info/top_level.txt` | 5 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz-2026.5.dist-info/WHEEL` | 110 B |
| `.venv_c_mirror_backup/Lib/site-packages/pytz-2026.5.dist-info/zip-safe` | 1 B |
| `.venv_c_mirror_backup/Lib/site-packages/six-1.17.0.dist-info/INSTALLER` | 4 B |
| `.venv_c_mirror_backup/Lib/site-packages/six-1.17.0.dist-info/LICENSE` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/six-1.17.0.dist-info/METADATA` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/six-1.17.0.dist-info/RECORD` | 561 B |
| `.venv_c_mirror_backup/Lib/site-packages/six-1.17.0.dist-info/top_level.txt` | 4 B |
| `.venv_c_mirror_backup/Lib/site-packages/six-1.17.0.dist-info/WHEEL` | 109 B |
| `.venv_c_mirror_backup/Lib/site-packages/six.py` | 33.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/__init__.py` | 252 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Abidjan` | 130 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Accra` | 130 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Addis_Ababa` | 191 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Algiers` | 470 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Asmara` | 191 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Asmera` | 191 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Bamako` | 130 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Bangui` | 180 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Banjul` | 130 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Bissau` | 149 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Blantyre` | 131 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Brazzaville` | 180 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Bujumbura` | 131 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Cairo` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Casablanca` | 793 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Ceuta` | 562 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Conakry` | 130 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Dakar` | 130 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Dar_es_Salaam` | 191 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Djibouti` | 191 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Douala` | 180 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/El_Aaiun` | 704 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Freetown` | 130 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Gaborone` | 131 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Harare` | 131 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Johannesburg` | 190 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Juba` | 458 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Kampala` | 191 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Khartoum` | 458 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Kigali` | 131 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Kinshasa` | 180 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Lagos` | 180 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Libreville` | 180 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Lome` | 130 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Luanda` | 180 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Lubumbashi` | 131 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Lusaka` | 131 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Malabo` | 180 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Maputo` | 131 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Maseru` | 190 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Mbabane` | 190 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Mogadishu` | 191 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Monrovia` | 164 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Nairobi` | 191 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Ndjamena` | 160 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Niamey` | 180 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Nouakchott` | 130 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Ouagadougou` | 130 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Porto-Novo` | 180 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Sao_Tome` | 173 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Timbuktu` | 130 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Tripoli` | 431 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Tunis` | 449 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Africa/Windhoek` | 638 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Adak` | 969 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Anchorage` | 977 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Anguilla` | 177 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Antigua` | 177 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Araguaina` | 592 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Argentina/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Argentina/Buenos_Aires` | 708 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Argentina/Catamarca` | 708 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Argentina/ComodRivadavia` | 708 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Argentina/Cordoba` | 708 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Argentina/Jujuy` | 690 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Argentina/La_Rioja` | 717 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Argentina/Mendoza` | 708 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Argentina/Rio_Gallegos` | 708 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Argentina/Salta` | 690 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Argentina/San_Juan` | 717 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Argentina/San_Luis` | 717 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Argentina/Tucuman` | 726 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Argentina/Ushuaia` | 708 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Aruba` | 177 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Asuncion` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Atikokan` | 149 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Atka` | 969 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Bahia` | 682 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Bahia_Banderas` | 700 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Barbados` | 278 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Belem` | 394 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Belize` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Blanc-Sablon` | 177 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Boa_Vista` | 430 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Bogota` | 179 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Boise` | 999 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Buenos_Aires` | 708 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Cambridge_Bay` | 883 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Campo_Grande` | 952 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Cancun` | 538 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Caracas` | 190 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Catamarca` | 708 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Cayenne` | 151 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Cayman` | 149 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Chicago` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Chihuahua` | 691 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Ciudad_Juarez` | 718 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Coral_Harbour` | 149 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Cordoba` | 708 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Costa_Rica` | 232 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Coyhaique` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Creston` | 240 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Cuiaba` | 934 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Curacao` | 177 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Danmarkshavn` | 447 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Dawson` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Dawson_Creek` | 683 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Denver` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Detroit` | 899 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Dominica` | 177 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Edmonton` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Eirunepe` | 436 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/El_Salvador` | 176 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Ensenada` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Fort_Nelson` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Fort_Wayne` | 531 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Fortaleza` | 484 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Glace_Bay` | 880 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Godthab` | 965 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Goose_Bay` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Grand_Turk` | 853 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Grenada` | 177 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Guadeloupe` | 177 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Guatemala` | 212 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Guayaquil` | 179 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Guyana` | 181 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Halifax` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Havana` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Hermosillo` | 258 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Indiana/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Indiana/Indianapolis` | 531 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Indiana/Knox` | 1016 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Indiana/Marengo` | 567 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Indiana/Petersburg` | 683 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Indiana/Tell_City` | 522 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Indiana/Vevay` | 369 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Indiana/Vincennes` | 558 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Indiana/Winamac` | 603 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Indianapolis` | 531 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Inuvik` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Iqaluit` | 855 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Jamaica` | 339 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Jujuy` | 690 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Juneau` | 966 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Kentucky/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Kentucky/Louisville` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Kentucky/Monticello` | 972 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Knox_IN` | 1016 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Kralendijk` | 177 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/La_Paz` | 170 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Lima` | 283 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Los_Angeles` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Louisville` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Lower_Princes` | 177 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Maceio` | 502 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Managua` | 295 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Manaus` | 412 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Marigot` | 177 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Martinique` | 178 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Matamoros` | 437 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Mazatlan` | 690 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Mendoza` | 708 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Menominee` | 917 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Merida` | 654 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Metlakatla` | 586 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Mexico_City` | 773 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Miquelon` | 550 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Moncton` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Monterrey` | 709 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Montevideo` | 969 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Montreal` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Montserrat` | 177 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Nassau` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/New_York` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Nipigon` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Nome` | 975 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Noronha` | 484 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/North_Dakota/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/North_Dakota/Beulah` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/North_Dakota/Center` | 990 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/North_Dakota/New_Salem` | 990 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Nuuk` | 965 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Ojinaga` | 718 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Panama` | 149 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Pangnirtung` | 855 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Paramaribo` | 187 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Phoenix` | 240 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Port-au-Prince` | 565 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Port_of_Spain` | 177 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Porto_Acre` | 418 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Porto_Velho` | 394 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Puerto_Rico` | 177 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Punta_Arenas` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Rainy_River` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Rankin_Inlet` | 807 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Recife` | 484 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Regina` | 638 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Resolute` | 807 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Rio_Branco` | 418 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Rosario` | 708 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Santa_Isabel` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Santarem` | 409 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Santiago` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Santo_Domingo` | 317 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Sao_Paulo` | 952 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Scoresbysund` | 984 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Shiprock` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Sitka` | 956 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/St_Barthelemy` | 177 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/St_Johns` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/St_Kitts` | 177 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/St_Lucia` | 177 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/St_Thomas` | 177 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/St_Vincent` | 177 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Swift_Current` | 368 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Tegucigalpa` | 194 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Thule` | 455 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Thunder_Bay` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Tijuana` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Toronto` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Tortola` | 177 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Vancouver` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Virgin` | 177 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Whitehorse` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Winnipeg` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Yakutat` | 946 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/America/Yellowknife` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Antarctica/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Antarctica/Casey` | 287 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Antarctica/Davis` | 197 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Antarctica/DumontDUrville` | 154 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Antarctica/Macquarie` | 976 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Antarctica/Mawson` | 152 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Antarctica/McMurdo` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Antarctica/Palmer` | 887 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Antarctica/Rothera` | 132 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Antarctica/South_Pole` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Antarctica/Syowa` | 133 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Antarctica/Troll` | 158 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Antarctica/Vostok` | 170 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Arctic/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Arctic/Longyearbyen` | 705 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Aden` | 133 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Almaty` | 618 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Amman` | 928 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Anadyr` | 743 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Aqtau` | 606 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Aqtobe` | 615 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Ashgabat` | 375 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Ashkhabad` | 375 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Atyrau` | 616 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Baghdad` | 630 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Bahrain` | 152 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Baku` | 744 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Bangkok` | 152 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Barnaul` | 753 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Beirut` | 732 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Bishkek` | 618 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Brunei` | 320 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Calcutta` | 220 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Chita` | 750 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Choibalsan` | 594 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Chongqing` | 393 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Chungking` | 393 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Colombo` | 247 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Dacca` | 231 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Damascus` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Dhaka` | 231 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Dili` | 170 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Dubai` | 133 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Dushanbe` | 366 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Famagusta` | 940 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Gaza` | 2.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Harbin` | 393 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Hebron` | 2.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Ho_Chi_Minh` | 232 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Hong_Kong` | 775 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Hovd` | 594 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Irkutsk` | 760 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Istanbul` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Jakarta` | 248 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Jayapura` | 171 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Jerusalem` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Kabul` | 159 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Kamchatka` | 727 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Karachi` | 266 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Kashgar` | 133 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Kathmandu` | 161 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Katmandu` | 161 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Khandyga` | 775 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Kolkata` | 220 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Krasnoyarsk` | 741 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Kuala_Lumpur` | 256 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Kuching` | 320 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Kuwait` | 133 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Macao` | 791 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Macau` | 791 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Magadan` | 751 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Makassar` | 190 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Manila` | 274 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Muscat` | 133 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Nicosia` | 597 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Novokuznetsk` | 726 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Novosibirsk` | 753 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Omsk` | 741 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Oral` | 625 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Phnom_Penh` | 152 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Pontianak` | 247 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Pyongyang` | 183 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Qatar` | 152 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Qostanay` | 624 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Qyzylorda` | 624 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Rangoon` | 187 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Riyadh` | 133 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Saigon` | 232 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Sakhalin` | 755 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Samarkand` | 366 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Seoul` | 415 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Shanghai` | 393 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Singapore` | 256 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Srednekolymsk` | 742 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Taipei` | 511 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Tashkent` | 366 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Tbilisi` | 620 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Tehran` | 812 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Tel_Aviv` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Thimbu` | 154 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Thimphu` | 154 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Tokyo` | 213 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Tomsk` | 753 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Ujung_Pandang` | 190 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Ulaanbaatar` | 594 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Ulan_Bator` | 594 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Urumqi` | 133 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Ust-Nera` | 771 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Vientiane` | 152 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Vladivostok` | 742 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Yakutsk` | 741 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Yangon` | 187 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Yekaterinburg` | 760 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Asia/Yerevan` | 708 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Atlantic/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Atlantic/Azores` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Atlantic/Bermuda` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Atlantic/Canary` | 478 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Atlantic/Cape_Verde` | 175 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Atlantic/Faeroe` | 441 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Atlantic/Faroe` | 441 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Atlantic/Jan_Mayen` | 705 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Atlantic/Madeira` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Atlantic/Reykjavik` | 130 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Atlantic/South_Georgia` | 132 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Atlantic/St_Helena` | 130 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Atlantic/Stanley` | 789 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Australia/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Australia/ACT` | 904 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Australia/Adelaide` | 921 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Australia/Brisbane` | 289 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Australia/Broken_Hill` | 941 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Australia/Canberra` | 904 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Australia/Currie` | 1003 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Australia/Darwin` | 234 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Australia/Eucla` | 314 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Australia/Hobart` | 1003 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Australia/LHI` | 692 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Australia/Lindeman` | 325 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Australia/Lord_Howe` | 692 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Australia/Melbourne` | 904 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Australia/North` | 234 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Australia/NSW` | 904 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Australia/Perth` | 306 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Australia/Queensland` | 289 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Australia/South` | 921 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Australia/Sydney` | 904 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Australia/Tasmania` | 1003 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Australia/Victoria` | 904 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Australia/West` | 306 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Australia/Yancowinna` | 941 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Brazil/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Brazil/Acre` | 418 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Brazil/DeNoronha` | 484 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Brazil/East` | 952 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Brazil/West` | 412 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Canada/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Canada/Atlantic` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Canada/Central` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Canada/Eastern` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Canada/Mountain` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Canada/Newfoundland` | 1.8 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Canada/Pacific` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Canada/Saskatchewan` | 638 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Canada/Yukon` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/CET` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Chile/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Chile/Continental` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Chile/EasterIsland` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/CST6CDT` | 922 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Cuba` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/EET` | 682 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Egypt` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Eire` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/EST` | 149 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/EST5EDT` | 922 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Etc/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Etc/GMT` | 111 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Etc/GMT+0` | 111 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Etc/GMT+1` | 113 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Etc/GMT+10` | 114 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Etc/GMT+11` | 114 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Etc/GMT+12` | 114 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Etc/GMT+2` | 113 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Etc/GMT+3` | 113 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Etc/GMT+4` | 113 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Etc/GMT+5` | 113 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Etc/GMT+6` | 113 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Etc/GMT+7` | 113 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Etc/GMT+8` | 113 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Etc/GMT+9` | 113 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Etc/GMT-0` | 111 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Etc/GMT-1` | 114 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Etc/GMT-10` | 115 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Etc/GMT-11` | 115 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Etc/GMT-12` | 115 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Etc/GMT-13` | 115 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Etc/GMT-14` | 115 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Etc/GMT-2` | 114 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Etc/GMT-3` | 114 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Etc/GMT-4` | 114 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Etc/GMT-5` | 114 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Etc/GMT-6` | 114 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Etc/GMT-7` | 114 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Etc/GMT-8` | 114 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Etc/GMT-9` | 114 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Etc/GMT0` | 111 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Etc/Greenwich` | 111 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Etc/UCT` | 111 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Etc/Universal` | 111 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Etc/UTC` | 111 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Etc/Zulu` | 111 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Amsterdam` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Andorra` | 389 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Astrakhan` | 726 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Athens` | 682 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Belfast` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Belgrade` | 478 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Berlin` | 705 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Bratislava` | 723 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Brussels` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Bucharest` | 661 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Budapest` | 766 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Busingen` | 497 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Chisinau` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Copenhagen` | 705 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Dublin` | 1.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Gibraltar` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Guernsey` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Helsinki` | 481 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Isle_of_Man` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Istanbul` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Jersey` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Kaliningrad` | 904 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Kiev` | 558 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Kirov` | 735 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Kyiv` | 558 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Lisbon` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Ljubljana` | 478 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/London` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Luxembourg` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Madrid` | 897 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Malta` | 928 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Mariehamn` | 481 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Minsk` | 808 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Monaco` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Moscow` | 908 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Nicosia` | 597 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Oslo` | 705 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Paris` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Podgorica` | 478 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Prague` | 723 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Riga` | 694 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Rome` | 947 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Samara` | 732 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/San_Marino` | 947 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Sarajevo` | 478 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Saratov` | 726 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Simferopol` | 865 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Skopje` | 478 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Sofia` | 592 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Stockholm` | 705 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Tallinn` | 675 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Tirane` | 604 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Tiraspol` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Ulyanovsk` | 760 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Uzhgorod` | 558 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Vaduz` | 497 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Vatican` | 947 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Vienna` | 658 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Vilnius` | 676 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Volgograd` | 753 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Warsaw` | 923 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Zagreb` | 478 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Zaporozhye` | 558 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Europe/Zurich` | 497 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Factory` | 113 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/GB` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/GB-Eire` | 1.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/GMT` | 111 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/GMT+0` | 111 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/GMT-0` | 111 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/GMT0` | 111 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Greenwich` | 111 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Hongkong` | 775 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/HST` | 221 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Iceland` | 130 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Indian/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Indian/Antananarivo` | 191 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Indian/Chagos` | 152 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Indian/Christmas` | 152 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Indian/Cocos` | 187 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Indian/Comoro` | 191 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Indian/Kerguelen` | 152 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Indian/Mahe` | 133 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Indian/Maldives` | 152 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Indian/Mauritius` | 179 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Indian/Mayotte` | 191 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Indian/Reunion` | 133 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Iran` | 812 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/iso3166.tab` | 4.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Israel` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Jamaica` | 339 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Japan` | 213 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Kwajalein` | 219 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/leapseconds` | 3.6 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Libya` | 431 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/MET` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Mexico/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Mexico/BajaNorte` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Mexico/BajaSur` | 690 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Mexico/General` | 773 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/MST` | 240 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/MST7MDT` | 922 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Navajo` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/NZ` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/NZ-CHAT` | 808 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Apia` | 407 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Auckland` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Bougainville` | 201 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Chatham` | 808 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Chuuk` | 154 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Easter` | 1.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Efate` | 342 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Enderbury` | 172 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Fakaofo` | 153 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Fiji` | 396 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Funafuti` | 134 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Galapagos` | 175 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Gambier` | 132 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Guadalcanal` | 134 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Guam` | 350 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Honolulu` | 221 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Johnston` | 221 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Kanton` | 172 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Kiritimati` | 174 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Kosrae` | 242 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Kwajalein` | 219 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Majuro` | 134 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Marquesas` | 139 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Midway` | 146 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Nauru` | 183 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Niue` | 154 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Norfolk` | 237 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Noumea` | 198 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Pago_Pago` | 146 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Palau` | 148 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Pitcairn` | 153 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Pohnpei` | 134 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Ponape` | 134 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Port_Moresby` | 154 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Rarotonga` | 406 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Saipan` | 350 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Samoa` | 146 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Tahiti` | 133 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Tarawa` | 134 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Tongatapu` | 237 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Truk` | 154 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Wake` | 134 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Wallis` | 134 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Pacific/Yap` | 154 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Poland` | 923 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Portugal` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/PRC` | 393 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/PST8PDT` | 922 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/ROC` | 511 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/ROK` | 415 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Singapore` | 256 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Turkey` | 1.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/tzdata.zi` | 102.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/UCT` | 111 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Universal` | 111 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/US/__init__.py` | 0 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/US/Alaska` | 977 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/US/Aleutian` | 969 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/US/Arizona` | 240 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/US/Central` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/US/East-Indiana` | 531 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/US/Eastern` | 1.7 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/US/Hawaii` | 221 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/US/Indiana-Starke` | 1016 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/US/Michigan` | 899 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/US/Mountain` | 1.0 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/US/Pacific` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/US/Samoa` | 146 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/UTC` | 111 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/W-SU` | 908 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/WET` | 1.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/zone.tab` | 18.4 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/zone1970.tab` | 17.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/zonenow.tab` | 8.2 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zoneinfo/Zulu` | 111 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata/zones` | 8.9 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata-2026.5.dist-info/INSTALLER` | 4 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata-2026.5.dist-info/licenses/LICENSE` | 625 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata-2026.5.dist-info/licenses/licenses/LICENSE_APACHE` | 11.1 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata-2026.5.dist-info/METADATA` | 1.3 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata-2026.5.dist-info/RECORD` | 55.5 KB |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata-2026.5.dist-info/top_level.txt` | 7 B |
| `.venv_c_mirror_backup/Lib/site-packages/tzdata-2026.5.dist-info/WHEEL` | 109 B |
| `.venv_c_mirror_backup/pyvenv.cfg` | 323 B |
| `.venv_c_mirror_backup/Scripts/activate` | 2.1 KB |
| `.venv_c_mirror_backup/Scripts/activate.bat` | 999 B |
| `.venv_c_mirror_backup/Scripts/activate.fish` | 2.1 KB |
| `.venv_c_mirror_backup/Scripts/Activate.ps1` | 8.8 KB |
| `.venv_c_mirror_backup/Scripts/deactivate.bat` | 393 B |
| `.venv_c_mirror_backup/Scripts/f2py.exe` | 105.8 KB |
| `.venv_c_mirror_backup/Scripts/numpy-config.exe` | 105.8 KB |
| `.venv_c_mirror_backup/Scripts/pip.exe` | 105.8 KB |
| `.venv_c_mirror_backup/Scripts/pip3.13.exe` | 105.8 KB |
| `.venv_c_mirror_backup/Scripts/pip3.exe` | 105.8 KB |
| `.venv_c_mirror_backup/Scripts/python.exe` | 235.5 KB |
| `.venv_c_mirror_backup/Scripts/pythonw.exe` | 231.5 KB |
| `config/physics_concepts_100_catalog.json` | 12.5 KB |
| `config/physics_v2_schema.json` | 3.8 KB |
| `config/settings.json` | 923 B |
| `data/interim/physics_concepts_v2_modelraw.jsonl` | 6.0 KB |
| `data/interim/prompt_variant_v1.jsonl` | 3.4 KB |
| `data/interim/prompt_variant_v2.jsonl` | 3.5 KB |
| `data/interim/sample_records.jsonl` | 5.0 KB |
| `data/processed/physics_concepts_v2.jsonl` | 3.5 KB |
| `data/processed/sample_records.parquet` | 9.2 KB |
| `data/raw/README_DO_NOT_OVERWRITE.txt` | 1.1 KB |
| `docs/STAGE1_NOTES.md` | 3.6 KB |
| `logs/jsonl_to_parquet.log` | 1.5 KB |
| `logs/make_sample_data.log` | 856 B |
| `logs/openscigraph.log` | 1.4 KB |
| `logs/physics_v2.log` | 12.2 KB |
| `logs/run_stage1_tests.log` | 2.2 KB |
| `README.md` | 5.5 KB |
| `reports/initial_test_report.md` | 13.6 KB |
| `reports/jsonl_check_20261012T074410Z.json` | 2.5 KB |
| `reports/jsonl_check_20261012T082656Z.json` | 2.5 KB |
| `reports/jsonl_check_stage1.json` | 2.5 KB |
| `reports/migration_final_report.md` | 9.8 KB |
| `reports/migration_integrity_report.md` | 4.0 KB |
| `reports/migration_precheck_report.md` | 4.6 KB |
| `reports/migration_runtime_test_report.md` | 11.1 KB |
| `reports/parquet_export_20261012T075331Z.json` | 2.5 KB |
| `reports/parquet_export_20261012T082657Z.json` | 2.5 KB |
| `reports/parquet_export_stage1.json` | 2.5 KB |
| `reports/physics_v2_run_20261014T102628Z.json` | 4.4 KB |
| `reports/physics_v2_run_20261014T102709Z.json` | 4.4 KB |
| `reports/physics_v2_run_20261014T102748Z.json` | 4.5 KB |
| `reports/physics_v2_run_20261014T102859Z.json` | 6.2 KB |
| `requirements.txt` | 1.3 KB |
| `scripts/clean_physics_v2.py` | 31.8 KB |
| `src/__init__.py` | 168 B |
| `src/check_jsonl.py` | 13.3 KB |
| `src/common.py` | 12.1 KB |
| `src/jsonl_to_parquet.py` | 11.7 KB |
| `src/make_sample_data.py` | 9.2 KB |
| `tests/__init__.py` | 69 B |
| `tests/run_stage1_tests.py` | 19.3 KB |
| `tests/test_pipeline.py` | 9.5 KB |

## 7. 已知限制与未做的事

- 本阶段 **未** 下载任何 Wikidata / Wikipedia 数据，`data/raw/` 目前仅含保护说明文件。
- 本阶段 **未** 调用任何收费 API，也 **未** 上传任何本地文件。
- `data/raw/` 被硬性保护：脚本向其写入会直接抛出 `PermissionError`（已由单元测试验证）。
- 合成测试数据仅用于验证管道，不代表真实知识图谱分布。
- 尚未定义真实数据源的字段映射与许可审核流程（留待后续阶段）。

## 8. 下一步（需你确认后才执行）

1. 确认阶段一产出是否符合预期。
2. 明确第二阶段的数据来源与使用许可，再决定是否接入真实数据。
3. 若来源许可不明，将先产出待审核报告，绝不进入发布环节。
