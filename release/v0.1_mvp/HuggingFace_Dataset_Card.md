---
pretty_name: OpenSciGraph Golden Dataset v0.1 (MVP)
language:
- zh
license: other
license_name: unverified-offline-batch
task_categories:
- multiple-choice
- question-answering
- text-classification
tags:
- physics
- knowledge-graph
- hallucination
- benchmark
- chinese
- offline
size_categories:
- n<1K
configs:
- config_name: eval_items
  data_files:
  - split: train
    path: eval_items.jsonl
- config_name: concepts
  data_files:
  - split: train
    path: concepts.jsonl
---

# OpenSciGraph Golden Dataset v0.1 (MVP)

> **一句话**：16 组基础物理概念图谱 + 16 道防幻觉评测题（概念辨析 11 + AI 幻觉陷阱 5），
> 全部经人工逐题复核准入，**100% 离线提纯、零虚假来源**，纯数据产物、无模型推理参与。

## 1. 数据简介

OpenSciGraph 面向**大模型物理知识可靠性**评测。本数据包是其 v0.1 MVP 公开样本，包含两部分内容：

| 部分 | 数量 | 内容 |
|---|---|---|
| **物理概念图谱** | 16 条 | 中英文名、中文定义、核心公式、上位/下位概念关系、许可标识 |
| **防幻觉 Benchmarks** | 16 道 | 概念辨析 11 道 + AI 幻觉陷阱 5 道，含四选项、答案键、解析、命中混淆点 |

题目与概念**严格一一对应**（`eval_id == "EVAL_" + concept_id`），且每道题内联了对应概念对象，
前端或评测脚本无需再做关联查询。

**覆盖领域**：力学（万有引力、加速度、功率）、振动与波动（频率、波长、干涉）、
热学（温度、热量、热传导）、电磁学（电荷）、光学与量子效应（偏振、光电效应、波粒二象性）。

### 它为什么值得一看

- **幻觉陷阱题是特制的**：题干植入一个错误前提（如「功率是一种能量」「加速度是运动学的一个分支学科」），
  正确答案必须明确否定该前提，而 3 个干扰项**顺着错误前提走**——专门用来暴露模型
  「把相关关系误判为种属关系」这类系统性幻觉，普通 QA 数据集测不出来。
- **答案键经过人工验算**：项目在 50 题全批次里确认了 9 道有害缺陷题并隔离，
  又在复核中发现 6 道「双正确项 / 答案键反转」缺陷——**盲测自洽 ≠ 物理正确**，
  这是本项目最重要的一条结论。本包只收编人工判定为合格的全部 16 道。
- **离线可复现**：打包脚本确定性执行，运行多少次产物完全一致（无随机抽样）。

### 溯源信息

| 项 | 值 |
|---|---|
| 数据集名称 | OpenSciGraph Golden Dataset |
| 版本 | v0.1（v0.1_mvp） |
| 生成时间（UTC） | 2026-10-14T14:00:28Z |
| 生成脚本 | `scripts/build_golden_v01.py` |
| 是否含模型推理 | `model_involved = false` |
| 是否全程离线 | `offline = true` |
| 选题方式 | 确定性提取（非随机抽样）：`fixed_human_reviewed_ok` |
| 主文件名 | `OpenSciGraph_Golden_v0.1.json` |
| sha256 | `0cac0180402d470e24e4a4a48edb023ad74712c2ec95379128a45090955b704c` |

### 仓库文件

| 文件 | 说明 |
|---|---|
| `README.md` | 本数据集卡（由 `HuggingFace_Dataset_Card.md` 改名而来） |
| `OpenSciGraph_Golden_v0.1.json` | 完整数据包（UTF-8 无 BOM，41201 字节），含 `concepts[]` 与 `eval_items[]` |
| `eval_items.jsonl` | `datasets` 分片：16 行，一行一题 |
| `concepts.jsonl` | `datasets` 分片：16 行，一行一概念 |

