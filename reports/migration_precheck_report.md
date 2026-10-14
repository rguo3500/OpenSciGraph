# OpenSciGraph 迁移 · 迁移前检查报告

- 检查时间（UTC）：`2026-10-12T08:20Z`（本地 16:20）
- 检查性质：**只读**。未创建、未修改、未删除任何文件，未发起任何网络请求。
- 源路径：`C:\OpenSciGraph`
- 目标路径：`E:\OpenSciGraph`

---

## 1. 路径与磁盘

| 检查项 | 结果 |
|---|---|
| `C:\OpenSciGraph` 是否存在 | **存在**，且为目录 |
| E 盘是否存在 | **存在**（300 GB 卷） |
| E 盘是否可写 | 是（后续复制实测成功） |
| E 盘可用空间 | **289 GB** |
| C 盘可用空间 | 99 GB |
| 源项目总大小 | 232 MB |
| 空间是否足够 | **足够**（源大小仅占可用空间的 0.08%） |

## 2. 源项目规模

| 指标 | 数值 |
|---|---|
| 全部文件数（含 `.venv`） | 7428 |
| 全部目录数（含 `.venv`） | 756（含根目录；子目录 755 个） |
| 总字节数 | 232 MB（其中 `.venv` 占 232 MB / 7403 文件） |
| 业务文件（排除 `.venv`、`__pycache__`） | **25 个，133,159 字节** |

## 3. 目录清单（排除 `.venv` / `__pycache__`）

```text
.gitignore
README.md
requirements.txt
config/settings.json
data/raw/README_DO_NOT_OVERWRITE.txt
data/interim/sample_records.jsonl
data/processed/sample_records.parquet
docs/STAGE1_NOTES.md
logs/jsonl_to_parquet.log
logs/make_sample_data.log
logs/openscigraph.log
logs/run_stage1_tests.log
reports/initial_test_report.md
reports/jsonl_check_20261012T074410Z.json
reports/jsonl_check_stage1.json
reports/parquet_export_20261012T075331Z.json
reports/parquet_export_stage1.json
src/__init__.py
src/check_jsonl.py
src/common.py
src/jsonl_to_parquet.py
src/make_sample_data.py
tests/__init__.py
tests/run_stage1_tests.py
tests/test_pipeline.py
```

## 4. 隐藏文件与特殊文件

| 检查项 | 结果 |
|---|---|
| 隐藏文件/目录 | `.gitignore`、`.venv` |
| 符号链接 | **0 个**（无链接可被误跟随） |
| 锁文件 | 未发现 |

## 5. Python 环境信息

| 项目 | 值 |
|---|---|
| 项目虚拟环境 | `C:\OpenSciGraph\.venv` |
| 解释器版本 | **Python 3.13.14** |
| `sys.prefix`（迁移前） | `C:\OpenSciGraph\.venv` |
| 基础解释器（`base_prefix`） | `C:\Users\HP\.workbuddy\binaries\python\versions\3.13.12` ← **位于项目之外** |
| 平台 | Windows-11-10.0.26200-SP0 |

依赖版本（`pip freeze` 实测）：

```text
numpy==2.5.4
pandas==2.3.3
pyarrow==26.0.0
python-dateutil==2.9.0.post0
pytz==2026.5
six==1.17.0
tzdata==2026.5
pip==26.1.2
```

## 6. Git 状态

项目**未使用 Git**：无 `.git` 目录，仅有一个 `.gitignore`。无需处理 Git 配置。

## 7. 占用项目的进程

迁移前执行 `tasklist` 检查：**没有任何 python / pythonw 进程在运行**，不存在文件占用风险。

## 8. C 盘路径引用清单（静态扫描）

| 文件 | 引用处数 | 类别 | 是否影响运行 |
|---|---|---|---|
| `src/*.py` | **0** | — | 否 |
| `tests/*.py` | **0** | — | 否 |
| `config/settings.json` | **0** | — | 否 |
| `.gitignore` | **0** | — | 否 |
| `README.md` | 6 | A 类：可复制执行的操作指引 | **需修正** |
| `reports/initial_test_report.md` | 6 | B 类：历史报告存档 | 否，不修改 |
| `.venv/Scripts/activate.bat` | 1 | 环境脚本硬编码 `VIRTUAL_ENV` | **需处理** |
| `.venv/Scripts/activate` | 1 | 同上（bash 版） | **需处理** |
| `.venv/pyvenv.cfg` | 1 | `command` 记录字段 | 仅记录，不影响运行 |
| `.venv/Scripts/pip*.exe` | 内嵌 | shebang 指向 C 盘解释器 | **需处理**（实测确认） |

关键说明：**业务代码零绝对路径**。`src/common.py` 用 `Path(__file__).resolve().parent.parent` 动态推导项目根目录，因此迁移后无需修改任何代码。

## 9. 目标目录冲突检查

| 检查项 | 结果 |
|---|---|
| `E:\OpenSciGraph` 是否已存在 | **已存在**（创建时间 2026-10-12 15:32） |
| 其中文件数（含隐藏/系统文件） | **0** |
| 是否有其他项目或用户文件 | 无，**完全为空** |
| 是否构成覆盖风险 | **无** |
| 补充说明 | E 盘根目录另有用户的个人文件（`NovelMind_AI_Project`、`海南照片`、`新建文件夹` 等），但均**不在**目标目录内，本次迁移不受影响、也不触碰 |

## 10. 是否允许继续迁移

**允许继续。**

理由：

1. 源项目存在、可读、无进程占用、无符号链接
2. 目标目录已存在但完全为空，无覆盖风险
3. 磁盘空间充足（289 GB 可用 vs 232 MB 需求）
4. 失败可回退：第二阶段采用复制方式，C 盘源项目保持原样

**需在后续阶段处理**：虚拟环境的 C 盘路径绑定（见 `migration_final_report.md` 第 C 节）。
