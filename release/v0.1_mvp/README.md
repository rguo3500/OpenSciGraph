# OpenSciGraph Golden Dataset v0.1 (MVP)

> 一份**完全离线提纯、零虚假来源**的基础物理概念图谱 + 防幻觉评测样例包。
> 本包为纯数据产物，生成过程中**未调用任何大模型推理**（`model_involved: false`）。

## 一、数据概览

- **16 组物理概念图谱实体**：覆盖力学、振动与波动、热学、电磁学、光学与量子效应，
  每条含中英文名、中文定义、核心公式、上位/下位概念关系与许可标识。
- **16 道防幻觉 Benchmarks 样例**：概念辨析题 11 道 + AI 幻觉陷阱题 5 道，
  每道题含题干、四选项、正确答案键、解析与命中的混淆点。
- **一一对应**：16 道题的 `concept_id` 与 16 条概念实体严格一一对应，
  且每道题内联了对应概念对象，前端无需再做关联查询。

### 文件清单

| 文件 | 说明 |
|---|---|
| `OpenSciGraph_Golden_v0.1.json` | 主交付文件（UTF-8 无 BOM，41201 字节） |
| `eval_items.jsonl` | HF `datasets` 分片：16 行，一行一题（与主包逐行一致） |
| `concepts.jsonl` | HF `datasets` 分片：16 行，一行一概念（与主包逐行一致） |
| `HuggingFace_Dataset_Card.md` | 对外发布用数据集卡（含质量证明、样例、加载代码、需求反馈区） |
| `COMMUNITY_POST.md` | 社区宣发文案套件（V2EX + 英文简版） |
| `README.md` | 本说明文档 |

### 概念清单

| # | concept_id | 中文名 | 英文名 | 核心公式 | 上位概念 |
|---|---|---|---|---|---|
| 1 | `P004` | 万有引力定律 | Newton's law of universal gravitation | F = G * (m1 * m2) / r^2 | 力 |
| 2 | `P006` | 能量 | Energy | — | 物理量 |
| 3 | `P008` | 功率 | Power | P = W/t | 能量 |
| 4 | `P010` | 加速度 | Acceleration | a = Δv / Δt | 运动学 |
| 5 | `P012` | 速度 | Velocity | — | 运动学 |
| 6 | `P026` | 势能 | Potential energy | — | 能量 |
| 7 | `P044` | 频率 | Frequency | — | 振动 |
| 8 | `P045` | 波长 | Wavelength | — | 振动 |
| 9 | `P049` | 波的干涉 | Wave interference | — | 波动 |
| 10 | `P059` | 温度 | Temperature | — | 能量 |
| 11 | `P060` | 热量 | Heat | — | 能量 |
| 12 | `P070` | 热传导 | Thermal conduction | — | 热传递 |
| 13 | `P073` | 电荷 | Electric charge | — | 电学 |
| 14 | `P093` | 光的偏振 | Polarization of light | — | 光的波动性 |
| 15 | `P096` | 光电效应 | Photoelectric effect | — | 量子效应 |
| 16 | `P098` | 波粒二象性 | Wave-particle duality | — | 量子力学 |

### 题目清单

| # | eval_id | 题型 | 概念 | 答案键 |
|---|---|---|---|---|
| 1 | `EVAL_P006` | 概念辨析 | 能量 | A |
| 2 | `EVAL_P012` | 概念辨析 | 速度 | A |
| 3 | `EVAL_P026` | 概念辨析 | 势能 | C |
| 4 | `EVAL_P044` | 概念辨析 | 频率 | B |
| 5 | `EVAL_P045` | 概念辨析 | 波长 | A |
| 6 | `EVAL_P049` | 概念辨析 | 波的干涉 | C |
| 7 | `EVAL_P060` | 概念辨析 | 热量 | A |
| 8 | `EVAL_P070` | 概念辨析 | 热传导 | A |
| 9 | `EVAL_P073` | 概念辨析 | 电荷 | A |
| 10 | `EVAL_P093` | 概念辨析 | 光的偏振 | A |
| 11 | `EVAL_P096` | 概念辨析 | 光电效应 | B |
| 12 | `EVAL_P004` | 幻觉陷阱 | 万有引力定律 | B |
| 13 | `EVAL_P008` | 幻觉陷阱 | 功率 | A |
| 14 | `EVAL_P010` | 幻觉陷阱 | 加速度 | B |
| 15 | `EVAL_P059` | 幻觉陷阱 | 温度 | A |
| 16 | `EVAL_P098` | 幻觉陷阱 | 波粒二象性 | A |

## 二、核心特性

### 1. 100% 离线提纯

- 全流程在本地完成：概念清洗、评测题生成、缺陷隔离、人工复核、打包，**不访问网络**。
- 原始数据来自本地 `data/raw`（只读），中间产物落盘为可复现的 JSONL。
- 打包脚本 `scripts/build_golden_v01.py` 为**确定性**执行：固定 ID 清单，运行多少次结果完全一致。
- 生成过程未调用任何模型推理接口，包内 `model_involved: false` 即为声明。

