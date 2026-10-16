# OpenSciGraph

学术知识图谱数据管道（**当前进度：v0.1 MVP 已发布**）。

目标是在**本地、免费、可离线**的前提下，把来源规范的实体数据
（JSONL 中间格式）规范化并输出为 Parquet 交付格式。

> **数据性质声明**：本项目**尚未接入任何真实数据源**。阶段一的管道使用**合成测试数据**；
> v0.1 MVP 黄金包由本地小模型**离线蒸馏**产出，`wikidata_id` / `source_url` 一律为 `null`、
> `license_type` 统一标为 `UNVERIFIED` —— **不冒充真实 Wikipedia / Wikidata 数据**。

---

## v0.1 MVP 快速导航

| 条目 | 位置 / 链接 |
|---|---|
| **核心产物** | `release/v0.1_mvp/OpenSciGraph_Golden_v0.1.json` —— **16 物理概念 + 16 防幻觉 Benchmarks**（11 概念辨析 + 5 幻觉陷阱） |
| **Hugging Face Datasets 主页** | <https://huggingface.co/datasets/guowei79/OpenSciGraph-Physics-Bench> |
| **数据集详细说明文档** | `release/v0.1_mvp/HuggingFace_Dataset_Card.md` |
| **联系与反馈邮箱** | rguo3500@gmail.com |

**本包要点**

- 16 条概念 + 16 道题**全部经人工逐题验算**（非模型自评）后准入；另有 9 道已隔离、
  6 道确认缺陷 + 3 道存疑已剔除，均未进入本包。
- 打包过程**未调用任何模型**（`model_involved: false`）、全程离线（`offline: true`），
  由 `scripts/build_golden_v01.py` 确定性生成（不调模型、不联网、不改原始数据）。
- 在线加载：

  ```python
  from datasets import load_dataset
  ds = load_dataset("guowei79/OpenSciGraph-Physics-Bench", "eval_items", split="train")
  ```

- 已知边界：概念间的 `parent_concept` / `child_concepts` 为**模型推断的层级边**
  （实测双向闭合率约 48.4%），**仅供检索参考，不可作为权威本体**；
  16 道公式计算题未纳入本包，也未经逐题复核。

---

## 1. 目录结构

> 下列为**阶段一的基础管道**结构。v0.1 MVP 新增的对外交付物与脚本见上方快速导航区，
> 主要为 `release/v0.1_mvp/`（黄金包、数据集卡、宣发文案）与 `scripts/`（清洗、评测生成、
> 黄金包构建、HF 上架与在线冒烟）。

```
E:\OpenSciGraph\
├── config\
│   └── settings.json                  # 全局配置（必填字段、批次大小、压缩方式等）
├── data\
│   ├── raw\                           # 【只读保护区】原始输入，脚本禁止写入
│   │   └── README_DO_NOT_OVERWRITE.txt
│   ├── interim\                       # 中间格式（JSONL）
│   │   └── sample_records.jsonl       # 10 条合成测试记录
│   └── processed\                     # 交付格式（Parquet）
│       └── sample_records.parquet
├── src\
│   ├── common.py                      # 公共工具（路径/日志/JSONL 读取/写入保护）
│   ├── make_sample_data.py            # 生成合成测试数据
│   ├── check_jsonl.py                 # 校验 JSONL（只读）
│   └── jsonl_to_parquet.py            # JSONL → Parquet
├── tests\
│   ├── test_pipeline.py               # 单元测试（标准库 unittest）
│   └── run_stage1_tests.py            # 一键跑完并生成验收报告
├── reports\                           # 校验/导出报告 + 验收报告
├── docs\
│   └── STAGE1_NOTES.md                # 阶段一说明
├── logs\                              # 运行日志（UTF-8）
├── requirements.txt
└── .gitignore
```

---

## 2. 环境准备（在 **PowerShell** 中执行）

虚拟环境已经创建在 `E:\OpenSciGraph\.venv`，依赖也已装好
（pandas 2.3.3 / pyarrow 26.0.0 / numpy 2.5.4）。