> **为什么有两个 JSONL？** 完整数据包是**单个 JSON 对象**，而 HuggingFace 的 json loader 面向
> 「JSONL 或 JSON 数组」，无法把嵌套对象展开成多行。因此额外提供两个扁平分片，
> 二者均由同一份数据派生、与主包逐行一致，保证 `load_dataset()` 开箱可用。

## 2. 质量证明：28 项结构校验全部 PASS

成品落盘前由打包脚本执行 28 项结构校验，结论 **28/28 全部通过**；
另用**独立脚本**（不复用同一套校验代码）二次交叉复核，结论一致。完整明细见仓库内
`reports/stage4_golden_v01_validation.md`。

| # | 检查项 | 结论 | 说明 |
|---|---|---|---|
| 1 | 顶层必需键齐全 | ✅ PASS | 缺失=[] |
| 2 | eval_items 数量 = 16 | ✅ PASS | 实际=16 |
| 3 | concepts 数量 = 16 | ✅ PASS | 实际=16 |
| 4 | counts 与实际一致 | ✅ PASS | counts=16/16 |
| 5 | eval_id 集合与清单一致 | ✅ PASS | 实际=['EVAL_P004', 'EVAL_P006', 'EVAL_P008', 'EVAL_P010', 'EVAL_P012', 'EVAL_P026', 'EVAL_P044', 'EVAL_P045', 'EVAL_P049', 'EVAL_P059', 'EVAL_P060', 'EVAL_P070', 'EVAL_P073', 'EVAL_P093', 'EVAL_P096', 'EVAL_P098'] |
| 6 | eval_id 无重复 | ✅ PASS | — |
| 7 | 提取顺序 = 辨析在前/陷阱在后 | ✅ PASS | — |
| 8 | 题型分布 11 辨析 / 5 陷阱 / 0 公式 | ✅ PASS | 辨析=11 陷阱=5 公式=0 |
| 9 | eval_item 字段与顺序符合契约 | ✅ PASS | — |
| 10 | options 均为 4 项、非空、互不重复 | ✅ PASS | — |
| 11 | correct_option ∈ {A,B,C,D} | ✅ PASS | — |
| 12 | 内联 concept 与 concepts[] 逐字段一致 | ✅ PASS | — |
| 13 | eval_id == 'EVAL_' + concept_id | ✅ PASS | — |
| 14 | concept_id 全局唯一 | ✅ PASS | — |
| 15 | concepts[].concept_id 与题目一一对应 | ✅ PASS | — |
| 16 | concept 字段与顺序符合契约 | ✅ PASS | — |
| 17 | wikidata_id 全部为 null（零虚假来源） | ✅ PASS | — |
| 18 | source_url 全部为 null（零虚假来源） | ✅ PASS | — |
| 19 | license_type 全部为 UNVERIFIED | ✅ PASS | — |
| 20 | definition_zh 全部 >= 10 字 | ✅ PASS | — |
| 21 | 不含被隔离的缺陷题 | ✅ PASS | — |
| 22 | 全部题目人工复核判定为 ok | ✅ PASS | — |
| 23 | model_involved == false | ✅ PASS | — |
| 24 | offline == true | ✅ PASS | — |
| 25 | JSON 可序列化且往返一致 | ✅ PASS | — |
| 26 | 文本无 BOM | ✅ PASS | — |
| 27 | 换行统一为 LF | ✅ PASS | — |
| 28 | UTF-8 可解码 | ✅ PASS | 41201 字节 |

校验覆盖的六个维度：