### 2. 零虚假来源

- 所有概念的 `wikidata_id` 与 `source_url` **一律为 `null`**，`license_type` 统一为 `UNVERIFIED`——
  离线批次无法联网核验来源，因此**有意留空**，绝不编造无法核实的 QID 或许可链接。
- 数据字典中的每一条字段说明均直接抽取自项目 Schema 契约文件，描述与结构同源。

### 3. 特制大模型陷阱测试点
- 5 道**幻觉陷阱题**针对阶段二实测发现的模型系统性盲点设计：题干植入一个错误前提
  （如「功率是一种能量」「加速度是运动学的一个分支学科」），正确答案必须明确否定该前提，
  干扰项则**顺从错误前提**构成有效诱导，用于暴露「把相关关系误判为种属关系」的典型幻觉。
- 11 道**概念辨析题**聚焦易混淆概念对（速度 vs 加速度、热量 vs 内能、偏振 vs 衍射等），
  四个选项同维度、均可判定真假，考验模型精确区分能力。

### 4. 人工逐题复核准入

- 本包 **16 道题全部经人工逐题验算**（题干条件完整性、选项唯一性、答案键与解析一致性），
  判定为 `ok` 方准入。已剔除阶段三确认的 9 道缺陷题，以及阶段四复核发现的双正确项 / 答案键反转等缺陷与存疑题。

### 5. 已知限制（请务必阅读）

- concepts[].parent_concept / child_concepts 为模型推断的层级边，阶段二复核实测约半数边不可信（双向闭合率仅 48.4%），仅供检索参考，不可作为权威本体。
- EVAL_P049 题干内嵌了选项文本（格式瑕疵），不影响答案键正确性。
- 公式计算题（16 道）按要求未纳入本包，也未经逐题复核。
- suspect 与 defect 题目仍留在主线数据 physics_eval_v1.jsonl 中，扩充评测集前须先修正或剔除。

## 三、数据字典

### 3.1 顶层结构

```
OpenSciGraph_Golden_v0.1.json
├── dataset / version / release / schema_version   # 标识
├── purpose                                        # 用途
├── generated_at / generated_by                    # 溯源
├── model_involved: false                          # 声明无模型推理参与
├── offline: true                                  # 声明全程离线
├── selection                                      # 选题方式与固定 ID 清单
├── human_review                                   # 复核口径与排除清单
├── sources                                        # 上游文件路径
├── counts                                         # 数量统计
├── field_order                                    # 字段顺序契约
├── data_dictionary                                # 本字段字典（自描述）
├── concepts    [16 × object]                      # 概念实体
├── eval_items  [16 × object]                      # 评测题（含内联 concept）
└── notes                                          # 完整性/质量/许可/限制
```

### 3.2 顶层字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `dataset` | string | 数据集名称。 |
| `version` | string | 数据版本号。 |
| `release` | string | 发布批次目录名。 |
| `schema_version` | string | 本包结构契约版本。 |
| `purpose` | string | 包的用途说明。 |
| `generated_at` | string | 生成时间（UTC，ISO-8601）。 |
| `generated_by` | string | 生成脚本路径。 |
| `model_involved` | boolean | 是否有模型推理参与；恒为 false。 |
| `offline` | boolean | 是否全程离线产出；恒为 true。 |
| `selection` | object | 选题方式与固定 ID 清单。 |
| `human_review` | object | 人工复核口径、准入与排除清单。 |
| `sources` | object | 上游数据与契约文件路径。 |
| `counts` | object | 数量统计。 |
| `field_order` | object | 字段顺序契约。 |
| `data_dictionary` | object | 本字段字典自身（自描述）。 |
| `concepts` | array<object> | 概念实体数组，见 concepts 字段表。 |
| `eval_items` | array<object> | 评测题数组，见 eval_item 字段表。 |
| `notes` | object | 完整性 / 质量 / 许可 / 已知限制说明。 |

### 3.3 `eval_items[]` 字段（评测题）

| 字段 | 类型 | 必填 | 可空 | 说明 |
|---|---|---|---|---|
| `eval_id` | string | 是 | 否 | 评测题编号，格式 EVAL_P + 三位数字。取值规则：EVAL_P### 与 concept_id P### 一一对应（eval_id == "EVAL_" + concept_id）。全批次 50 题对应的 concept_id 互不重复，故 eval_id 全局唯一。以脚本生成为准，模型无权改写。 |
| `concept_id` | string | 是 | 否 | 该题锚定的物理概念编号，必须存在于 data/processed/physics_concepts_v2.jsonl 中。以脚本生成为准，模型无权改写。 |
| `question_type` | string | 是 | 否 | 题型。三类的配额为 20 / 20 / 10，合计 50 题。以脚本生成为准，模型无权改写。 |
| `question` | string | 是 | 否 | 题干，简体中文。必须是完整、自洽、有唯一最佳答案的问句或判断句。 |
| `options` | array<string> | 是 | 否 | 四个选项，按 A/B/C/D 顺序排列。要求：① 恰好 4 个；② 各项非空、互不重复、长度相近；③ 不含「以上都对」「以上都不对」这类依赖其他选项的元选项。 |
| `correct_option` | string | 是 | 否 | 唯一正确选项的字母。必须与 options 数组下标对应（A=索引 0，B=索引 1，C=索引 2，D=索引 3）。 |
| `explanation` | string | 是 | 否 | 解析，说明正确选项为何成立，并指出主要干扰项的错因。简体中文。 |
| `target_hallucination_point` | string | 是 | 否 | 本题针对的模型盲点描述，例如「混淆概念与学科分类」「把相关关系误判为种属关系（动量→能量）」。即使是概念辨析题与公式题也必须填写，用于标注该题预期暴露的错误倾向。 |
| `concept` | object | 是 | 否 | 该题 concept_id 对应概念实体的内联副本，字段与 concepts[] 逐字段一致，仅供前端渲染便利；以 concepts[] 为准。 |

