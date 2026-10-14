# STAGE2_NOTES.md — 阶段二说明

阶段二目标：用**本地离线**大模型，把基础物理概念清单提纯成 V2 结构化记录。

当前状态：**管道已跑通**，首批 10 条种子数据已产出（详见 `reports/stage2_seed10_report.md`）。

---

## 1. 阶段二相比阶段一新增了什么

阶段一是「目录骨架 + JSONL 校验 + Parquet 导出」，只处理合成测试数据。
阶段二引入**真实内容生成**：由本地 Ollama 上的 `qwen2.5:7b-instruct-q5_K_M`
为每个物理概念生成中文定义、核心公式、上位/下位概念。

| 项 | 阶段一 | 阶段二 |
|---|---|---|
| 数据来源 | 合成测试数据 | 本地大模型离线生成 |
| 中间格式 | `data/interim/sample_records.jsonl`（12 字段） | `data/processed/physics_concepts_v2.jsonl`（11 字段） |
| 结构契约 | `config/settings.json` | `config/physics_v2_schema.json` |
| 输入清单 | 无 | `config/physics_concepts_100_catalog.json`（100 条） |
| 出网 | 无 | **仍然无**（仅访问 127.0.0.1:11434） |

---

## 2. 新增文件

```
config/
  physics_concepts_100_catalog.json   # 100 条概念清单（P001-P100），权威输入
  physics_v2_schema.json              # V2 记录契约（11 字段）
scripts/                              # ← 新目录。项目原有约定是 src/，此处按指令放置
  clean_physics_v2.py                 # 清洗主脚本
data/processed/
  physics_concepts_v2.jsonl           # 交付物
data/interim/
  physics_concepts_v2_modelraw.jsonl  # 模型原始输出留档（审计）
  prompt_variant_v1.jsonl             # prompt 迭代对比
  prompt_variant_v2.jsonl
reports/
  stage2_seed10_report.md             # 阶段汇报
  physics_v2_run_<UTC时间戳>.json      # 每次运行的完整指标
logs/
  physics_v2.log
```

---

## 3. 怎么跑

在 `E:\OpenSciGraph` 下（PowerShell）：

```powershell
$py = ".\.venv\Scripts\python.exe"

# 先确认本地模型服务在跑
ollama list

# ① 首批 10 条种子（清单里 seed_batch 标记的概念）
& $py scripts\clean_physics_v2.py --seed-only --force

# ② 全量 100 条
& $py scripts\clean_physics_v2.py --force

# ③ 前 N 条
& $py scripts\clean_physics_v2.py --limit 20 --force
```

### 常用参数

| 参数 | 作用 |
|---|---|
| `--seed-only` | 只跑清单里 `seed_batch` 标记的 10 条 |
| `--limit N` | 只跑前 N 条 |
| `--force` | 覆盖已有输出（**默认是断点续跑**，跳过已完成的 concept_id） |
| `--qid-policy null\|model` | `wikidata_id` 策略，默认 `null`（不臆造），详见下节 |
| `--no-format-json` | 关闭 Ollama JSON 约束，用于对比实验 |
| `--temperature` | 默认 0.2 |
| `--timeout` | 单次请求超时，默认 300 秒 |

**幂等性**：不加 `--force` 时脚本会读取已有输出、跳过已完成的 `concept_id`，
中断后直接重跑即可续上。

---

## 4. 两条设计原则（重要）

### 4.1 标识字段不由模型决定

`concept_id` / `name_zh` / `name_en` **一律以 config 清单为权威值**。
模型即使改写，也会被脚本覆盖并记一条告警。
这样保证 ID 不会漂移、可重复运行结果稳定。

### 4.2 离线不可核验的字段一律留 `null`

依项目 README 第 5 节纪律（禁止冒充真实 Wikipedia / Wikidata 数据）：

| 字段 | 离线批次取值 | 原因 |
|---|---|---|
| `wikidata_id` | `null` | 模型凭记忆生成的 QID 无法离线核验 |
| `source_url` | `null` | 同上 |
| `license_type` | `"UNVERIFIED"` | 许可未核验，不填看起来像真的许可证名 |
| `missing_zh_reason` | `null` | 本批 `name_zh` 均存在 |

`name_zh` 缺失时的既定策略：**保留空字符串 + 在 `missing_zh_reason` 记录原因**，
而不是填 `null` 或让模型猜。

若确需模型输出 QID 猜测值（不推荐）：
```powershell
& $py scripts\clean_physics_v2.py --seed-only --force --qid-policy model
```

---

## 5. 脚本内置的质量体检

每次运行结束，报告 JSON 的 `graph_quality` 段会自动给出：

- `dangling_parent_refs` / `dangling_child_refs`：指向本批次外概念的悬空引用
  （跨批次时属正常，100 条跑完后会大幅减少）
- `bidirectional_closure_rate`：A 声明 `parent=B` 时，B 是否也把 A 列进 `child_concepts`
- `category_like_parent_count`：把学科分类名（力学/运动学…）当成上位概念的条数
- `avg_children_per_record`：平均下位概念数

另外，`validate_record()` 会对每条记录产出告警列表：
名称被覆盖、定义过短、`child_concepts` 类型异常、上位是分类名等。

---

## 6. 已知限制

**关系边（`parent_concept` / `child_concepts`）质量是当前瓶颈。**
7B 模型对「上位/下位」的理解不稳定，实测约一半关系边需要复核，
且同一 prompt 重跑结果会变。定义与公式字段质量明显更好（人工核对 10/10 正确）。

详见 `reports/stage2_seed10_report.md` 第 6 节的分析与建议。

**建议：关系边的最终定稿走人工/联网复核，而不是继续调 prompt。**

---

## 7. 全量 100 条跑批结果（2026-10-14）

跑批命令：

```powershell
# 断点续传：自动跳过已完成的 concept_id，只补未跑的 90 条
& .\.venv\Scripts\python.exe scripts\clean_physics_v2.py
```

| 指标 | 结果 |
|---|---|
| 记录数 | 100（P001–P100 连续无缺口） |
| 合计耗时 | 193.9 s（种子批 18.9 s + 全量批 175.0 s） |
| 平均单条 | 1.94 s |
| 生成 token | 7,131（平均 71.3/条） |
| 吞吐 | 42.42 tok/s |
| JSON 可解析率 / 零污染率 | 100% / 100% |
| Schema 合规率 | 100%（跑批时 98.9%，P042 修补后复检 100%） |
| API 失败 | 0 |

**关系边实测（100 条终稿）：** 上位边 100 条、下位边 98 条、平均每条下位 0.98 个、
双向闭合率 **48.4%**、13 条把学科分类名当上位概念。69 条上位的指向落在本批次外
（跨批引用，待后续批次补齐，属正常）。

**P042「振幅」修补**：模型首次给出 9 字定义，低于 Schema 的 10 字下限，
用同一 prompt 重掷第 2 次得到 16 字定义后原地替换，行序不变。
审计留档 `reports/repair_p042_audit.jsonl`，raw 留档追加 1 条 repair 记录。

完整报告：`reports/stage2_full100_report.md`
关系边人工复核清单：`reports/graph_quality_review.md`（19 条需人工介入）

**下一阶段注意**：本批关系边的双向闭合率不足 50%，**不可直接作为衍生 AI 评测集的
关系型 ground truth**，需先人工校订或引入外部权威知识库校验。