1. **结构与计数**：顶层键齐全、`eval_items` = 16、`concepts` = 16、`counts` 与实测一致；
2. **标识一致性**：`eval_id` 集合与人工清单精确相等、无重复、辨析在前陷阱在后、题型分布 11 / 5 / 0；
3. **字段契约**：字段名与**顺序**逐条比对 Schema、`options` 恰好 4 项且非空去重、`correct_option ∈ {A,B,C,D}`；
4. **关系完整性**：`eval_id == "EVAL_" + concept_id`、概念 ID 全局唯一、内联 `concept` 与 `concepts[]` 逐字段一致；
5. **来源诚信**：`wikidata_id` / `source_url` **全部为 `null`**、`license_type` 全为 `UNVERIFIED`、`definition_zh` 均 ≥ 10 字；
6. **排除与编码**：无隔离缺陷题混入、全部题目人工判定为 `ok`、JSON 可往返序列化、无 BOM、纯 LF、UTF-8 可解码。

> **口径说明**：「零虚假来源」指来源字段一律留空、绝不编造 QID 或链接；
> 这**不等于**数据已权威化——`parent_concept` / `child_concepts` 关系边尚未核验（见第 5 节）。

## 3. 数据样例

以下两段 JSON **直接从 `OpenSciGraph_Golden_v0.1.json` 的 `eval_items[]` 中抽取**，未做任何改写。

### 3.1 概念辨析题示例 —— `EVAL_P006`（能量）

```json
{
  "eval_id": "EVAL_P006",
  "concept_id": "P006",
  "question_type": "concept_distinction",
  "question": "关于能量和动能的区别，以下描述正确的是？",
  "options": [
    "能量包括动能、势能和内能等多种形式",
    "动能是物体由于静止而具有的能量",
    "能量和动能的单位都是焦耳，因此它们没有区别",
    "动能可以转化为其他形式的能量，但能量不能相互转化"
  ],
  "correct_option": "A",
  "explanation": "正确选项A说明了能量是统称，包括动能、势能和内能等多种形式。主要干扰项B混淆了静止物体不具有动能的概念。",
  "target_hallucination_point": "模型可能混淆静止物体是否具有动能",
  "concept": {
    "concept_id": "P006",
    "name_zh": "能量",
    "name_en": "Energy",
    "wikidata_id": null,
    "definition_zh": "物体进行工作或引起变化的能力。",
    "formula": null,
    "parent_concept": "物理量",
    "child_concepts": [
      "动能",
      "势能",
      "内能"
    ],
    "license_type": "UNVERIFIED",
    "source_url": null,
    "missing_zh_reason": null
  }
}
```

**看点**：干扰项 B 把「静止」和「动能」对立起来（静止物体动能为零，故 B 为假），
C 用「单位相同 ⇒ 没有区别」偷换概念，D 则否认了能量守恒框架下能量形式的相互转化。

### 3.2 AI 幻觉陷阱题示例 —— `EVAL_P004`（万有引力定律）

```json
{
  "eval_id": "EVAL_P004",
  "concept_id": "P004",
  "question_type": "hallucination_trap",
  "question": "关于万有引力定律与力的关系，下列说法正确的是？某同学认为万有引力定律就是一种力，请你判断。",
  "options": [
    "是的，万有引力定律就是一种力",
    "不是，万有引力定律描述了力的作用规律",
    "万有引力定律可以产生力，但不是力本身",
    "万有引力定律与力没有关系"
  ],
  "correct_option": "B",
  "explanation": "正确答案为B，万有引力定律描述的是物体之间力的作用规律，而不是一种力。干扰项A和C看似合理，但都未能明确指出二者本质上的区别。D项虽然提到了关系不成立，但没有具体说明正确的关系。",
  "target_hallucination_point": "把相关关系误判为种属关系",
  "concept": {
    "concept_id": "P004",
    "name_zh": "万有引力定律",
    "name_en": "Newton's law of universal gravitation",
    "wikidata_id": null,
    "definition_zh": "两个物体之间存在相互吸引的力，其大小与两物体质量的乘积成正比，与它们距离的平方成反比。",
    "formula": "F = G * (m1 * m2) / r^2",
    "parent_concept": "力",
    "child_concepts": [],
    "license_type": "UNVERIFIED",
    "source_url": null,
    "missing_zh_reason": null
  }
}
```

