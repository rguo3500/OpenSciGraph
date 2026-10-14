# OpenSciGraph 项目迁移最终报告（C 盘 → E 盘）

- 报告生成时间（UTC）：`2026-10-12T08:30Z`（本地 16:30）
- 执行方式：实际复制 + 逐文件哈希校验 + E 盘实机运行验收
- 网络访问：**未发起任何针对 Wikipedia / Wikidata 或任何数据源的请求；未下载任何数据**

---

## A. 迁移前检查

| 项目 | 值 |
|---|---|
| 源目录 | `C:\OpenSciGraph`（存在，可读） |
| 目标目录 | `E:\OpenSciGraph`（已存在但**完全为空**，0 条目） |
| C 盘可用空间 | 99 GB |
| E 盘可用空间 | **289 GB** |
| 源项目文件数 | 7428（业务文件 25 个 + `.venv` 7403 个） |
| 源项目总字节数 | 232 MB |
| 业务文件字节数 | 133,159 B |
| 符号链接 | 0 |
| 占用进程 | 无 |
| C 盘路径引用（业务代码） | **0 处** |
| 迁移前结论 | **允许继续** |

详细内容见 `migration_precheck_report.md`。

## B. 文件完整性

| 指标 | 数值 |
|---|---|
| 源文件数 | 7428 |
| 复制成功数 | **7428** |
| 复制失败数 | **0** |
| SHA-256 不一致数 | **0** |
| 字节数不一致数 | **0** |
| 目录数（源 / 目标） | 755 / 755 |
| 路径集合差异（仅源 / 仅目标） | 0 / 0 |
| 未能校验的文件 | **无** |
| 被跳过的锁文件 | **无** |
| 符号链接复制 | 无（0 个，未跟随任何外部链接） |

校验方式：相对路径集合 + 每个文件字节数 + 每个文件 SHA-256 全量比对。
完整逐文件哈希清单：工作区 `migration\integrity_file_hashes.json`。

**结论：复制阶段零丢失、零损坏。**

## C. Python 环境

### C.1 原环境（复制来的 `.venv`）实测

| 检查项 | 结果 |
|---|---|
| `E:\OpenSciGraph\.venv\Scripts\python.exe --version` | Python 3.13.14（**可运行**） |
| `sys.prefix` | `E:\OpenSciGraph\.venv`（正确） |
| 依赖导入 | pandas 2.3.3 / pyarrow 26.0.0 / numpy 2.5.4（**可用**） |
| `Scripts\activate.bat` | **硬编码 `VIRTUAL_ENV=C:\OpenSciGraph\.venv`** |
| `Scripts\activate`（bash 版） | **硬编码 `cygpath 'C:\OpenSciGraph\.venv'`** |
| `Scripts\pip.exe --version` | **`pip 26.1.2 from C:\OpenSciGraph\.venv\Lib\site-packages\pip`** ← 实际操作的是 C 盘环境，存在误改源项目的风险 |

### C.2 处理决定与执行

原环境的 `python.exe` 可用，但其**启动脚本与 `pip.exe` 仍绑定 C 盘路径**，符合迁移指令中"必须重建"的触发条件。据此执行：

1. ✅ 保存原依赖清单 → `venv_original_freeze.txt` / `venv_original_pip_list.json`
2. ✅ **未删除**原复制来的 venv，而是重命名保留为 `E:\OpenSciGraph\.venv_c_mirror_backup`（232 MB）
3. ✅ 用**同一基础解释器** `C:\Users\HP\.workbuddy\binaries\python\versions\3.13.12\python.exe` 在 `E:\OpenSciGraph\.venv` 新建环境
4. ✅ 安装**完全相同的依赖版本**（全部命中本地 pip 缓存，**未产生实际下载**）
5. ✅ C 盘原虚拟环境**未做任何改动**

### C.3 重建结果

