# STAGE3_NOTES.md — 阶段三说明

## 1. 阶段三做了什么

在阶段二 100 条高精概念数据的基础上，衍生首批 **50 道四选一物理评测题**
（《基础物理 AI 评测数据集 Benchmark》），全程本地离线。

| 题型 | 数量 | 目标 |
|---|---|---|
| `concept_distinction` 概念辨析题 | 20 | 测试模型能否区分相似物理概念 |
| `formula_reasoning` 公式应用与量纲题 | 20 | 测试公式记忆与物理量关系推理 |
| `hallucination_trap` AI 幻觉陷阱题 | 10 | 针对阶段二实测的模型易错关系设计诱导题 |

## 2. 新增文件

```
config/physics_eval_schema.json          评测集 Schema 规范（8 字段契约）
scripts/generate_physics_eval.py         衍生脚本
data/processed/physics_eval_v1.jsonl     50 道评测题终稿
data/interim/physics_eval_v1_modelraw.jsonl  模型原始输出留档（含盲测记录）
reports/stage3_eval50_report.md          阶段三终稿报告
reports/eval_answer_key_review.md        答案键复核清单（50 行全表）
```

## 3. 怎么跑

```powershell
# 先确认本地模型服务在跑
ollama list

# ① 全量生成 50 题
& .\.venv\Scripts\python.exe scripts\generate_physics_eval.py

# ② 冒烟测试（每类只出 1 题）
& .\.venv\Scripts\python.exe scripts\generate_physics_eval.py --limit-per-type 1 --force

# ③ 重制未通过盲测的题（推荐：出完题后跑一遍）
& .\.venv\Scripts\python.exe scripts\generate_physics_eval.py --repair

# ④ 出题时即附加严格自查指令
& .\.venv\Scripts\python.exe scripts\generate_physics_eval.py --strict --force
```

常用参数：`--limit-per-type N`、`--max-retry N`、`--no-verify`、`--temperature`、`--force`。

## 4. 三条设计原则

### 4.1 标识字段不由模型决定

`eval_id` / `concept_id` / `question_type` 由脚本的**确定性蓝图**给出，模型只写
题干、选项、答案、解析、盲点五个内容字段。蓝图里写死了每题锚定的概念、
对比概念、错误前提，因此覆盖面可控可复现。

### 4.2 幻觉陷阱题的错误前提来自阶段二实测缺陷

10 道陷阱题植入的错误前提，全部取自阶段二 `graph_quality` 检出的模型易错边
（如「动量属于能量」「熵是热力学第二定律的下位概念」「欧姆是电阻的下位概念」）。
这保证陷阱题打的是模型**真正犯过的错**，不是凭空设计的假想错误。

### 4.3 出题后做盲测自洽校验

把题面单独喂回模型（不给答案）让它盲答，与答案键比对。作为质量信号，
**不是正确率保证**——见第 6 节的重要限制。

## 5. 实测指标

| 指标 | 结果 |
|---|---|
| 题量 / 配额 | 50 题，20:20:10 精确命中 |
| JSON / Schema 校验通过率 | **100%**（独立复检器二次校验同样 100%） |
| 生成耗时 | 首轮 220.8 s（4.42 s/题）；修复轮 83.5 s |
| 吞吐 | 43.3 tok/s |
| 盲测自洽率 | 74.0% → **86.0%**（`--repair` 后） |
| 按题型自洽率（首轮） | 辨析 85% · **公式 60%** · 陷阱 80% |
| 人工确认有害缺陷 | **9 / 50 题** |

## 6. 已知限制（重要）

**答案键由 7B 模型生成，未经审核，不可直接使用。**

1. **盲测自洽 ≠ 物理正确。** `--repair` 把自洽率从 74% 提到 86%，但逐题验算发现：
   重制的 6 题里只有 4 题真的修好了，另 2 题（EVAL_P021 角动量、EVAL_P089 光的折射）
   只是把"不一致的错误"变成了"**一致的错误**"——模型可以稳定自信地给出错误答案键。
2. **已确认有害缺陷的 9 道题不能用。** 缺陷类型：答案键与解析矛盾、正确答案不在选项内、
   两个选项都成立（破坏单选唯一性）、题干条件不足。清单见 `reports/eval_answer_key_review.md`。
3. **真实缺陷率大概率高于 18%（9/50）。** 剩余 37 题未逐题验算。
4. 根因与阶段二一致：7B 模型能生成语言形式正确的物理文本，但**多步数值推理与
   概念边界判定不自洽**。阶段二表现为关系边错乱，阶段三表现为答案键错乱。

**结论：管道可用，答案键不可信。下一步应引入符号计算引擎（如 sympy）自动验算数值，
或由人工裁定答案键，而不是继续让模型自问自答。**

## 7. 与阶段二的关系

阶段三的陷阱题素材、以及"模型自洽但错误"的发现，都直接依赖阶段二的
`graph_quality` 实测数据。两个阶段指向同一个结论：
**当前 7B 模型的短板不在"生成流畅文本"，而在"保持事实与逻辑的一致"。**