**看点**：题干把「万有引力定律是一种力」这个**错误前提**塞给模型。
选项 A 直接顺从前提；选项 C「定律可以产生力，但不是力本身」看似辩证，
实际仍未否定「定律 vs 力」的混淆——这正是模型最容易踩的坑。
对应的 `target_hallucination_point` 字段写明：*把相关关系误判为种属关系*。

## 4. 开发者加载代码（Python）

主文件是**单个 JSON 对象**（非 JSONL、非 parquet），含概念图谱与题目两部分；
仓库另提供两个扁平的 JSONL 分片供 `datasets` 在线加载。

### 4.1 在线加载（HuggingFace `datasets`，推荐）

```python
from datasets import load_dataset

# 评测题分片：16 行，一行一题
bench = load_dataset('guowei79/OpenSciGraph-Physics-Bench', 'eval_items', split='train')
print(bench)
print(bench[0]['eval_id'], bench[0]['question_type'], bench[0]['correct_option'])

# 概念分片：16 行，一行一概念
concepts_ds = load_dataset('guowei79/OpenSciGraph-Physics-Bench', 'concepts', split='train')
print(concepts_ds[0]['name_zh'], concepts_ds[0]['definition_zh'])
```

> **国内网络提示**：`huggingface.co` 在中国大陆可能不可达。下载场景可先设镜像：
> `export HF_ENDPOINT=https://hf-mirror.com`（PowerShell：`$env:HF_ENDPOINT="https://hf-mirror.com"`）。
> 实测（2026-10-14）该镜像同样**透传写操作**，`create_repo` / `upload_file` / `delete_repo` 均可用，
> 故本数据集的上架亦经镜像端点完成；但镜像稳定性不由本项目保证，正式发布建议直连官方站点。

### 4.2 直接读取单文件 JSON（含完整图谱）

```python
import json
from pathlib import Path

PATH = Path('release/v0.1_mvp/OpenSciGraph_Golden_v0.1.json')

with PATH.open(encoding='utf-8') as fh:        # 注意：UTF-8，无 BOM
    data = json.load(fh)

print(data['counts'])
# {'concepts': 16, 'eval_items': 16, 'distinction': 11, 'trap': 5, ...}

concepts = {c['concept_id']: c for c in data['concepts']}
for item in data['eval_items']:
    assert item['concept'] == concepts[item['concept_id']]   # 内联副本一致性自检
```

### 4.3 按题型筛选

```python
distinction = [i for i in data['eval_items'] if i['question_type'] == 'concept_distinction']
trap        = [i for i in data['eval_items'] if i['question_type'] == 'hallucination_trap']

print(len(distinction), len(trap))   # 11 5
```

### 4.4 评测你的模型（完整打分骨架）

```python
import re

PROMPT = '''请回答下面的单选题，只输出一个大写字母（A/B/C/D）。

{question}

A. {o0}
B. {o1}
C. {o2}
D. {o3}'''

def build_prompt(item):
    return PROMPT.format(
        question=item['question'],
        o0=item['options'][0], o1=item['options'][1],
        o2=item['options'][2], o3=item['options'][3],
    )

def extract_choice(text):
    m = re.search(r'\b([ABCD])\b', text.upper())
    return m.group(1) if m else None

def evaluate(model_fn, items):
    rows, correct = [], 0
    for item in items:
        pred = extract_choice(model_fn(build_prompt(item)))
        ok = (pred == item['correct_option'])
        correct += ok
        rows.append({
            'eval_id': item['eval_id'],
            'question_type': item['question_type'],
            'gold': item['correct_option'],
            'pred': pred,
            'correct': ok,
        })
    acc = correct / len(items) if items else 0.0
    # 陷阱题准确率单独统计——这才是本数据集的核心指标
    traps = [r for r in rows if r['question_type'] == 'hallucination_trap']
    trap_acc = sum(r['correct'] for r in traps) / len(traps) if traps else 0.0
    return {'overall_acc': acc, 'trap_acc': trap_acc, 'details': rows}

# 示例：接任意模型（此处用本地 Ollama 的 chat 接口）
# from ollama import Client
# client = Client(host='http://127.0.0.1:11434')
# def model_fn(p):
#     return client.chat(model='qwen2.5:7b-instruct-q5_K_M',
#                        messages=[{'role': 'user', 'content': p}])['message']['content']
# print(evaluate(model_fn, data['eval_items']))
```

