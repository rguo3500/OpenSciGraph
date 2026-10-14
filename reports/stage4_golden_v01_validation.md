# 阶段四定稿 · v0.1 MVP 黄金数据包校验报告

- 生成时间：2026-10-14T14:00:29Z
- 执行方式：纯数据操作（离线、不调用模型）
- 产物：`release/v0.1_mvp/OpenSciGraph_Golden_v0.1.json`
- 校验结论：**28/28 项通过**

## 校验明细

| # | 检查项 | 结论 | 说明 |
|---|---|---|---|
| 1 | 顶层必需键齐全 | ✅ PASS | 缺失=[] |
| 2 | eval_items 数量 = 16 | ✅ PASS | 实际=16 |
| 3 | concepts 数量 = 16 | ✅ PASS | 实际=16 |
| 4 | counts 与实际一致 | ✅ PASS | counts=16/16 |
| 5 | eval_id 集合与清单一致 | ✅ PASS | 实际=['EVAL_P004', 'EVAL_P006', 'EVAL_P008', 'EVAL_P010', 'EVAL_P012', 'EVAL_P026', 'EVAL_P044', 'EVAL_P045', 'EVAL_P049', 'EVAL_P059', 'EVAL_P060', 'EVAL_P070', 'EVAL_P073', 'EVAL_P093', 'EVAL_P096', 'EVAL_P098'] |
| 6 | eval_id 无重复 | ✅ PASS |  |
| 7 | 提取顺序 = 辨析在前/陷阱在后 | ✅ PASS |  |
| 8 | 题型分布 11 辨析 / 5 陷阱 / 0 公式 | ✅ PASS | 辨析=11 陷阱=5 公式=0 |
| 9 | eval_item 字段与顺序符合契约 | ✅ PASS |  |
| 10 | options 均为 4 项、非空、互不重复 | ✅ PASS |  |
| 11 | correct_option ∈ {A,B,C,D} | ✅ PASS |  |
| 12 | 内联 concept 与 concepts[] 逐字段一致 | ✅ PASS |  |
| 13 | eval_id == 'EVAL_' + concept_id | ✅ PASS |  |
| 14 | concept_id 全局唯一 | ✅ PASS |  |
| 15 | concepts[].concept_id 与题目一一对应 | ✅ PASS |  |
| 16 | concept 字段与顺序符合契约 | ✅ PASS |  |
| 17 | wikidata_id 全部为 null（零虚假来源） | ✅ PASS |  |
| 18 | source_url 全部为 null（零虚假来源） | ✅ PASS |  |
| 19 | license_type 全部为 UNVERIFIED | ✅ PASS |  |
| 20 | definition_zh 全部 >= 10 字 | ✅ PASS |  |
| 21 | 不含被隔离的缺陷题 | ✅ PASS |  |
| 22 | 全部题目人工复核判定为 ok | ✅ PASS |  |
| 23 | model_involved == false | ✅ PASS |  |
| 24 | offline == true | ✅ PASS |  |
| 25 | JSON 可序列化且往返一致 | ✅ PASS |  |
| 26 | 文本无 BOM | ✅ PASS |  |
| 27 | 换行统一为 LF | ✅ PASS |  |
| 28 | UTF-8 可解码 | ✅ PASS | 41201 字节 |

## 成品摘要

- concepts：16
- eval_items：16（概念辨析 11 / 幻觉陷阱 5）

| # | eval_id | 题型 | concept_id | 概念 | 答案键 |
|---|---|---|---|---|---|
| 1 | `EVAL_P006` | concept_distinction | P006 | 能量 | A |
| 2 | `EVAL_P012` | concept_distinction | P012 | 速度 | A |
| 3 | `EVAL_P026` | concept_distinction | P026 | 势能 | C |
| 4 | `EVAL_P044` | concept_distinction | P044 | 频率 | B |
| 5 | `EVAL_P045` | concept_distinction | P045 | 波长 | A |
| 6 | `EVAL_P049` | concept_distinction | P049 | 波的干涉 | C |
| 7 | `EVAL_P060` | concept_distinction | P060 | 热量 | A |
| 8 | `EVAL_P070` | concept_distinction | P070 | 热传导 | A |
| 9 | `EVAL_P073` | concept_distinction | P073 | 电荷 | A |
| 10 | `EVAL_P093` | concept_distinction | P093 | 光的偏振 | A |
| 11 | `EVAL_P096` | concept_distinction | P096 | 光电效应 | B |
| 12 | `EVAL_P004` | hallucination_trap | P004 | 万有引力定律 | B |
| 13 | `EVAL_P008` | hallucination_trap | P008 | 功率 | A |
| 14 | `EVAL_P010` | hallucination_trap | P010 | 加速度 | B |
| 15 | `EVAL_P059` | hallucination_trap | P059 | 温度 | A |
| 16 | `EVAL_P098` | hallucination_trap | P098 | 波粒二象性 | A |

## 附：HuggingFace `datasets` 分片校验

主交付文件是**单个 JSON 对象**（含 `concepts[]` / `eval_items[]` 两个嵌套数组），
HF 的 json loader 面向 JSONL 或 JSON 数组，**无法**把嵌套对象展开成多行；
因此额外导出 `eval_items.jsonl`（16 行）与 `concepts.jsonl`（16 行）两个扁平分片，
两者均由同一 payload 派生，与主包逐行一致。

结论：**6/6 项通过**

| # | 检查项 | 结论 | 说明 |
|---|---|---|---|
| 1 | eval_items.jsonl 行数 = 16 | ✅ PASS | 16 |
| 2 | concepts.jsonl 行数 = 16 | ✅ PASS | 16 |
| 3 | eval_items.jsonl 与主包逐行一致 | ✅ PASS | — |
| 4 | concepts.jsonl 与主包逐行一致 | ✅ PASS | — |
| 5 | 分片均为 UTF-8 无 BOM | ✅ PASS | — |
| 6 | pyarrow 可据分片建表（datasets 可加载） | ✅ PASS | — |
