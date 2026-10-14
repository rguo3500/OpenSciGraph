# OpenSciGraph v0.1 MVP · 社区宣发文案套件

> **给 Owner 的使用说明（发帖前请读，发布时整段删除）**
>
> 1. 本文档仅供复制粘贴，**不是**数据集的一部分，无需上传到 HuggingFace 仓库。
> 2. 发帖前请确认 HF 仓库**已真实上架**（先跑 `scripts/upload_to_hf.py`），
>    否则文中的数据集链接会 404，效果反噬。
> 3. 文中所有数字（50 题 / 9 道隔离 / 6 道新缺陷 / 48.4% 闭合率 / 28 项校验）均取自项目实测报告，
>    可放心引用；**不要再往上加码**，本文案的说服力恰恰来自「敢自曝短板」。
> 4. 邮箱 `rguo3500@gmail.com` 为公开联系方式，若不想暴露个人邮箱，发帖前替换为公司/项目专用邮箱。
> 5. HuggingFace 仓库 ID 已定案为 `guowei79/OpenSciGraph-Physics-Bench`（2026-10-14 上架，公开）。
>    沿革：原定的 `OpenSciGraph` 组织在 HF 上不存在；备选的 `ruguo3500` 组织虽为账号所属，
>    但所用细粒度 token 未获该组织写权限（403），故最终落在 token 唯一可写的 `guowei79` 命名空间。
> 6. 代码仓库链接为 `https://github.com/rguo3500/OpenSciGraph`（2026-10-14 更新）。
>    ⚠️ 该仓库**截至更新时为 404**（用户 rguo3500 存在，仓库尚未创建）。发帖前请先建仓，

---

## 一、V2EX 宣发帖

**建议节点**：`分享创造`（主）+ `AI`（备）
**建议标签**：`开源` `AI` `数据集` `大模型`

### 标题

```
【开源】被大模型假数据坑怕了，我们做了一套 100% 离线清洗的物理图谱 + 防幻觉 Bench (v0.1 MVP)
```

### 正文