### 4.5 概念图谱字段速查

```python
c = concepts['P006']
print(c['name_zh'], c['name_en'])      # 能量 Energy
print(c['definition_zh'])              # 物体进行工作或引起变化的能力。
print(c['formula'])                    # None（描述性概念无公式）
print(c['parent_concept'], c['child_concepts'])
# 物理量 ['动能', '势能', '内能']
print(c['wikidata_id'], c['source_url'], c['license_type'])
# None None UNVERIFIED
```

## 5. 已知限制

请在使用前了解以下几点，避免误用：

1. concepts[].parent_concept / child_concepts 为模型推断的层级边，阶段二复核实测约半数边不可信（双向闭合率仅 48.4%），仅供检索参考，不可作为权威本体。
2. EVAL_P049 题干内嵌了选项文本（格式瑕疵），不影响答案键正确性。
3. 公式计算题（16 道）按要求未纳入本包，也未经逐题复核。
4. suspect 与 defect 题目仍留在主线数据 physics_eval_v1.jsonl 中，扩充评测集前须先修正或剔除。

此外：本包仅 **16 组**样本，适合做**冒烟测试与展示**，统计显著性有限；
同批次主线数据中仍存在未经复核的公式计算题，不建议直接并入评测。

## 6. 需求反馈与联系

本数据包为 v0.1 MVP 公开样本。如果你需要**全量数据、定制数据集或合作**，欢迎联系我们：

| 需求类型 | 说明 | 联系方式 |
|---|---|---|
| 索要全量数据 | 完整概念图谱与全量评测题（含未公开部分） | rguo3500@gmail.com |
| 定制数据集 | 指定学科领域 / 题型配比 / 语言 / 输出格式（JSONL、Parquet 等） | rguo3500@gmail.com |
| 缺陷反馈 | 发现答案键错误、概念定义不准或关系边有误 | https://github.com/rguo3500/OpenSciGraph / Issues |
| 商务与合作 | 联合评测、模型幻觉专项测评、企业内训数据 | rguo3500@gmail.com |

**联系时建议附上**：

- 你的使用场景（评测 / 训练 / 检索 / 展示）
- 目标学科与题量需求
- 期望的数据格式与许可要求

- 代码仓库：https://github.com/rguo3500/OpenSciGraph
- HuggingFace 主页：https://huggingface.co/datasets/guowei79/OpenSciGraph-Physics-Bench

## 7. 引用与许可

```bibtex
@misc{openscigraph_golden_v0_1,
  title        = {OpenSciGraph Golden Dataset v0.1 (MVP)},
  author       = {OpenSciGraph Contributors},
  year         = {2026},
  note         = {16 physics concepts + 16 anti-hallucination benchmarks, offline-curated}
}
```

**许可**：`license_type = UNVERIFIED`。本批次为离线产出，**未联网核验上游来源与许可**，
因此不对数据来源作任何权利主张，也不保证可再分发。使用前请自行评估合规风险。
若你计划商用，请先通过上方联系方式取得确认。

---

*本卡片由 `scripts/build_golden_v01.py` 自动生成于 2026-10-14T14:00:28Z，所有数字与样例均取自同一批次成品（sha256 `0cac0180402d470e…`）。*
