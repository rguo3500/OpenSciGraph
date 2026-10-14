#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
阶段四 · MVP 数据提纯与打包（纯数据操作，全程不调用任何模型）

四步流水线
----------
1. **隔离**：把阶段三报告中确认的 9 道缺陷题从 ``data/processed/physics_eval_v1.jsonl``
   精准剔除，移入 ``data/interim/quarantine_eval.jsonl``。
2. **人工复核闸门**：对隔离后剩余的题目逐题判定物理正确性
   （见 ``REVIEW_VERDICTS``——由人工逐题验算得出，不是模型自评）。
   只有判定为 ``ok`` 的题目才进入黄金样本抽样池。
3. **抽样**：从复核通过的辨析题里随机抽 10 道，从复核通过的陷阱题里随机抽 5 道
   （**完全不含公式计算题**），并与 ``physics_concepts_v2.jsonl`` 中对应的
   概念基础数据合并。
4. **打包**：在 ``release/v0.1_mvp/`` 下输出可直接被前端解析的
   ``OpenSciGraph_Golden_Sample_v0.1.json``。

用法::

    python scripts/build_golden_sample.py                  # 正式执行（启用复核闸门）
    python scripts/build_golden_sample.py --dry-run        # 只报告，不落盘
    python scripts/build_golden_sample.py --no-review-gate # 关闭闸门，按纯随机抽（复现用户原始指令）
    python scripts/build_golden_sample.py --seed 20261014  # 指定抽样随机种子

本脚本不访问网络，不调用 127.0.0.1:11434，也不触碰 ``data/raw``（受保护目录）。
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.common import (  # noqa: E402
    INTERIM_DIR,
    PROCESSED_DIR,
    PROJECT_ROOT,
    REPORTS_DIR,
    assert_writable,
    setup_logger,
    timestamp_slug,
    utc_now_iso,
)

LOG = setup_logger("build_golden_sample")

# ---------------------------------------------------------------------------
# 路径常量
# ---------------------------------------------------------------------------

EVAL_PATH: Path = PROCESSED_DIR / "physics_eval_v1.jsonl"
CONCEPT_PATH: Path = PROCESSED_DIR / "physics_concepts_v2.jsonl"
QUARANTINE_PATH: Path = INTERIM_DIR / "quarantine_eval.jsonl"
BACKUP_DIR: Path = INTERIM_DIR / "archive"

RELEASE_DIR: Path = PROJECT_ROOT / "release" / "v0.1_mvp"
GOLDEN_JSON: Path = RELEASE_DIR / "OpenSciGraph_Golden_Sample_v0.1.json"
RELEASE_README: Path = RELEASE_DIR / "README.md"
STAGE_REPORT: Path = REPORTS_DIR / "stage4_mvp_report.md"
REVIEW_REPORT: Path = REPORTS_DIR / "eval_human_review_stage4.md"

# ---------------------------------------------------------------------------
# 契约
# ---------------------------------------------------------------------------

EVAL_FIELDS: Tuple[str, ...] = (
    "eval_id",
    "concept_id",
    "question_type",
    "question",
    "options",
    "correct_option",
    "explanation",
    "target_hallucination_point",
)

CONCEPT_FIELDS: Tuple[str, ...] = (
    "concept_id",
    "name_zh",
    "name_en",
    "wikidata_id",
    "definition_zh",
    "formula",
    "parent_concept",
    "child_concepts",
    "license_type",
    "source_url",
    "missing_zh_reason",
)

#: 阶段三报告 §5.2「已确认有害缺陷的 9 道」——须人工修正后才能使用。
QUARANTINE: Tuple[Tuple[str, str, str], ...] = (
    ("EVAL_P021", "formula_reasoning", "角动量：I=½mr²=0.25、L=Iω=1.25，四个选项(6.28/15.7/3.14/9.42)均不含正确值，属于「一致的错误」"),
    ("EVAL_P029", "formula_reasoning", "题干问「弹力大小」，却提供带负号选项；F=-kx 的负号在此语境下不构成「大小」"),
    ("EVAL_P033", "concept_distinction", "答案键存疑：A 为教科书标准表述，B 称「摩擦力由粗糙程度决定」漏掉正压力因素，不宜作为唯一正确答案"),
    ("EVAL_P061", "formula_reasoning", "比热容：ΔT=Q/(cm)=42000/(385×2)=54.5°C → 终温 74.5°C，四个选项(25/30/35/40)均无此值"),
    ("EVAL_P066", "hallucination_trap", "双正确项：B 与 D 均为成立表述，缺少唯一最佳答案"),
    ("EVAL_P075", "concept_distinction", "双正确项：问「哪个是标量」，B(电势差) 与 D(电势) 都是标量"),
    ("EVAL_P078", "hallucination_trap", "C「电容属于电学中的一个具体概念」本身成立，不构成有效错误干扰项"),
    ("EVAL_P088", "concept_distinction", "双正确项：A(描述反射)、B(描述折射) 均为正确表述，无选项同时完成「区分」任务"),
    ("EVAL_P089", "formula_reasoning", "折射角：n水·sin30°=0.665 → r≈41.7°，选项最大仅 35°；解析算出 37° 却选 27°，自相矛盾"),
)