> **注**：上表 `question_type` 中「20 / 20 / 10，合计 50 题」是项目原始契约里 50 题全批次的配额描述。
> **本数据包只收录其中人工复核判定为 `ok` 的 11 道概念辨析题与 5 道幻觉陷阱题（共 16 道），不含公式计算题。**

### 3.4 `concepts[]` 字段（概念实体）

| 字段 | 类型 | 必填 | 可空 | 说明 |
|---|---|---|---|---|
| `concept_id` | string | 是 | 否 | 概念编号，P + 三位数字，与 config/physics_concepts_100_catalog.json 一致；以清单为准，模型无权改写。 |
| `name_zh` | string | 是 | 否 | 中文名称。允许为空字符串（缺失时保留空值，并在 missing_zh_reason 中记录原因）。 |
| `name_en` | string | 是 | 否 | 英文名称。以清单为准，模型无权改写。 |
| `wikidata_id` | string | 是 | 是 | Wikidata QID。离线批次无法核验，默认写 null，等待阶段三联网核验后回填；不得填入模型凭记忆生成的未核验值。 |
| `definition_zh` | string | 是 | 否 | 中文定义，一句话可陈述的物理定义。 |
| `formula` | string | 是 | 是 | 该概念的核心公式（如 F = ma）。无公式的概念（如惯性、能量等描述性概念）写 null。 |
| `parent_concept` | string | 是 | 是 | 上位概念的中文名，用于构建层级边。无明确上位概念时写 null。 |
| `child_concepts` | array<string> | 是 | 否 | 下位概念中文名列表，缺失时为空列表 []，不得为 null。 |
| `license_type` | string | 是 | 否 | 许可标识。本离线批次来源未核验，统一写 UNVERIFIED；来源与许可审核通过后才可替换为 CC0 / CC BY-SA 4.0 等真实值。 |
| `source_url` | string | 是 | 是 | 来源链接。离线批次不得臆造，默认写 null，等待阶段三联网核验后回填。 |
| `missing_zh_reason` | string | 是 | 是 | name_zh 为空时的原因说明；name_zh 正常时为 null。 |

### 3.5 字段顺序契约

- `eval_items[]`：`eval_id` → `concept_id` → `question_type` → `question` → `options` → `correct_option` → `explanation` → `target_hallucination_point` → `concept`
- `concepts[]`：`concept_id` → `name_zh` → `name_en` → `wikidata_id` → `definition_zh` → `formula` → `parent_concept` → `child_concepts` → `license_type` → `source_url` → `missing_zh_reason`

### 3.6 解包示例

```js
const data = await fetch('OpenSciGraph_Golden_v0.1.json').then(r => r.json());
console.log(data.counts);            // { concepts: 16, eval_items: 16, ... }
for (const item of data.eval_items) {
  console.log(item.eval_id, item.question_type, item.correct_option,
              item.concept.name_zh, item.concept.definition_zh);
}
```

```python
import json
with open('OpenSciGraph_Golden_v0.1.json', encoding='utf-8') as fh:
    data = json.load(fh)
concepts = {c['concept_id']: c for c in data['concepts']}
for it in data['eval_items']:
    assert it['concept'] == concepts[it['concept_id']]   # 内联副本一致性
```

## 四、需求反馈与联系

如需**全量数据、定制数据集或合作**，欢迎联系我们：

| 需求类型 | 说明 | 联系方式 |
|---|---|---|
| 索要全量数据 | 完整概念图谱与全量评测题（含未公开部分） | rguo3500@gmail.com |
| 定制数据集 | 指定学科领域 / 题型配比 / 语言 / 输出格式（JSONL、Parquet 等） | rguo3500@gmail.com |
| 缺陷反馈 | 发现答案键错误、概念定义不准或关系边有误 | https://github.com/rguo3500/OpenSciGraph / Issues |
| 商务与合作 | 联合评测、模型幻觉专项测评、企业内训数据 | rguo3500@gmail.com |

- **邮箱**：rguo3500@gmail.com
- **代码仓库**：https://github.com/rguo3500/OpenSciGraph
- **HuggingFace Datasets**：https://huggingface.co/datasets/guowei79/OpenSciGraph-Physics-Bench
