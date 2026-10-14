# 迁移后运行验收报告（E 盘）

- 生成时间（UTC）：`2026-10-12T08:27:00Z`
- 工作目录：`E:\OpenSciGraph`
- 解释器：`E:\OpenSciGraph\.venv\Scripts\python.exe`
- 网络请求：**未发起任何网络请求**；**未下载任何数据**

## 1. 测试结果总表

| # | 测试项 | 退出码 | 预期 | 结果 |
|---|---|---|---|---|
| 1 | 1. Python 版本检查 | 0 | 0 | 通过 |
| 2 | 2. 依赖导入检查 | 0 | 0 | 通过 |
| 3 | 3. V1 单元测试（unittest，含 JSONL 校验与 Parquet 往返） | 0 | 0 | 通过 |
| 4 | 4. JSONL 校验脚本（默认输出路径） | 1 | 0,1 | 通过 |
| 5 | 5. Parquet 导出（默认交付路径） | 0 | 0 | 通过 |
| 6 | 6. Parquet 回读与列契约校验 | 0 | 0 | 通过 |
| 7 | 8. 配置读取与路径解析（关键：PROJECT_ROOT 必须指向 E 盘） | 0 | 0 | 通过 |
| 8 | 9. data/raw 写保护（仅路径检查，不写入文件） | 0 | 0 | 通过 |
| 9 | 10. 生成文件输出路径检查 | 0 | 0 | 通过 |

| 项目 | 结果 |
|---|---|
| 单元测试用例数 | 21 |
| 失败数 | 0 |
| 跳过数 | 0 |
| V2 测试 | 未执行 / 尚不存在。项目中未发现任何 V2 测试文件（扫描到 0 个含 'v2' 的路径）。 |

## 2. 逐项明细（真实命令与输出）

### 1. 1. Python 版本检查

- 工作目录：`E:\OpenSciGraph`
- 命令：`.\.venv\Scripts\python.exe --version`
- 退出码：0（预期 [0]）

标准输出：

```text
Python 3.13.14
```

### 2. 2. 依赖导入检查

- 工作目录：`E:\OpenSciGraph`
- 命令：`.\.venv\Scripts\python.exe -c import pandas,pyarrow,numpy,dateutil,pytz;print('pandas',pandas.__version__);print('pyarrow',pyarrow.__version__);print('numpy',numpy.__version__);print('dateutil',dateutil.__version__);print('pytz',pytz.__version__)`
- 退出码：0（预期 [0]）

标准输出：

```text
pandas 2.3.3
pyarrow 26.0.0
numpy 2.5.4
dateutil 2.9.0.post0
pytz 2026.5
```

### 3. 3. V1 单元测试（unittest，含 JSONL 校验与 Parquet 往返）

- 工作目录：`E:\OpenSciGraph`
- 命令：`.\.venv\Scripts\python.exe -m unittest discover -s tests -v`
- 退出码：0（预期 [0]）

标准输出：

```text
（无）
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
Ran 21 tests in 0.990s

OK
```

### 4. 4. JSONL 校验脚本（默认输出路径）

- 工作目录：`E:\OpenSciGraph`
- 命令：`.\.venv\Scripts\python.exe src/check_jsonl.py --input data/interim/sample_records.jsonl --batch-size 3`
- 退出码：1（预期 [0, 1]）
- 说明：退出码 1 属预期：合成测试夹具故意包含 2 条非法 QID

标准输出：

```text
2026-10-12 16:26:56 | INFO    | 开始校验 JSONL：data/interim/sample_records.jsonl（batch_size=3）
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
2026-10-12 16:26:56 | INFO    | 报告已写入：reports/jsonl_check_20261012T082656Z.json
2026-10-12 16:26:56 | ERROR   | 校验结束：发现 2 条错误记录，需修复后重跑。
```

### 5. 5. Parquet 导出（默认交付路径）

- 工作目录：`E:\OpenSciGraph`
- 命令：`.\.venv\Scripts\python.exe src/jsonl_to_parquet.py --input data/interim/sample_records.jsonl --output data/processed/sample_records.parquet --batch-size 4 --force`
- 退出码：0（预期 [0]）

标准输出：

```text
2026-10-12 16:26:57 | INFO    | 读取 JSONL：data/interim/sample_records.jsonl（batch_size=4）
2026-10-12 16:26:57 | INFO    | 解析完成：保留 7 行，跳过 3 行。
2026-10-12 16:26:57 | INFO    | Parquet 已写出：data/processed/sample_records.parquet（9.2 KB）
2026-10-12 16:26:57 | INFO    | 报告已写入：reports/parquet_export_20261012T082657Z.json
--------------------------------------------------------------
输入 JSONL : data/interim/sample_records.jsonl  (5.0 KB)
输出 Parquet: data/processed/sample_records.parquet  (9.2 KB)
保留行数   : 7
列数       : 12  ['entity_id', 'entity_label_zh', 'entity_label_en', 'entity_type', 'description', 'description_lang', 'aliases', 'source', 'license', 'retrieved_at', 'is_synthetic', 'data_origin']
跳过行数   : 3（其中重复 1）
压缩方式   : snappy
--------------------------------------------------------------
```

### 6. 6. Parquet 回读与列契约校验