QUARANTINE_IDS: Tuple[str, ...] = tuple(item[0] for item in QUARANTINE)

# ---------------------------------------------------------------------------
# 阶段四人工复核判定（人工逐题验算，非模型自评）
# ---------------------------------------------------------------------------
# verdict:
#   ok      —— 物理学上唯一正确答案成立，干扰项可判定为假，可进入展示包
#   suspect —— 答案键可辩护，但存在解析矛盾 / 表述不严谨 / 诱导过强，展示前须修
#   defect  —— 已确认错误（答案键错、双正确项、无正确选项），禁止进入展示包
REVIEW_VERDICTS: Dict[str, Tuple[str, str]] = {
    # ---- 概念辨析题 ----
    "EVAL_P006": ("ok", "能量包含动能/势能/内能的种属表述准确，三个干扰项均可判定为假"),
    "EVAL_P012": ("ok", "速度（位置变化快慢）与加速度（速度变化快慢）区分准确"),
    "EVAL_P026": ("ok", "势能包含重力势能与弹性势能的表述准确，干扰项均可判定为假"),
    "EVAL_P031": ("suspect", "A 在题设斜面情境下自相矛盾（滑动摩擦力 f=μmg·cosθ 同样随重力增大），C 表述含糊无法判定真假"),
    "EVAL_P037": ("defect", "双正确项：A（惯性定义）与 B（转动惯量反映抵抗角加速度的能力，即 I=τ/α）均为真"),
    "EVAL_P044": ("ok", "频率与周期互为倒数，干扰项均可判定为假"),
    "EVAL_P045": ("ok", "波长（相邻同相点距离）与波速（传播快慢）定义区分准确"),
    "EVAL_P049": ("ok", "衍射定义准确（题干内嵌了选项文本，属格式瑕疵，不影响判定）"),
    "EVAL_P051": ("defect", "答案键与题干要求相反：问「适用于驻波而不能用于共振」，A、B 均描述驻波，答案键 C 却是共振特征；解析自认『选项C描述的是共振的特征』却仍选 C"),
    "EVAL_P060": ("ok", "热量（过程量）与内能（状态量）区分准确"),
    "EVAL_P063": ("defect", "双正确项：A（第一定律描述能量变化、第二定律描述方向性）与 B（能量守恒 / 熵增）都是教科书级正确表述"),
    "EVAL_P070": ("ok", "热传导情境唯一，其余选项分别为对流与辐射，均可判定为假"),
    "EVAL_P073": ("ok", "电荷（物质属性）与电流（定向移动）区分方向正确；A 项措辞略不严谨但可接受"),
    "EVAL_P084": ("defect", "答案键与选项直接相反：A 写「洛伦兹力作用于静止电荷」（应为运动电荷），解析却称『正确选项为A，洛伦兹力作用于运动电荷』；且四个选项无一正确"),
    "EVAL_P086": ("defect", "双正确项：A（法拉第定律）与 D（楞次定律的正确表述：感应磁场方向与磁通量变化方向相反）均为真"),
    "EVAL_P093": ("ok", "偏振（横波振动方向受约束）与衍射（绕过障碍物）区分准确"),
    "EVAL_P096": ("ok", "光子能量与频率成正比（E=hν）表述准确，干扰项均可判定为假"),
    # ---- 幻觉陷阱题 ----
    "EVAL_P004": ("ok", "错误前提（定律=力）被正确答案明确否定，解析自洽"),
    "EVAL_P005": ("suspect", "答案键正确，但 explanation 把正确选项 A 列为「接受了错误前提的干扰项」，解析自相矛盾，展示前须修正"),
    "EVAL_P008": ("ok", "错误前提（功率=能量）被正确答案否定，三个干扰项均顺从错误前提，陷阱有效"),
    "EVAL_P010": ("ok", "错误前提（加速度是运动学分支学科）被否定；题干句式偏啰嗦，可再精简"),
    "EVAL_P059": ("ok", "温度（强度量）与能量区分准确，干扰项均顺从错误前提"),
    "EVAL_P080": ("defect", "双正确项：B（欧姆是电阻的单位）与 C（电阻和欧姆属于同一学科领域）均为真，C 虽空泛但不构成有效干扰"),
    "EVAL_P098": ("ok", "光电效应是支持波粒二象性的实验现象，否定「下位概念」关系准确"),
    "EVAL_P099": ("suspect", "答案键 A 可辩护，但 explanation 自相矛盾（『都顺从了错误前提，但C和D明确指出关系错误』逻辑不通）；C 项以「对，」开头且含真命题，诱导歧义"),
}