| 项目 | 值 |
|---|---|
| 解释器 | `E:\OpenSciGraph\.venv\Scripts\python.exe` |
| 版本 | Python 3.13.14 |
| `sys.prefix` | `E:\OpenSciGraph\.venv` |
| `base_prefix` | `C:\Users\HP\.workbuddy\binaries\python\versions\3.13.12` |
| `pip.exe` 指向 | **`E:\OpenSciGraph\.venv\Lib\site-packages\pip`**（问题已修复） |
| 启动脚本 C 盘引用 | **已无** |
| 依赖版本与原清单对比 | **完全一致，零差异** |

```text
numpy==2.5.4
pandas==2.3.3
pyarrow==26.0.0
python-dateutil==2.9.0.post0
pytz==2026.5
six==1.17.0
tzdata==2026.5
```

> ⚠️ **必须知悉**：`base_prefix` 指向 `C:\Users\HP\.workbuddy\binaries\python\versions\3.13.12`。
> 这是**基础 Python 解释器**，位于 OpenSciGraph 项目之外（属系统级运行时，不是"项目文件"）。
> 用同一基础解释器重建是为了保证版本一致。若该基础解释器被移除，E 盘 venv 将失效——
> 届时需要换用其他 Python 3.13 重新建环境。这一点在下面"后续操作"中也有提示。

## D. 路径检查

### D.1 发现的 C 盘路径引用

| 文件 | 处数 | 类别 | 处置 |
|---|---|---|---|
| `src/*.py` | 0 | — | 无需处理 |
| `tests/*.py` | 0 | — | 无需处理 |
| `config/settings.json` | 0 | — | 无需处理 |
| **`README.md`** | 6 | **A 类：可复制执行的操作指引** | ✅ **已修正**（仅 E 盘副本） |
| `reports/initial_test_report.md` | 6 | B 类：阶段一历史报告 | ❌ **不修改**（历史记录不可篡改） |
| `.venv` 内脚本与 `pip.exe` | 见 C 节 | 环境绑定 | ✅ **通过重建解决** |

### D.2 实际修改内容

**仅修改 1 个文件**：`E:\OpenSciGraph\README.md`，6 处 `C:\OpenSciGraph` → `E:\OpenSciGraph`
（目录树示例 1 处、环境说明 1 处、`cd` 命令 3 处、工作目录说明 1 处）。

- ❌ 未做全局批量替换
- ❌ 未修改 `C:\OpenSciGraph\README.md`（源文件仍为 6 处 C 盘路径，哈希未变）
- ❌ 未修改任何 `src/` 或 `tests/` 代码
- ❌ 未修改 `config/settings.json`、未修改 12 列 Parquet 契约
- ❌ 未创建任何 `.bat` / `.ps1` 启动脚本

## E. 测试结果（E 盘实机运行）

工作目录：`E:\OpenSciGraph`；解释器：`E:\OpenSciGraph\.venv\Scripts\python.exe`

| # | 测试项 | 退出码 | 预期 | 结果 |
|---|---|---|---|---|
| 1 | Python 版本检查 | 0 | 0 | 通过 |
| 2 | 依赖导入检查 | 0 | 0 | 通过 |
| 3 | V1 单元测试（unittest） | 0 | 0 | 通过 |
| 4 | JSONL 校验脚本 | 1 | 0,1 | 通过（退出码 1 属预期） |
| 5 | Parquet 导出（默认交付路径） | 0 | 0 | 通过 |
| 6 | Parquet 回读与列契约校验 | 0 | 0 | 通过 |
| 7 | 配置读取与路径解析 | 0 | 0 | 通过 |
| 8 | data/raw 写保护 | 0 | 0 | 通过 |
| 9 | 生成文件输出路径检查 | 0 | 0 | 通过 |

- **单元测试：Ran 21 tests，失败 0，全部通过**
- **V2 离线测试：未执行 / 尚不存在**（项目中没有 V2 测试文件，未编造结果）
- 第 4 项退出码 1 的原因：合成夹具故意包含 2 条非法 QID（`QABC123`、`42`），属设计预期，**未修改测试预期来"通过"**

关键证据：

```text
PROJECT_ROOT E:\OpenSciGraph
RAW_DIR      E:\OpenSciGraph\data\raw
PROTECTED_DIRS ['E:\\OpenSciGraph\\data\\raw']
REPORTS_DIR  E:\OpenSciGraph\reports
ALL_BLOCKED  True            ← data/raw 写保护在 E 盘生效
processed_writable True
```