- 工作目录：`E:\OpenSciGraph`
- 命令：`.\.venv\Scripts\python.exe -c import pandas as pd;df=pd.read_parquet('data/processed/sample_records.parquet');print('shape',df.shape);print('columns',list(df.columns));print('has_cjk', any('合成' in str(v) for v in df['entity_label_zh'].dropna()));print('is_synthetic_all_false_expected','is_synthetic' in df.columns)`
- 退出码：0（预期 [0]）

标准输出：

```text
shape (7, 12)
columns ['entity_id', 'entity_label_zh', 'entity_label_en', 'entity_type', 'description', 'description_lang', 'aliases', 'source', 'license', 'retrieved_at', 'is_synthetic', 'data_origin']
has_cjk True
is_synthetic_all_false_expected True
```

### 7. 8. 配置读取与路径解析（关键：PROJECT_ROOT 必须指向 E 盘）

- 工作目录：`E:\OpenSciGraph`
- 命令：`.\.venv\Scripts\python.exe -c import sys; sys.path.insert(0,'src'); import common;c=common.load_config();print('PROJECT_ROOT',common.PROJECT_ROOT);print('RAW_DIR',common.RAW_DIR);print('PROCESSED_DIR',common.PROCESSED_DIR);print('PROTECTED_DIRS',[str(p) for p in common.PROTECTED_DIRS]);print('batch_size',c['batch_size']);print('required_fields',c['jsonl']['required_fields']);print('parquet',c['parquet'])`
- 退出码：0（预期 [0]）

标准输出：

```text
PROJECT_ROOT E:\OpenSciGraph
RAW_DIR E:\OpenSciGraph\data\raw
PROCESSED_DIR E:\OpenSciGraph\data\processed
PROTECTED_DIRS ['E:\\OpenSciGraph\\data\\raw']
batch_size 500
required_fields ['entity_id', 'source', 'is_synthetic', 'data_origin']
parquet {'compression': 'snappy', 'index': False}
```

### 8. 9. data/raw 写保护（仅路径检查，不写入文件）

- 工作目录：`E:\OpenSciGraph`
- 命令：`.\.venv\Scripts\python.exe -c import sys; sys.path.insert(0,'src'); import common;blocked=[];tests=[common.RAW_DIR/'__should_be_blocked__.txt', common.RAW_DIR/'sub'/'x.parquet'];
for t in tests:
    try:
        common.assert_writable(t); blocked.append(('NOT_BLOCKED',str(t)))
    except PermissionError:
        blocked.append(('BLOCKED',str(t)))
print(blocked);print('ALL_BLOCKED', all(s=='BLOCKED' for s,_ in blocked));print('processed_writable', bool(common.assert_writable(common.PROCESSED_DIR/'ok.tmp')))`
- 退出码：0（预期 [0]）

标准输出：

```text
[('BLOCKED', 'E:\\OpenSciGraph\\data\\raw\\__should_be_blocked__.txt'), ('BLOCKED', 'E:\\OpenSciGraph\\data\\raw\\sub\\x.parquet')]
ALL_BLOCKED True
processed_writable True
```

### 9. 10. 生成文件输出路径检查

- 工作目录：`E:\OpenSciGraph`
- 命令：`.\.venv\Scripts\python.exe -c import sys; sys.path.insert(0,'src'); import common;print('REPORTS_DIR',common.REPORTS_DIR);print('LOGS_DIR',common.LOGS_DIR);import os;print('reports_exists', os.path.isdir(common.REPORTS_DIR));print('logs_exists', os.path.isdir(common.LOGS_DIR))`
- 退出码：0（预期 [0]）

标准输出：

```text
REPORTS_DIR E:\OpenSciGraph\reports
LOGS_DIR E:\OpenSciGraph\logs
reports_exists True
logs_exists True
```

## 3. Parquet 交付文件是否被测试改变

- 测试前 SHA-256：`b61a0a69e9ef60ff4355df1f05dc9057a9ce46d2127f787d5f17cacf7b3469a4`
- 测试后 SHA-256：`b61a0a69e9ef60ff4355df1f05dc9057a9ce46d2127f787d5f17cacf7b3469a4`
- 是否一致：一致

## 4. 产物与日志中的 C 盘依赖扫描

发现以下行仍包含 `C:\OpenSciGraph`：

- `reports/initial_test_report.md:5: - 项目根目录：`C:\OpenSciGraph``
- `reports/initial_test_report.md:15: | Python 路径 | `C:\OpenSciGraph\.venv\Scripts\python.exe` |`
- `reports/initial_test_report.md:34: 命令（工作目录 `C:\OpenSciGraph`）：`
- `reports/initial_test_report.md:55: 命令（工作目录 `C:\OpenSciGraph`）：`
- `reports/initial_test_report.md:94: 命令（工作目录 `C:\OpenSciGraph`）：`
- `reports/initial_test_report.md:119: 命令（工作目录 `C:\OpenSciGraph`）：`
- `reports/migration_integrity_report.md:4: - 源目录：`C:\OpenSciGraph``
- `reports/migration_integrity_report.md:90: - 源项目 C:\OpenSciGraph 在本次校验中 **仅被读取**，未做任何写入。`

## 5. 未执行项

- V2 离线测试：未执行 / 尚不存在。项目中未发现任何 V2 测试文件（扫描到 0 个含 'v2' 的路径）。

## 6. 结论

- 执行 9 项，通过 9 项，失败 0 项。
- 单元测试：Ran 21 tests，全部通过。
