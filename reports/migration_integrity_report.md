# 迁移完整性校验报告

- 生成时间（UTC）：`2026-10-12T08:23:36Z`
- 源目录：`C:\OpenSciGraph`
- 目标目录：`E:\OpenSciGraph`
- 校验方式：相对路径集合 + 字节数 + SHA-256 逐文件比对

## 0. 事先声明的忽略项

以下文件为本次迁移新建的报告产物，源项目中本不存在，因此不计入差异：

- `reports/migration_final_report.md` （尚未生成）
- `reports/migration_integrity_report.md` （尚未生成）
- `reports/migration_precheck_report.md` （尚未生成）
- `reports/migration_runtime_test_report.md` （尚未生成）

**未忽略任何业务文件或数据文件。**

## 1. 汇总

| 校验项 | 源 (C:) | 目标 (E:) | 结果 |
|---|---|---|---|
| 普通文件数 | 7428 | 7428 | 一致 |
| 目录数 | 755 | 755 | 一致 |
| 符号链接数 | 0 | 0 | 一致 |
| 仅存在于源的文件 | 0 | — | 通过 |
| 仅存在于目标的文件 | — | 0 | 通过 |
| 仅存在于源的目录 | 0 | — | 通过 |
| 仅存在于目标的目录 | — | 0 | 通过 |
| 字节数不一致 | 0 | 0 | 通过 |
| SHA-256 不一致 | 0 | 0 | 通过 |
| 关键文件全部匹配 | — | — | 通过 |

### 总体结论：**通过**

## 2. 差异明细

**无任何差异。**

## 3. 关键文件哈希

| 文件 | 字节 | 源 SHA-256 | 目标 SHA-256 | 结果 |
|---|---|---|---|---|
| `config/settings.json` | 923 | `c5888cfce874cd48…` | `c5888cfce874cd48…` | 一致 |
| `src/common.py` | 12374 | `62bbe53c57aa6f06…` | `62bbe53c57aa6f06…` | 一致 |
| `src/check_jsonl.py` | 13575 | `1c608f8eff0dc783…` | `1c608f8eff0dc783…` | 一致 |
| `src/jsonl_to_parquet.py` | 12012 | `681ac48269bbda07…` | `681ac48269bbda07…` | 一致 |
| `src/make_sample_data.py` | 9459 | `ec8cfda22205cc73…` | `ec8cfda22205cc73…` | 一致 |
| `data/raw/README_DO_NOT_OVERWRITE.txt` | 1151 | `609921cd0ef40f4e…` | `609921cd0ef40f4e…` | 一致 |
| `data/interim/sample_records.jsonl` | 5142 | `bc5f6d7fb633f914…` | `bc5f6d7fb633f914…` | 一致 |
| `data/processed/sample_records.parquet` | 9390 | `b61a0a69e9ef60ff…` | `b61a0a69e9ef60ff…` | 一致 |
| `reports/initial_test_report.md` | 13906 | `1f7c24089c7e2fa0…` | `1f7c24089c7e2fa0…` | 一致 |
| `tests/test_pipeline.py` | 9695 | `ed7634b6d5f018c4…` | `ed7634b6d5f018c4…` | 一致 |
| `tests/run_stage1_tests.py` | 19797 | `56098192397eaeb1…` | `56098192397eaeb1…` | 一致 |
| `requirements.txt` | 1355 | `d38ebea447683e18…` | `d38ebea447683e18…` | 一致 |
| `README.md` | 5668 | `6e0e5258a63ad6c3…` | `6e0e5258a63ad6c3…` | 一致 |
| `.gitignore` | 444 | `3072194603533226…` | `3072194603533226…` | 一致 |

> 表中 SHA-256 为十六进制前 16 位缩略显示，完整值见 `integrity_file_hashes.json`。

## 4. data\raw 目录内容及哈希

| 文件 | 字节 | SHA-256 | 源中是否存在 | 结果 |
|---|---|---|---|---|
| `data/raw/README_DO_NOT_OVERWRITE.txt` | 1151 | `609921cd0ef40f4e…` | 是 | 一致 |

> data/raw 写保护机制未被触碰：`src/common.py` 的 `PROTECTED_DIRS` 与 `assert_writable()` 哈希一致，见第 3 节。

## 5. V1 测试与报告文件完整性

| 文件 | 源 | 目标 | SHA-256 一致 |
|---|---|---|---|
| `tests/test_pipeline.py` | 有 | 有 | 是 |
| `tests/run_stage1_tests.py` | 有 | 有 | 是 |
| `reports/initial_test_report.md` | 有 | 有 | 是 |
| `reports/jsonl_check_stage1.json` | 有 | 有 | 是 |
| `reports/parquet_export_stage1.json` | 有 | 有 | 是 |
| `reports/jsonl_check_20261012T074410Z.json` | 有 | 有 | 是 |
| `reports/parquet_export_20261012T075331Z.json` | 有 | 有 | 是 |

## 6. 完整逐文件哈希清单

全部 7428 个文件的 SHA-256 已写入工作区文件：

`C:\Users\HP\WorkBuddy\2026-10-12-15-36-51\migration\integrity_file_hashes.json`

## 7. 结论

- 校验结果：**通过，可以进入后续阶段**
- 源项目 C:\OpenSciGraph 在本次校验中 **仅被读取**，未做任何写入。