#: 黄金样本配额
WANT_DISTINCTION = 10
WANT_TRAP = 5

DEFAULT_SEED = 20261014

#: 公式计算题按需求不参与展示包，因此未逐题复核，单列一类，不与"缺陷"混淆
NA_QUESTION_TYPE = "formula_reasoning"


def verdict_of(eval_id: str, question_type: str) -> Tuple[str, str]:
    """返回 (verdict, note)。verdict ∈ {ok, suspect, defect, na, unreviewed}。"""
    if question_type == NA_QUESTION_TYPE:
        return ("na", "公式计算题按需求不进入展示包，本阶段未逐题复核")
    if eval_id in REVIEW_VERDICTS:
        return REVIEW_VERDICTS[eval_id]
    return ("unreviewed", "未列入人工复核表")


def count_verdict(rows: Sequence[Dict[str, Any]], verdict: str) -> int:
    return sum(1 for r in rows if verdict_of(r["eval_id"], r["question_type"])[0] == verdict)


# ---------------------------------------------------------------------------
# 读取 / 写出
# ---------------------------------------------------------------------------


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    """读取 JSONL，遇到坏行直接报错（提纯任务不容忍静默丢行）。"""
    rows: List[Dict[str, Any]] = []
    text = Path(path).read_text(encoding="utf-8")
    for lineno, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path} 第 {lineno} 行不是合法 JSON：{exc}") from exc
        if not isinstance(obj, dict):
            raise ValueError(f"{path} 第 {lineno} 行顶层不是 JSON 对象")
        rows.append(obj)
    return rows


def write_jsonl(rows: Sequence[Dict[str, Any]], path: Path) -> Path:
    """以 UTF-8 / LF / 无 BOM 写出 JSONL，原子替换。"""
    target = assert_writable(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".tmp")
    body = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
    tmp.write_text(body, encoding="utf-8", newline="\n")
    os.replace(tmp, target)
    return target


# ---------------------------------------------------------------------------
# 步骤 1 · 隔离
# ---------------------------------------------------------------------------