```
先说结论：我们让本地跑的大模型生成了 50 道物理评测题，最后只敢放出 16 道。
剩下 34 道的下场是：9 道隔离、16 道公式题未复核、9 道（6 缺陷 + 3 存疑）留在主线待修。

这篇帖子主要想聊的不是「我们做了个数据集」，而是「我们是怎么发现自己的数据是垃圾的」。
如果你也在用大模型批量造数据，可能能省掉一些返工。

---

■ 起因

我们在做一个物理知识图谱项目（OpenSciGraph），需要一个能测大模型物理知识可靠性的
Benchmark。为了 100% 离线可控，用的是本地 Ollama + Qwen2.5-7B-Instruct (Q5_K_M)，
跑 100 条概念清洗大约 194 秒、42 tok/s，全程不联网。

生成环节看起来很顺：加了 JSON 语法约束，100 条全部通过结构校验，Schema 合规率 100%。
然后我们做了一次「盲测自洽」——把每条记录的定义、关系反过来让模型再判一遍。
自洽率 74%，加一轮修复后到 86%。

看起来还行？**问题恰恰出在这里。**

---

■ 踩到的坑：盲测自洽 ≠ 物理正确

我们逐题人工验算了一遍，结果很难看：

- `EVAL_P084`（洛伦兹力题）：选项 A 写的是「洛伦兹力作用于静止电荷」，
  解析里却写「正确选项为 A，洛伦兹力作用于运动电荷」——**答案键和选项直接相反**，
  而且四个选项**没有一个是对的**。
- `EVAL_P051`（驻波题）：题目问「适用于驻波而不能用于共振」，答案键却指向共振的特征，
  解析里模型自己都写着「选项 C 描述的是共振的特征」——然后仍然选了 C。
- `EVAL_P037 / P063 / P086 / P080`：**双正确项**。比如 P086 里，
  「法拉第定律」和「楞次定律的正确表述」两个选项同时成立。

结论很反直觉：**结构校验拦不住语义错误，盲测自洽也拦不住。**
自洽的 86% 里，混着一批「前后一致地错」的题——模型用错误的前提自洽地推导，
过程完全说得通。这类缺陷只有人工验算或符号计算能发现。

算下来，我们 41 道候选题里的缺陷率在 24%–33%，比一开始估计的 18% 高得多。

所以最后我们做了三件事：
① 把确认有害的 9 道隔离进 quarantine（保留审计字段，可追溯）；
② 对剩余题目逐题人工验算，又抓出新增缺陷，全部剔除；
③ 只放行判定为「唯一正确答案成立、干扰项可判定为假」的题目——**16 道**。

上线前跑了 28 项结构校验，100% PASS，另用独立脚本交叉复核过一遍。

---

■ 数据集里有什么

16 组基础物理概念图谱 + 16 道防幻觉 Benchmarks：

- **概念图谱 16 条**：中英文名、中文定义、核心公式、上位/下位关系、许可标识；
- **概念辨析题 11 道**：速度 vs 加速度、热量 vs 内能、偏振 vs 衍射、波长 vs 波速……
  四个选项同维度、都能判定真假，考的是精确区分；
- **AI 幻觉陷阱题 5 道**：这是我认为最有意思的部分。

陷阱题的设计原理是：题干**植入一个错误前提**，比如「功率是一种能量」
「加速度是运动学的一个分支学科」「万有引力定律就是一种力」。
正确答案必须明确否定这个前提，而另外 3 个干扰项**顺着错误前提往下走**。

这类题专门用来暴露大模型的一个系统性盲点：**把「相关关系」误判为「种属关系」**。
普通的 QA 数据集测不出来，因为那些题不会故意给模型下套。

---

■ 两个我们比较在意的点

**1. 零虚假来源**

所有概念的 `wikidata_id` 和 `source_url` **一律是 `null`**，`license_type` 统一 `UNVERIFIED`。
离线批次没法联网核验来源，那就不填——**我们没有让模型凭记忆糊一个 QID 上去**。

说实话这个决定让数据「看起来不完整」，但我们宁愿不完整，也不要假的可验证字段。
「看起来像真的」和「是真的」之间的差距，正是这个项目想解决的问题。

**2. 主动披露：我们连自己的关系边都不信**

概念之间的 `parent_concept` / `child_concepts` 是模型推断出来的。
我们做了一次双向闭合检查（A 的下位里有 B，B 的上位是不是 A），
**闭合率只有 48.4%——大约一半的边是不可信的。**

这批边我们保留在数据里了，因为对检索还有点参考价值，但 README 里写得很清楚：
**不可作为权威本体使用。**

（也正因为这个数字太难看，一度考虑过直接删掉关系边只留概念。
最后决定留着 + 显著标注，比删掉更诚实。）

---

■ 已知限制（先说清楚，免得你踩坑）

1. **样本量只有 16 组**，适合做冒烟测试和展示，**统计显著性有限**，别拿它下结论说某个模型多强多弱；
2. 关系边闭合率 48.4%，参考可以，当本体不行；
3. 许可 `UNVERIFIED`：没联网核验来源，**使用前请自行评估合规风险**，商用建议先联系我们；
4. 同批次还有 16 道公式计算题没纳入也没复核，不建议直接并进评测。

---

■ 链接

- HuggingFace 数据集：https://huggingface.co/datasets/guowei79/OpenSciGraph-Physics-Bench
- 代码仓库：https://github.com/rguo3500/OpenSciGraph

加载就 3 行：

    from datasets import load_dataset
    bench = load_dataset("guowei79/OpenSciGraph-Physics-Bench", "eval_items", split="train")
    print(bench[0])

（国内网络 `huggingface.co` 可能不通，下载可以先 `set HF_ENDPOINT=https://hf-mirror.com`。）

---

■ 最后