- Parquet 测试前后 SHA-256 **一致** → 导出可复现，未被测试破坏
- 日志与报告产物中**未发现** `C:\OpenSciGraph` 运行依赖

详细逐项输出见 `migration_runtime_test_report.md`。

## F. 原项目保护

### C 盘源项目状态：**完全未改动**

校验方式：用迁移前建立的 7428 文件哈希基线，在全部操作完成后重新扫描 C 盘逐文件比对。

| 指标 | 结果 |
|---|---|
| 基线文件数 | 7428 |
| 当前文件数 | 7428 |
| **被修改** | **0** |
| **被删除** | **0** |
| **新增** | **0** |
| 结论 | **C:\OpenSciGraph 与迁移前完全一致** |

其它保护措施执行情况：

- ✅ 未剪切、未移动、未重命名源项目
- ✅ 未删除任何文件
- ✅ `data/raw` 写保护机制未被修改（`src/common.py` 哈希一致，写保护实测仍生效）
- ✅ 未创建任何指向 C 盘项目的运行依赖、目录联接或符号链接
- ✅ 未修改系统环境变量、未卸载任何环境

## G. 最终运行路径

```
E:\OpenSciGraph
```

**本项目在 E 盘的运行方式**：使用 `E:\OpenSciGraph\.venv\Scripts\python.exe`，
工作目录为 `E:\OpenSciGraph`。已实测：所有输出（报告、日志、Parquet）均落在 E 盘项目内。

## H. 后续操作

### H.1 在 E 盘启动与运行（在 PowerShell 中执行）

```powershell
cd E:\OpenSciGraph

# 直接调用解释器（推荐，无需激活）
.\.venv\Scripts\python.exe --version

# 一键跑通阶段一全流程并生成报告
.\.venv\Scripts\python.exe tests\run_stage1_tests.py

# 单元测试
.\.venv\Scripts\python.exe -m unittest discover -s tests -v

# 校验 JSONL
.\.venv\Scripts\python.exe src\check_jsonl.py --input data\interim\sample_records.jsonl

# 导出 Parquet
.\.venv\Scripts\python.exe src\jsonl_to_parquet.py `
    --input data\interim\sample_records.jsonl `
    --output data\processed\sample_records.parquet --force
```

如需激活虚拟环境：

```powershell
cd E:\OpenSciGraph
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### H.2 提请注意的遗留事项（等你确认后再动）

1. **`.venv_c_mirror_backup`（232 MB）** —— 这是从 C 盘复制来的原 venv，因绑定 C 盘路径而未被启用，予以**保留未删除**。确认 E 盘环境稳定后可自行删除。
2. **基础解释器依赖** —— E 盘 venv 依赖 `C:\Users\HP\.workbuddy\binaries\python\versions\3.13.12` 作为基础解释器（项目外）。若希望彻底脱离 C 盘，需安装独立的 Python 3.13 后重建 venv。
3. **测试产物** —— 验收过程在 `reports/` 新增 2 个时间戳报告、在 `logs/` 追加了日志，均为测试正常运行结果。
4. **C 盘归档** —— 按你的指令，C:\OpenSciGraph **保持原样未动**，等你后续确认归档方案。

---

## 迁移成功判定（对照指令第十节）

| 判定条件 | 状态 |
|---|---|
| E:\OpenSciGraph 完整存在 | ✅ |
| 关键文件哈希校验通过 | ✅（复制阶段 7428/7428 一致） |
| Python 环境在 E 盘可用 | ✅（重建后解释器、依赖、pip 全部指向 E 盘） |
| 原有 V1 测试通过 | ✅（21/21） |
| 关键数据和配置完整 | ✅ |
| data/raw 写保护未被修改 | ✅（`ALL_BLOCKED True`，源代码哈希一致） |
| 所有迁移所需路径已正确处理 | ✅ |
| 运行命令确实使用 E 盘项目 | ✅ |
| 没有发生网络访问或数据下载 | ✅（依赖安装全部命中本地缓存） |

**结论：迁移成功。运行路径为 `E:\OpenSciGraph`。**