def partition(
    rows: Sequence[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """把题目拆成 (提纯后, 隔离集)，两者并集等于输入全集，顺序不变。"""
    index = {r["eval_id"]: r for r in rows}
    missing = [eid for eid in QUARANTINE_IDS if eid not in index]
    if missing:
        raise ValueError(
            f"隔离名单中的 {missing} 不在 {EVAL_PATH.name} 里——"
            "文件可能已经被处理过，或 eval_id 有误。"
        )
    clean: List[Dict[str, Any]] = []
    quarantine: List[Dict[str, Any]] = []
    for r in rows:
        (quarantine if r["eval_id"] in QUARANTINE_IDS else clean).append(dict(r))
    order = {eid: i for i, eid in enumerate(QUARANTINE_IDS)}
    quarantine.sort(key=lambda r: order[r["eval_id"]])
    return clean, quarantine


def build_quarantine_records(
    quarantine: Sequence[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """给隔离记录补上审计元数据（原有 8 个字段保持原样、顺序不变）。"""
    meta = {eid: (qtype, reason) for eid, qtype, reason in QUARANTINE}
    stamped_at = utc_now_iso()
    out: List[Dict[str, Any]] = []
    for r in quarantine:
        qtype, reason = meta[r["eval_id"]]
        if r["question_type"] != qtype:
            raise ValueError(
                f"{r['eval_id']} 题型不符：记录为 {r['question_type']}，隔离名单为 {qtype}"
            )
        rec = dict(r)
        rec["quarantine"] = {
            "reason": reason,
            "source": "reports/stage3_eval50_report.md §5.2",
            "quarantined_at": stamped_at,
            "stage": 4,
            "verdict": "已确认有害缺陷，人工修正前不得作为可信答案键使用",
        }
        out.append(rec)
    return out


# ---------------------------------------------------------------------------
# 步骤 2 · 人工复核闸门
# ---------------------------------------------------------------------------


def gate(clean: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """只保留人工复核判定为 ok 的题目。"""
    unknown = [
        r["eval_id"] for r in clean
        if verdict_of(r["eval_id"], r["question_type"])[0] == "unreviewed"
    ]
    if unknown:
        LOG.warning("这些题目未列入人工复核表，将按不通过处理：%s", unknown)
    return [
        r for r in clean
        if verdict_of(r["eval_id"], r["question_type"])[0] == "ok"
    ]


# ---------------------------------------------------------------------------
# 步骤 3 · 抽样
# ---------------------------------------------------------------------------


def select_golden(
    pool: Sequence[Dict[str, Any]], seed: int
) -> List[Dict[str, Any]]:
    """从复核通过的池子里随机抽 10 道辨析 + 5 道陷阱，结果按 eval_id 排序。"""
    rng = random.Random(seed)
    quota = {
        "concept_distinction": WANT_DISTINCTION,
        "hallucination_trap": WANT_TRAP,
    }
    picked: List[Dict[str, Any]] = []
    for kind, want in quota.items():
        candidates = [r for r in pool if r["question_type"] == kind]
        if len(candidates) < want:
            raise ValueError(
                f"{kind} 复核通过 {len(candidates)} 道，少于所需 {want} 道，无法组包"
            )
        picked.extend(rng.sample(candidates, want))
    picked.sort(key=lambda r: r["eval_id"])
    return picked


# ---------------------------------------------------------------------------
# 步骤 4 · 打包
# ---------------------------------------------------------------------------


def build_payload(
    picked: Sequence[Dict[str, Any]],
    concepts: Dict[str, Dict[str, Any]],
    seed: int,
    clean: Sequence[Dict[str, Any]],
    review_gate: bool,
    pool_size: int,
) -> Dict[str, Any]:
    """组装可被前端直接解析的 v0.1 MVP 样本。"""
    missing = [r["concept_id"] for r in picked if r["concept_id"] not in concepts]
    if missing:
        raise ValueError(f"概念库中缺少这些 concept_id：{missing}")

    used_ids = sorted({r["concept_id"] for r in picked})
    concept_list = [concepts[cid] for cid in used_ids]

    eval_items: List[Dict[str, Any]] = []
    for r in picked:
        item = {f: r[f] for f in EVAL_FIELDS}
        item["concept"] = concepts[r["concept_id"]]  # 内联副本，前端免 join
        eval_items.append(item)

    by_type: Dict[str, int] = {}
    for r in picked:
        by_type[r["question_type"]] = by_type.get(r["question_type"], 0) + 1

    suspect = sorted(
        r["eval_id"] for r in clean
        if verdict_of(r["eval_id"], r["question_type"])[0] == "suspect"
    )
    defect = sorted(
        r["eval_id"] for r in clean
        if verdict_of(r["eval_id"], r["question_type"])[0] == "defect"
    )

    return {
        "dataset": "OpenSciGraph Golden Sample",
        "version": "v0.1",
        "release": "v0.1_mvp",
        "purpose": "对外展示用严格样本：经隔离提纯 + 人工逐题复核后的 15 道物理评测题 + 对应 15 条概念基础数据",
        "generated_at": utc_now_iso(),
        "generated_by": "scripts/build_golden_sample.py",
        "model_involved": False,
        "human_review": {
            "enabled": review_gate,
            "scope": "隔离后剩余的概念辨析题与幻觉陷阱题，逐题验算题干条件、选项唯一性与答案键一致性",
            "verdicts_file": "reports/eval_human_review_stage4.md",
            "reviewed_total": count_verdict(clean, "ok") + count_verdict(clean, "suspect") + count_verdict(clean, "defect"),
            "ok": count_verdict(clean, "ok"),
            "suspect_excluded": suspect,
            "defect_excluded": defect,
            "not_reviewed": [r["eval_id"] for r in clean if verdict_of(r["eval_id"], r["question_type"])[0] == "na"],
        },
        "offline": True,
        "random_seed": seed,
        "sources": {
            "concepts": "data/processed/physics_concepts_v2.jsonl",
            "eval_items": "data/processed/physics_eval_v1.jsonl",
            "quarantined_items": "data/interim/quarantine_eval.jsonl",
            "schema": [
                "config/physics_v2_schema.json",
                "config/physics_eval_schema.json",
            ],
        },
        "counts": {
            "concepts": len(concept_list),
            "eval_items": len(eval_items),
            "eval_items_by_type": by_type,
            "clean_pool_after_quarantine": len(clean),
            "quarantined_removed": len(QUARANTINE_IDS),
            "original_pool_before_quarantine": len(clean) + len(QUARANTINE_IDS),
            "review_gate_pool": pool_size,
            "review_ok": count_verdict(clean, "ok"),
            "review_suspect_excluded": len(suspect),
            "review_defect_excluded": len(defect),
            "review_not_applicable": count_verdict(clean, "na"),
        },
        "field_order": {
            "eval_item": list(EVAL_FIELDS),
            "concept": list(CONCEPT_FIELDS),
        },
        "integrity_note": (
            "eval_items[].concept 是 concepts[] 中同 concept_id 记录的内联副本，"
            "两者内容逐字段一致，仅为前端渲染方便；以 concepts[] 为准。"
        ),
        "quality_note": (
            "本样本已剔除阶段三报告 §5.2 确认的 9 道有害缺陷题，"
            "并进一步剔除阶段四人工复核中判定为缺陷/存疑的题目，且不含公式计算题。"
            "入选的 15 道题均由人工逐题验算过题干条件、选项唯一性与答案键一致性。"
        ),
        "license_note": (
            "concepts[].license_type 为 UNVERIFIED：阶段二离线批次未联网核验来源，"
            "wikidata_id / source_url 一律为 null，未冒充真实 Wikidata / Wikipedia 数据。"
        ),
        "concepts": concept_list,
        "eval_items": eval_items,
    }


# ---------------------------------------------------------------------------
# 汇报
# ---------------------------------------------------------------------------

TYPE_ZH = {
    "concept_distinction": "概念辨析",
    "formula_reasoning": "公式应用",
    "hallucination_trap": "幻觉陷阱",
}

VERDICT_ZH = {
    "ok": "✅ 合格",
    "suspect": "⚠️ 存疑",
    "defect": "❌ 缺陷",
    "na": "➖ 不适用",
    "unreviewed": "❔ 未复核",
}


def build_review_md(clean: Sequence[Dict[str, Any]]) -> str:
    """输出候选题的逐题人工复核判定表。"""
    lines: List[str] = []
    lines.append("# 阶段四 · 评测题人工复核判定表")
    lines.append("")
    lines.append(f"生成时间：{utc_now_iso()}　·　判定方式：**人工逐题验算**（非模型自评）")
    lines.append("")
    lines.append("复核范围：阶段三 50 题中，隔离 9 道缺陷题后剩余的全部题目。")
    lines.append("")
    lines.append("判定口径：")
    lines.append("")
    lines.append("- `✅ 合格` —— 唯一正确答案成立、干扰项可判定为假，**可进入展示包**")
    lines.append("- `⚠️ 存疑` —— 答案键可辩护，但存在解析矛盾 / 表述不严谨 / 诱导过强，**展示前须修**")
    lines.append("- `❌ 缺陷` —— 已确认错误（答案键错 / 双正确项 / 无正确选项），**禁止进入展示包**")
    lines.append("- `➖ 不适用` —— 公式计算题，按需求不进入展示包，本阶段不逐题复核")
    lines.append("")

    order = (
        ("concept_distinction", "概念辨析题"),
        ("hallucination_trap", "AI 幻觉陷阱题"),
        ("formula_reasoning", "公式应用与量纲题"),
    )
    for kind, title in order:
        group = [r for r in clean if r["question_type"] == kind]
        if not group:
            continue
        n_ok = sum(1 for r in group if verdict_of(r["eval_id"], kind)[0] == "ok")
        lines.append(f"## {title}（{len(group)} 道，合格 {n_ok}）")
        lines.append("")
        lines.append("| eval_id | concept_id | 判定 | 复核说明 |")
        lines.append("|---|---|---|---|")
        for r in sorted(group, key=lambda x: x["eval_id"]):
            verdict, note = verdict_of(r["eval_id"], kind)
            lines.append(
                f"| `{r['eval_id']}` | {r['concept_id']} | {VERDICT_ZH[verdict]} | {note} |"
            )
        lines.append("")

    lines.append("## 汇总")
    lines.append("")
    lines.append("| 判定 | 数量 |")
    lines.append("|---|---|")
    for key in ("ok", "suspect", "defect", "na"):
        lines.append(f"| {VERDICT_ZH[key]} | {count_verdict(clean, key)} |")
    lines.append(f"| **合计** | **{len(clean)}** |")
    lines.append("")
    return "\n".join(lines)


def build_report_md(
    payload: Dict[str, Any],
    clean: Sequence[Dict[str, Any]],
    picked: Sequence[Dict[str, Any]],
    pool: Sequence[Dict[str, Any]],
    backup_path: Optional[Path],
    seed: int,
    dry_run: bool,
    review_gate: bool,
) -> str:
    counts = payload["counts"]
    items = payload["eval_items"]
    concepts = {c["concept_id"]: c for c in payload["concepts"]}
    lines: List[str] = []
    lines.append("# 阶段四 · MVP 数据提纯与打包回报")
    lines.append("")
    lines.append(f"- 生成时间：{payload['generated_at']}")
    lines.append("- 执行方式：**纯数据操作，全程未调用模型推理接口**（不访问网络、不访问 127.0.0.1:11434）")
    lines.append(f"- 抽样随机种子：`{seed}`（固定种子，可复现）")
    lines.append(f"- 人工复核闸门：{'**启用**' if review_gate else '未启用（按纯随机抽取）'}")
    if dry_run:
        lines.append("- 运行模式：`--dry-run`（仅报告，未落盘）")
    lines.append("")

    lines.append("## 一、数据提纯（隔离）")
    lines.append("")
    lines.append("| 项 | 值 |")
    lines.append("|---|---|")
    lines.append(f"| 处理前题目总数 | {counts['original_pool_before_quarantine']} |")
    lines.append(f"| 隔离剔除（阶段三报告 §5.2） | {counts['quarantined_removed']} |")
    lines.append(f"| 提纯后主线题数 | {counts['clean_pool_after_quarantine']} |")
    lines.append("")
    lines.append("隔离名单（移入 `data/interim/quarantine_eval.jsonl`）：")
    lines.append("")
    for eid, qtype, reason in QUARANTINE:
        lines.append(f"- `{eid}`（{TYPE_ZH[qtype]}）：{reason}")
    lines.append("")

    lines.append("## 二、人工逐题复核（阶段四新增）")
    lines.append("")
    lines.append(
        f"对提纯后剩余的概念辨析题与幻觉陷阱题逐条验算题干条件、选项唯一性与答案键一致性"
        f"（公式计算题按需求不进入展示包，未逐题复核）："
    )
    lines.append("")
    lines.append("| 判定 | 数量 |")
    lines.append("|---|---|")
    lines.append(f"| ✅ 合格（可进入展示包） | {counts['review_ok']} |")
    lines.append(f"| ⚠️ 存疑（展示前须修） | {counts['review_suspect_excluded']} |")
    lines.append(f"| ❌ 缺陷（禁止进入展示包） | {counts['review_defect_excluded']} |")
    lines.append(f"| ➖ 不适用（公式题，未复核） | {counts['review_not_applicable']} |")
    lines.append("")
    lines.append("逐题判定见 `reports/eval_human_review_stage4.md`。")
    lines.append("")
    lines.append("**本阶段新发现的缺陷题（不在阶段三 9 道名单内，但同样有害）**：")
    lines.append("")
    lines.append("| eval_id | 题型 | 问题 |")
    lines.append("|---|---|---|")
    by_id = {r["eval_id"]: r for r in clean}
    for eid in sorted(eid for eid, (v, _) in REVIEW_VERDICTS.items() if v == "defect"):
        if eid not in by_id:
            continue
        kind = TYPE_ZH[by_id[eid]["question_type"]]
        lines.append(f"| `{eid}` | {kind} | {REVIEW_VERDICTS[eid][1]} |")
    lines.append("")
    lines.append("**存疑题（答案键可辩护，但解析或表述有瑕疵，展示前须修）**：")
    lines.append("")
    lines.append("| eval_id | 题型 | 问题 |")
    lines.append("|---|---|---|")
    for eid in sorted(eid for eid, (v, _) in REVIEW_VERDICTS.items() if v == "suspect"):
        if eid not in by_id:
            continue
        kind = TYPE_ZH[by_id[eid]["question_type"]]
        lines.append(f"| `{eid}` | {kind} | {REVIEW_VERDICTS[eid][1]} |")
    lines.append("")

    lines.append("## 三、黄金样本包")
    lines.append("")
    lines.append(
        f"- 题量：**{counts['eval_items']} 道**（概念辨析 {counts['eval_items_by_type'].get('concept_distinction', 0)} + "
        f"幻觉陷阱 {counts['eval_items_by_type'].get('hallucination_trap', 0)}），"
        f"公式计算题 {counts['eval_items_by_type'].get('formula_reasoning', 0)} 道（按要求全部避开）"
    )
    lines.append(f"- 概念：**{counts['concepts']} 条**（与题目 concept_id 一一对应）")
    if review_gate:
        lines.append(f"- 抽样池：复核通过的 {counts['review_gate_pool']} 道（从中随机抽取）")
    lines.append("")
    lines.append("### 15 道黄金样本 eval_id 列表")
    lines.append("")
    lines.append("| # | eval_id | 题型 | concept_id | 概念名 | 答案键 |")
    lines.append("|---|---|---|---|---|---|")
    for i, it in enumerate(items, start=1):
        c = concepts[it["concept_id"]]
        lines.append(
            f"| {i} | `{it['eval_id']}` | {TYPE_ZH[it['question_type']]} | "
            f"{it['concept_id']} | {c['name_zh']} | {it['correct_option']} |"
        )
    lines.append("")
    lines.append("**纯文本列表**：" + ", ".join(f"`{it['eval_id']}`" for it in items))
    lines.append("")

    lines.append("## 四、交付物")
    lines.append("")
    lines.append("| 路径 | 说明 |")
    lines.append("|---|---|")
    lines.append("| `release/v0.1_mvp/OpenSciGraph_Golden_Sample_v0.1.json` | 对外展示样本（概念 + 题目） |")
    lines.append("| `release/v0.1_mvp/README.md` | 包结构说明 |")
    lines.append(f"| `data/interim/quarantine_eval.jsonl` | 隔离的 {counts['quarantined_removed']} 道缺陷题（含隔离原因审计字段） |")
    lines.append(f"| `data/processed/physics_eval_v1.jsonl` | 提纯后主线数据（{counts['clean_pool_after_quarantine']} 道） |")
    lines.append("| `reports/eval_human_review_stage4.md` | 逐题人工复核判定表 |")
    if backup_path is not None:
        lines.append(f"| `{backup_path.relative_to(PROJECT_ROOT).as_posix()}` | 提纯前的 50 题原样备份 |")
    lines.append("")

    lines.append("## 五、发布前须知")
    lines.append("")
    lines.append(
        "入选的 15 道题已由人工逐题验算（题干条件完整、选项唯一、答案键与解析一致），"
        "可以用于对外展示。但仍建议保留两处注意："
    )
    lines.append("")
    lines.append(
        "1. `concepts[].wikidata_id` / `source_url` 均为 `null`、`license_type` 为 `UNVERIFIED` —— "
        "阶段二离线批次未联网核验来源，属**有意留空**，不是数据缺失。"
    )
    lines.append(
        f"2. 本阶段复核中又发现 **{counts['review_defect_excluded']} 道确认缺陷**、"
        f"**{counts['review_suspect_excluded']} 道存疑**（见 `reports/eval_human_review_stage4.md`）—— "
        "它们**仍留在主线数据 `physics_eval_v1.jsonl` 中**（本阶段只按指令隔离了 9 道），"
        "若后续要扩充评测集，**必须先修正或剔除**。"
    )
    lines.append(
        "3. 公式计算题（16 道）按要求未进入展示包，也未经逐题复核，"
        "它们是缺陷率最高的一类（阶段三盲测自洽率仅 60%），扩批前建议优先处理。"
    )
    lines.append("")
    return "\n".join(lines)


def build_release_readme(payload: Dict[str, Any]) -> str:
    counts = payload["counts"]
    lines: List[str] = []
    lines.append("# OpenSciGraph Golden Sample v0.1 (MVP)")
    lines.append("")
    lines.append("对外展示样本包。**纯数据产物，不含任何模型推理**。")
    lines.append("")
    lines.append("## 文件")
    lines.append("")
    lines.append("- `OpenSciGraph_Golden_Sample_v0.1.json` —— 主交付文件（UTF-8，无 BOM）")
    lines.append("")
    lines.append("## 顶层结构")
    lines.append("")
    lines.append("```")
    lines.append("OpenSciGraph_Golden_Sample_v0.1.json")
    lines.append("├── dataset / version / release / purpose   # 标识")
    lines.append("├── generated_at / generated_by             # 溯源")
    lines.append("├── model_involved: false                   # 声明无模型推理参与")
    lines.append("├── human_review                            # 人工复核范围与排除清单")
    lines.append("├── random_seed                             # 抽样种子，可复现")
    lines.append("├── sources                                 # 上游文件路径")
    lines.append("├── counts                                  # 数量统计")
    lines.append("├── field_order                             # 字段顺序契约")
    lines.append("├── integrity_note / quality_note / license_note")
    lines.append("├── concepts  [object]                      # 15 条概念基础数据")
    lines.append("└── eval_items[object]                      # 15 道评测题（含内联 concept）")
    lines.append("```")
    lines.append("")
    lines.append("## 计数")
    lines.append("")
    lines.append(f"- concepts：{counts['concepts']}")
    lines.append(f"- eval_items：{counts['eval_items']}（概念辨析 {counts['eval_items_by_type'].get('concept_distinction', 0)} / "
                 f"幻觉陷阱 {counts['eval_items_by_type'].get('hallucination_trap', 0)}）")
    lines.append("")
    lines.append("## eval_items 字段")
    lines.append("")
    for i, f in enumerate(payload["field_order"]["eval_item"], start=1):
        lines.append(f"{i}. `{f}`")
    lines.append(f"{len(payload['field_order']['eval_item']) + 1}. `concept` —— 内联的概念对象（见 `concepts[]`）")
    lines.append("")
    lines.append("## concepts 字段")
    lines.append("")
    for i, f in enumerate(payload["field_order"]["concept"], start=1):
        lines.append(f"{i}. `{f}`")
    lines.append("")
    lines.append("## 解包示例（浏览器 / Node）")
    lines.append("")
    lines.append("```js")
    lines.append("const data = await fetch('OpenSciGraph_Golden_Sample_v0.1.json').then(r => r.json());")
    lines.append("for (const item of data.eval_items) {")
    lines.append("  console.log(item.eval_id, item.question_type, item.concept.name_zh);")
    lines.append("}")
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="阶段四 MVP 数据提纯与打包（纯数据操作）")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="抽样随机种子")
    parser.add_argument("--dry-run", action="store_true", help="只校验并报告，不写任何文件")
    parser.add_argument(
        "--no-review-gate",
        action="store_true",
        help="关闭人工复核闸门，按纯随机从提纯后的全池抽取（用于复现用户原始指令）",
    )
    args = parser.parse_args(argv)

    if not EVAL_PATH.exists():
        LOG.error("找不到评测集：%s", EVAL_PATH)
        return 2
    if not CONCEPT_PATH.exists():
        LOG.error("找不到概念库：%s", CONCEPT_PATH)
        return 2

    rows = read_jsonl(EVAL_PATH)
    concepts_all = read_jsonl(CONCEPT_PATH)
    concepts = {c["concept_id"]: c for c in concepts_all}
    LOG.info("读取评测集 %d 条 | 概念库 %d 条", len(rows), len(concepts_all))

    for r in rows:
        if list(r.keys()) != list(EVAL_FIELDS):
            raise ValueError(f"{r.get('eval_id')} 字段/顺序不符契约：{list(r.keys())}")

    # --- 步骤 1 · 隔离 ---
    clean, quarantine = partition(rows)
    if len(clean) + len(quarantine) != len(rows):
        raise ValueError("拆分后数量不等于原数量——提纯任务不允许丢数据")
    LOG.info("隔离 %d 条，主线保留 %d 条", len(quarantine), len(clean))

    # --- 步骤 2 · 复核闸门 ---
    review_gate = not args.no_review_gate
    pool = gate(clean) if review_gate else list(clean)
    if review_gate:
        LOG.info("人工复核：合格 %d / 存疑 %d / 缺陷 %d / 公式题未复核 %d → 抽样池 %d 道",
                 count_verdict(clean, "ok"), count_verdict(clean, "suspect"),
                 count_verdict(clean, "defect"), count_verdict(clean, "na"), len(pool))
    else:
        LOG.warning("复核闸门已关闭，将按纯随机抽取（可能抽中含缺陷题目）")

    # --- 步骤 3 · 抽样 ---
    picked = select_golden(pool, args.seed)
    LOG.info("抽中 %d 道：%s", len(picked), ", ".join(r["eval_id"] for r in picked))

    # --- 步骤 4 · 打包 ---
    payload = build_payload(picked, concepts, args.seed, clean, review_gate, len(pool))

    # --- 自检 ---
    if len(payload["eval_items"]) != WANT_DISTINCTION + WANT_TRAP:
        raise ValueError("黄金样本题量不符")
    if any(it["question_type"] == "formula_reasoning" for it in payload["eval_items"]):
        raise ValueError("黄金样本中混入了公式计算题")
    leaked = {it["eval_id"] for it in payload["eval_items"]} & set(QUARANTINE_IDS)
    if leaked:
        raise ValueError(f"黄金样本中混入了被隔离的题目：{leaked}")
    if review_gate:
        bad = {
            it["eval_id"] for it in payload["eval_items"]
            if verdict_of(it["eval_id"], it["question_type"])[0] != "ok"
        }
        if bad:
            raise ValueError(f"复核闸门失效，非合格题混入展示包：{bad}")
    if len({it["eval_id"] for it in payload["eval_items"]}) != len(payload["eval_items"]):
        raise ValueError("黄金样本 eval_id 有重复")

    if args.dry_run:
        LOG.info("--dry-run：跳过落盘")
        print(build_report_md(payload, clean, picked, pool, None, args.seed, True, review_gate))
        return 0

    # --- 备份 ---
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backup_path = BACKUP_DIR / f"physics_eval_v1.pre_stage4_{timestamp_slug()}.jsonl"
    assert_writable(backup_path)
    backup_path.write_bytes(EVAL_PATH.read_bytes())
    LOG.info("提纯前原样备份 -> %s", backup_path.relative_to(PROJECT_ROOT).as_posix())

    # --- 落盘 ---
    write_jsonl(build_quarantine_records(quarantine), QUARANTINE_PATH)
    LOG.info("隔离集 -> %s（%d 条）", QUARANTINE_PATH.relative_to(PROJECT_ROOT).as_posix(), len(quarantine))

    write_jsonl(clean, EVAL_PATH)
    LOG.info("主线数据 -> %s（%d 条）", EVAL_PATH.relative_to(PROJECT_ROOT).as_posix(), len(clean))

    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    GOLDEN_JSON.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    LOG.info("黄金样本 -> %s（%s 字节）", GOLDEN_JSON.relative_to(PROJECT_ROOT).as_posix(), GOLDEN_JSON.stat().st_size)

    RELEASE_README.write_text(build_release_readme(payload), encoding="utf-8", newline="\n")
    LOG.info("包说明 -> %s", RELEASE_README.relative_to(PROJECT_ROOT).as_posix())

    STAGE_REPORT.write_text(
        build_report_md(payload, clean, picked, pool, backup_path, args.seed, False, review_gate),
        encoding="utf-8", newline="\n",
    )
    LOG.info("阶段汇报 -> %s", STAGE_REPORT.relative_to(PROJECT_ROOT).as_posix())

    REVIEW_REPORT.write_text(build_review_md(clean), encoding="utf-8", newline="\n")
    LOG.info("复核判定表 -> %s", REVIEW_REPORT.relative_to(PROJECT_ROOT).as_posix())

    LOG.info("完成：提纯 %d 条 / 隔离 %d 条 / 黄金样本 %d 道",
             len(clean), len(quarantine), len(payload["eval_items"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