如果你在做 LLM 数据质量、评测集构建，或者对大模型幻觉感兴趣，非常欢迎交流：

- 发现答案键错了、概念定义不准、关系边离谱 → 直接开 Issue
- 想要全量数据 / 定制数据集（指定学科、题型配比、格式）→ 发邮件给 rguo3500@gmail.com
- 想聊聊「怎么发现自己的数据是垃圾的」→ 评论区就行

下一步打算把公式计算题那一批也做完人工复核——那批的盲测自洽率只有 60%，
估计问题更多，做完了再来更新。

感谢看到这里。
```

---

## 二、英文简版（GitHub Release / Reddit / Discord）

> **Reddit 注意事项**：
> - `r/MachineLearning` 必须在标题前加 `[P]`（Project）标签，且需遵守自我推广频率限制；
> - `r/LocalLLaMA` 对「本地模型 + 数据集」题材接受度高，可直接发，但**不要在多个 subreddit 同时刷同一篇**；
> - 标题建议保留「我们丢掉了自己 40% 的生成数据」这个钩子，它比「我们发布了一个数据集」有效得多。

### Reddit / r/LocalLLaMA 版

**标题**

```
[P] We threw away 40% of the physics questions our own LLM generated — here's the 16 that survived (offline-curated benchmark)
```

**正文**

```
We built OpenSciGraph to measure how reliably LLMs "know" basic physics. To keep it fully
offline and reproducible, we generated the benchmark with a local Qwen2.5-7B-Instruct
(Q5_K_M, ~42 tok/s, no network).

Generation looked fine: 100% schema compliance, 74% blind self-consistency, 86% after one
repair pass.

Then we actually did the physics by hand, and it got ugly:

- EVAL_P084 (Lorentz force): option A says "acts on a *stationary* charge", the explanation
  says "correct answer is A, it acts on a *moving* charge". The answer key contradicts the
  option text — and none of the four options is correct.
- EVAL_P051 (standing waves): the question asks for a property of standing waves, the key
  points at a resonance property. The model's own explanation admits this ("option C
  describes a resonance feature") and still selects C.
- Four more with two simultaneously-correct options.

The lesson: **structural validation and blind self-consistency do not catch semantic errors.**
A model can be confidently, internally-consistently wrong. Defect rate across our candidate
pool was 24–33%, well above our initial 18% estimate.

So we quarantined 9, hand-verified the rest, and released only the 16 questions where a
unique correct answer actually holds.

**What's in it**

- 16 physics concept entities (bilingual name, definition, formula, parent/child relations)
- 11 concept-distinction items (velocity vs acceleration, heat vs internal energy,
  polarization vs diffraction, ...)
- **5 hallucination-trap items** — these are the interesting part. Each question plants a
  *false premise* ("power is a form of energy", "acceleration is a subfield of kinematics")
  in the prompt. The correct answer must reject that premise; the three distractors
  *go along with it*. This specifically probes a systemic failure mode: treating a
  correlated relation as a taxonomic (is-a) relation.

**Two things we're opinionated about**

1. Zero fabricated provenance. Every `wikidata_id` and `source_url` is `null` and
   `license_type` is `UNVERIFIED`, because we couldn't verify sources offline. We did not
   let the model hallucinate plausible-looking QIDs. Incomplete > fake.
2. We don't trust our own graph edges. `parent_concept`/`child_concepts` are
   model-inferred. A bidirectional closure check came back at **48.4%** — roughly half the
   edges are unreliable. They're kept for retrieval hints and explicitly flagged as
   **not authoritative**.

**Honest limitations**

- n = 16. Fine for smoke tests and demos, **not statistically meaningful** as a model ranking.
- Graph edges: 48.4% closure, use with care.
- License `UNVERIFIED` — assess compliance yourself before commercial use.
- 16 formula-reasoning items from the same batch were never hand-reviewed and are excluded.

**Links**