如果需要重装或换机器，执行：

```powershell
cd E:\OpenSciGraph
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

> **国内网络提示**：本机实测直连 PyPI 与部分镜像很慢或取不到索引，
> 腾讯云镜像速度正常（约 11 MB/s）。若上面的命令卡住或报
> `No matching distribution found`，改用：
> ```powershell
> .\.venv\Scripts\python.exe -m pip install `
>   -i https://mirrors.cloud.tencent.com/pypi/simple `
>   -r requirements.txt
> ```

> 如果 PowerShell 提示"禁止运行脚本"，不要修改系统策略，直接使用上面的
> `.\.venv\Scripts\python.exe` 写法即可（它绕过了激活脚本）。
>
> 若确实想激活环境，可先执行：
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> .\.venv\Scripts\Activate.ps1
> ```

---

## 3. 快速开始

以下命令**全部在 PowerShell 中执行**，工作目录为 `E:\OpenSciGraph`。

```powershell
cd E:\OpenSciGraph

# ① 一键跑完阶段一全部步骤，并生成 reports\initial_test_report.md
.\.venv\Scripts\python.exe tests\run_stage1_tests.py
```

如果想单步执行：

```powershell
cd E:\OpenSciGraph
$py = ".\.venv\Scripts\python.exe"

# 1. 生成 10 条合成测试记录
& $py src\make_sample_data.py --force
#    加 --force 才能覆盖已存在的输出文件

# 2. 校验 JSONL（只读，不会改动输入）
& $py src\check_jsonl.py --input data\interim\sample_records.jsonl
#    加 --strict 时，出现任何警告也会返回退出码 1
#    加 --batch-size 100 可调整每批行数

# 3. 导出 Parquet
& $py src\jsonl_to_parquet.py `
    --input data\interim\sample_records.jsonl `
    --output data\processed\sample_records.parquet `
    --force

# 4. 单元测试
& $py -m unittest discover -s tests -v
```

> 说明：第 1、3 步的 `--force` 只影响**派生输出**（`data/interim`、`data/processed`）。
> `data/raw` 是硬保护目录，任何写入尝试都会直接失败。

---

## 4. Parquet 列契约

`jsonl_to_parquet.py` 输出固定 12 列，顺序如下：

| 列名 | 类型 | 说明 |
|---|---|---|
| `entity_id` | string | Wikidata 风格 QID，必须匹配 `Q[1-9][0-9]*` |
| `entity_label_zh` | string | 中文标签，可为空 |
| `entity_label_en` | string | 英文标签，可为空 |
| `entity_type` | string | 实体类型 |
| `description` | string | 描述文本（多语言） |
| `description_lang` | string | 描述语言标记 |
| `aliases` | list&lt;string&gt; | 别名列表，缺失时为空列表 |
| `source` | string | 数据来源标识 |
| `license` | string | 许可信息 |
| `retrieved_at` | string | 获取时间（UTC，ISO-8601） |
| `is_synthetic` | boolean | **是否为合成测试数据** |
| `data_origin` | string | 数据性质标记，合成数据为 `SYNTHETIC_TEST_ONLY` |

---

## 5. 安全与纪律约束

- `data/raw` 只读：写入前经 `assert_writable()` 拦截（有单元测试覆盖）。
- 不调用任何收费 API，不需要任何密钥；代码与日志中不写入任何凭据。
- 不上传本地文件或原始语料。
- 支持小批次流式处理（`--batch-size`）、重复运行（幂等）、失败后重跑。
- 发现来源许可不明时，停止发布流程并生成待审核报告。
- 合成数据一律带 `is_synthetic = true`，禁止冒充真实 Wikipedia / Wikidata 数据。

---

## 6. 日志

- `logs/openscigraph.log` —— JSONL 校验日志
- `logs/jsonl_to_parquet.log` —— Parquet 导出日志
- `logs/make_sample_data.log` —— 数据生成日志
- `logs/run_stage1_tests.log` —— 一键验收脚本日志

日志为 UTF-8 追加写入，可直接用记事本或 VS Code 打开。