- Dataset: https://huggingface.co/datasets/guowei79/OpenSciGraph-Physics-Bench
- Code: https://github.com/rguo3500/OpenSciGraph

```
from datasets import load_dataset
bench = load_dataset("guowei79/OpenSciGraph-Physics-Bench", "eval_items", split="train")
print(bench[0])
```

Feedback, wrong answer keys, and requests for the full/custom dataset are all welcome:
rguo3500@gmail.com
```

### Discord / Slack 短版（AI 开发者频道）

```
📐 OpenSciGraph v0.1 — a small, offline-curated physics benchmark, and a cautionary tale.

We generated 50 physics questions with a local Qwen2.5-7B, then hand-checked them.
Only 16 survived. 9 had to be quarantined; we found answer keys that contradicted their
own options, and questions with two correct answers.

Takeaway worth repeating: blind self-consistency ≠ physical correctness. 86%
self-consistent, still ~30% defective.

What's inside: 16 concept entities + 16 items (11 concept-distinction, 5 hallucination-traps).
The trap items plant a false premise and make the distractors agree with it — designed to
expose "correlation mistaken for taxonomy" errors.

Zero fabricated provenance: all wikidata_id / source_url are null on purpose.
Also disclosed up front: our graph edges only reach 48.4% bidirectional closure.
n=16 — good for smoke tests, not for leaderboards.

📦 https://huggingface.co/datasets/guowei79/OpenSciGraph-Physics-Bench
💬 Full data / custom datasets: rguo3500@gmail.com
```

### GitHub Release Notes 版

```markdown
## OpenSciGraph Golden Dataset v0.1 (MVP)

First public sample of OpenSciGraph — an offline-curated physics knowledge graph plus an
anti-hallucination benchmark.

### Contents
- **16** physics concept entities (bilingual names, definitions, formulas, hierarchical relations)
- **16** benchmark items: 11 concept-distinction + **5 hallucination-trap**
- Fully offline, deterministic build (`scripts/build_golden_v01.py`), no model inference involved
- 28/28 structural validation checks passing

### Highlights
- **Hallucination-trap items** plant a false premise in the prompt and require the model to
  reject it, while all three distractors comply with it.
- **Zero fabricated provenance** — `wikidata_id` / `source_url` are `null` by design.
- Every admitted item was **hand-verified** for a unique correct answer.

### Known limitations
- Released after quarantining 9 defective items and excluding 9 more found during manual
  review. Defect rate in the original pool: 24–33%.
- Graph edges show only **48.4%** bidirectional closure — not authoritative.
- n = 16: suitable for smoke testing, not for statistically meaningful model ranking.
- `license_type = UNVERIFIED`.

### Links
- 🤗 Dataset: https://huggingface.co/datasets/guowei79/OpenSciGraph-Physics-Bench
- 💻 Code: https://github.com/rguo3500/OpenSciGraph
- ✉️ Full / custom datasets: rguo3500@gmail.com
```

---

## 三、发帖节奏建议（可选）

| 渠道 | 建议时机 | 备注 |
|---|---|---|
| V2EX `分享创造` | 首发 | 中文社区反馈最快，先在这里接一轮吐槽，改完再发英文 |
| GitHub Release | 与 V2EX 同日 | 作为所有渠道的权威落点 |
| HuggingFace 数据集页 | 上架后立即 | README 即数据集卡，自带质量证明与加载代码 |
| Reddit `r/LocalLLaMA` | 首发后 1–2 天 | 用英文简版；避开发帖高峰（UTC 晚间人多） |
| Discord 社群 | 与 Reddit 同日 | 用短版，别贴长文 |
| `r/MachineLearning` | 最后 | 需 `[P]` 标签，审核更严，建议等前几轮反馈后再发 |

**统一提醒**：所有渠道都保留「主动披露 48.4% 闭合率」这一段。
这是本文案的信任锚点——愿意自曝短板的技术帖，比只讲成绩的推广帖更容易拿到真实反馈。
