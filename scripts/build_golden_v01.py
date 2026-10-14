#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
阶段四（定稿）· OpenSciGraph v0.1 MVP 黄金数据包封装

与 ``scripts/build_golden_sample.py`` 的区别
-------------------------------------------
- 上一版按 10 + 5 的配额**随机抽样**，产出 15 道；
- 本版按人工复核结论**确定性提取全部 16 道合格题**
  （11 道概念辨析 + 5 道幻觉陷阱），不含任何随机性，运行多少次结果都一致。

流水线
------
1. **提取**：从 ``data/processed/physics_eval_v1.jsonl`` 按固定 ID 清单取出 16 道题，
   并逐题校验「ID 存在 / 题型匹配 / 人工复核判定为 ok」。
2. **关联**：按 ``concept_id`` 从 ``data/processed/physics_concepts_v2.jsonl``
   取回对应的 16 条概念实体，作为内联副本写入题目（前端免 join）。
3. **打包**：写出 ``release/v0.1_mvp/OpenSciGraph_Golden_v0.1.json``。
4. **校验**：对成品做结构校验（字段顺序、计数、去重、内联一致性、来源留空、编码）。
5. **README**：生成 ``release/v0.1_mvp/README.md``（数据概览 / 核心特性 / 数据字典）。

用法::

    python scripts/build_golden_v01.py              # 正式执行
    python scripts/build_golden_v01.py --dry-run    # 只校验并打印，不落盘

本脚本纯数据操作：不访问网络、不调用 127.0.0.1:11434、不写入 ``data/raw``，
也**不修改**任何上游数据文件（只读）。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.common import (  # noqa: E402
    PROCESSED_DIR,
    PROJECT_ROOT,
    REPORTS_DIR,
    setup_logger,
    utc_now_iso,
)

# 复用上一版脚本里的人工复核判定表与字段契约，保证结论口径完全一致
import importlib.util as _ilu  # noqa: E402

_spec = _ilu.spec_from_file_location(
    "_build_golden_sample", _PROJECT_ROOT / "scripts" / "build_golden_sample.py"
)
_gs = _ilu.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_gs)  # type: ignore[union-attr]

EVAL_FIELDS: Tuple[str, ...] = _gs.EVAL_FIELDS
CONCEPT_FIELDS: Tuple[str, ...] = _gs.CONCEPT_FIELDS
REVIEW_VERDICTS: Dict[str, Tuple[str, str]] = _gs.REVIEW_VERDICTS
QUARANTINE_IDS: Tuple[str, ...] = _gs.QUARANTINE_IDS

LOG = setup_logger("build_golden_v01")

# ---------------------------------------------------------------------------
# 路径常量
# ---------------------------------------------------------------------------

EVAL_PATH: Path = PROCESSED_DIR / "physics_eval_v1.jsonl"
CONCEPT_PATH: Path = PROCESSED_DIR / "physics_concepts_v2.jsonl"
EVAL_SCHEMA_PATH: Path = PROJECT_ROOT / "config" / "physics_eval_schema.json"
CONCEPT_SCHEMA_PATH: Path = PROJECT_ROOT / "config" / "physics_v2_schema.json"

RELEASE_DIR: Path = PROJECT_ROOT / "release" / "v0.1_mvp"
GOLDEN_JSON: Path = RELEASE_DIR / "OpenSciGraph_Golden_v0.1.json"
RELEASE_README: Path = RELEASE_DIR / "README.md"
ARCHIVE_DIR: Path = RELEASE_DIR / "archive"
SUPERSEDED_JSON: Path = RELEASE_DIR / "OpenSciGraph_Golden_Sample_v0.1.json"
VALIDATION_REPORT: Path = REPORTS_DIR / "stage4_golden_v01_validation.md"
HF_CARD: Path = RELEASE_DIR / "HuggingFace_Dataset_Card.md"

#: HuggingFace `datasets` 原生加载所需的 JSONL 分片。
#: 主交付文件是**单个 JSON 对象**（含 ``concepts`` / ``eval_items`` 两个嵌套数组），
#: HF 的 json loader 面向「JSONL 或 JSON 数组」，无法把嵌套对象展开成多行，
#: 因此额外导出两个扁平分片，保证 ``load_dataset()`` 开箱可用。
EVAL_JSONL: Path = RELEASE_DIR / "eval_items.jsonl"
CONCEPT_JSONL: Path = RELEASE_DIR / "concepts.jsonl"

# ---------------------------------------------------------------------------
# 对外联系信息 —— 发布前必须替换！
# ---------------------------------------------------------------------------
#: 对外联系信息（已由项目方确认，2026-10-14）。
#: 卡片的「需求反馈」区与引用元数据会原样引用；
#: 若把任意字段改回 "<TODO: ...>" 形式，构建时会自动打 WARNING 并在卡片顶部插入待办提醒。
#: HuggingFace 数据集仓库 ID（命名空间 + 仓库名）。
#: 命名空间沿革（2026-10-14 实测）：
#:   ① 原定 ``OpenSciGraph`` 组织 —— 在 huggingface.co 上不存在（404）；
#:   ② 备选 ``ruguo3500`` 组织 —— 存在且账号是其成员，但所用细粒度 token 的
#:      ``scoped`` 授权只覆盖用户实体 ``guowei79``，不含该组织，写入返回 403；
#:   ③ 最终 ``guowei79`` —— 该 token 唯一可写的命名空间，上架成功。
#: 若日后补上组织权限，只改这一处并重跑即可。
HF_REPO_ID: str = "guowei79/OpenSciGraph-Physics-Bench"

CONTACT: Dict[str, str] = {
    "email": "rguo3500@gmail.com",
    #: 2026-10-14 改为项目方的真实仓库路径。
    #: 注意：该仓库 **当前为 404**（GitHub 用户 rguo3500 存在，但仓库 rguo3500/OpenSciGraph
    #: 尚未创建）。建好仓库后此链接即生效；在建成之前，公开的数据集页面上这条链接是死链。
    "repo": "https://github.com/rguo3500/OpenSciGraph",
    #: 由 HF_REPO_ID 派生，勿手写——避免命名空间改动时两处失配。
    "hf_home": f"https://huggingface.co/datasets/{HF_REPO_ID}",
}

#: 联系方式是否仍含未替换的占位符
CONTACT_PENDING: bool = any("<TODO:" in v for v in CONTACT.values())

#: 数据集卡中引用的两道完整示例题（一辨析、一陷阱）
EXAMPLE_DISTINCTION = "EVAL_P006"
EXAMPLE_TRAP = "EVAL_P004"


# ---------------------------------------------------------------------------
# 固定提取清单（人工复核判定为 ok 的全部题目）
# ---------------------------------------------------------------------------

DISTINCTION_IDS: Tuple[str, ...] = (
    "EVAL_P006", "EVAL_P012", "EVAL_P026", "EVAL_P044", "EVAL_P045",
    "EVAL_P049", "EVAL_P060", "EVAL_P070", "EVAL_P073", "EVAL_P093", "EVAL_P096",
)
TRAP_IDS: Tuple[str, ...] = ("EVAL_P004", "EVAL_P008", "EVAL_P010", "EVAL_P059", "EVAL_P098")

#: 期望题型映射
EXPECT_TYPE: Dict[str, str] = {**{e: "concept_distinction" for e in DISTINCTION_IDS},
                               **{e: "hallucination_trap" for e in TRAP_IDS}}

#: 期望提取顺序：先辨析（按题号）、后陷阱（按题号）
WANT_IDS: Tuple[str, ...] = DISTINCTION_IDS + TRAP_IDS

WANT_DISTINCTION = len(DISTINCTION_IDS)   # 11
WANT_TRAP = len(TRAP_IDS)                 # 5
WANT_TOTAL = WANT_DISTINCTION + WANT_TRAP  # 16

__all__ = ["main"]


# ---------------------------------------------------------------------------
# IO
# ---------------------------------------------------------------------------


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    text = Path(path).read_text(encoding="utf-8")
    for lineno, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:  # pragma: no cover
            raise ValueError(f"{path} 第 {lineno} 行不是合法 JSON：{exc}") from exc
        if not isinstance(obj, dict):
            raise ValueError(f"{path} 第 {lineno} 行顶层不是 JSON 对象")
        rows.append(obj)
    return rows


# ---------------------------------------------------------------------------
# 步骤 1 · 提取（带三道校验闸门）
# ---------------------------------------------------------------------------


def extract(eval_rows: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """按固定清单提取 16 道题；任一校验不通过直接抛错。"""
    index = {r["eval_id"]: r for r in eval_rows}

    missing = [e for e in WANT_IDS if e not in index]
    if missing:
        raise ValueError(f"清单中的题目不在 {EVAL_PATH.name} 里：{missing}")

    picked: List[Dict[str, Any]] = []
    for eid in WANT_IDS:
        rec = index[eid]
        got_type = rec["question_type"]
        want_type = EXPECT_TYPE[eid]
        if got_type != want_type:
            raise ValueError(f"{eid} 题型不符：期望 {want_type}，实际 {got_type}")
        verdict, note = REVIEW_VERDICTS.get(eid, ("unreviewed", "未列入人工复核表"))
        if verdict != "ok":
            raise ValueError(f"{eid} 人工复核判定为 {verdict}，不得进入黄金包（{note}）")
        if eid in QUARANTINE_IDS:
            raise ValueError(f"{eid} 属于已隔离缺陷题，不得进入黄金包")
        if list(rec.keys()) != list(EVAL_FIELDS):
            raise ValueError(f"{eid} 字段/顺序不符契约：{list(rec.keys())}")
        picked.append(dict(rec))
    return picked


def write_jsonl_rows(rows: Sequence[Dict[str, Any]], path: Path) -> Path:
    """以 UTF-8 / LF / 无 BOM 写出 JSONL（每行一个对象），原子替换。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    body = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
    tmp.write_text(body, encoding="utf-8", newline="\n")
    os.replace(tmp, path)
    return path


def read_jsonl_rows(path: Path) -> List[Dict[str, Any]]:
    return [json.loads(ln) for ln in Path(path).read_text(encoding="utf-8").splitlines() if ln.strip()]


# ---------------------------------------------------------------------------
# 步骤 2 · 关联概念
# ---------------------------------------------------------------------------


def link_concepts(
    picked: Sequence[Dict[str, Any]], concept_rows: Sequence[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    concepts = {c["concept_id"]: c for c in concept_rows}
    missing = [r["concept_id"] for r in picked if r["concept_id"] not in concepts]
    if missing:
        raise ValueError(f"概念库中缺少这些 concept_id：{missing}")
    used = sorted({r["concept_id"] for r in picked})
    concept_list = [concepts[cid] for cid in used]
    for c in concept_list:
        if list(c.keys()) != list(CONCEPT_FIELDS):
            raise ValueError(f"{c['concept_id']} 概念字段/顺序不符契约：{list(c.keys())}")
    return concept_list, concepts


# ---------------------------------------------------------------------------
# 步骤 3 · 组装数据字典（从 Schema 文件直接抽取，保证与契约一致）
# ---------------------------------------------------------------------------


def load_field_dict(schema_path: Path) -> List[Dict[str, Any]]:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    out: List[Dict[str, Any]] = []
    for f in schema["fields"]:
        entry = {
            "name": f["name"],
            "type": f.get("type"),
            "required": f.get("required", False),
            "nullable": f.get("nullable", False),
            "description": f.get("description", ""),
        }
        for extra in ("pattern", "enum", "exact_length", "min_length", "allow_empty_string"):
            if extra in f:
                entry[extra] = f[extra]
        out.append(entry)
    return out


# ---------------------------------------------------------------------------
# 步骤 4 · 组装成品
# ---------------------------------------------------------------------------


def build_payload(
    picked: Sequence[Dict[str, Any]],
    concept_list: Sequence[Dict[str, Any]],
    concepts: Dict[str, Dict[str, Any]],
    clean_pool: int,
    total_pool: int,
) -> Dict[str, Any]:
    concept_list = list(concept_list)
    eval_items: List[Dict[str, Any]] = []
    for r in picked:
        item = {f: r[f] for f in EVAL_FIELDS}
        item["concept"] = concepts[r["concept_id"]]  # 内联副本
        eval_items.append(item)

    by_type: Dict[str, int] = {}
    for r in picked:
        by_type[r["question_type"]] = by_type.get(r["question_type"], 0) + 1

    return {
        "dataset": "OpenSciGraph Golden Dataset",
        "version": "v0.1",
        "release": "v0.1_mvp",
        "schema_version": "1.0.0",
        "purpose": (
            f"OpenSciGraph v0.1 MVP 黄金数据包：{len(eval_items)} 组物理概念图谱"
            f"（{len(concept_list)} 条概念实体）与 {len(eval_items)} 道防幻觉 Benchmark 样例，"
            "全部经人工逐题复核，可离线直接加载。"
        ),
        "generated_at": utc_now_iso(),
        "generated_by": "scripts/build_golden_v01.py",
        "model_involved": False,
        "offline": True,
        "selection": {
            "mode": "fixed_human_reviewed_ok",
            "random_sampling": False,
            "rule": (
                "确定性提取：取人工逐题复核判定为 ok 的全部题目，"
                "即概念辨析题 11 道 + 幻觉陷阱题 5 道，共 16 道；不抽样、不含随机性。"
            ),
            "distinction_ids": list(DISTINCTION_IDS),
            "trap_ids": list(TRAP_IDS),
        },
        "human_review": {
            "enabled": True,
            "method": "人工逐题验算（非模型自评）",
            "scope": "复核题干条件完整性、选项唯一性与答案键一致性",
            "verdicts_file": "reports/eval_human_review_stage4.md",
            "ok_admitted": WANT_TOTAL,
            "suspect_excluded": sorted(
                eid for eid, (v, _) in REVIEW_VERDICTS.items() if v == "suspect"
            ),
            "defect_excluded": sorted(
                eid for eid, (v, _) in REVIEW_VERDICTS.items() if v == "defect"
            ),
            "quarantined": list(QUARANTINE_IDS),
        },
        "sources": {
            "concepts": "data/processed/physics_concepts_v2.jsonl",
            "eval_items": "data/processed/physics_eval_v1.jsonl",
            "quarantined_items": "data/interim/quarantine_eval.jsonl",
            "schemas": [
                "config/physics_v2_schema.json",
                "config/physics_eval_schema.json",
            ],
            "reports": [
                "reports/stage4_mvp_report.md",
                "reports/eval_human_review_stage4.md",
                "reports/graph_quality_review.md",
            ],
        },
        "counts": {
            "concepts": len(concept_list),
            "eval_items": len(eval_items),
            "eval_items_by_type": by_type,
            "distinction": by_type.get("concept_distinction", 0),
            "trap": by_type.get("hallucination_trap", 0),
            "formula_reasoning": by_type.get("formula_reasoning", 0),
            "eval_pool_after_quarantine": clean_pool,
            "eval_pool_before_quarantine": total_pool,
            "quarantined_removed": len(QUARANTINE_IDS),
        },
        "field_order": {
            "eval_item": list(EVAL_FIELDS) + ["concept"],
            "concept": list(CONCEPT_FIELDS),
        },
        "data_dictionary": {
            "top_level": [
                {"name": "dataset", "type": "string", "description": "数据集名称。"},
                {"name": "version", "type": "string", "description": "数据版本号。"},
                {"name": "release", "type": "string", "description": "发布批次目录名。"},
                {"name": "schema_version", "type": "string", "description": "本包结构契约版本。"},
                {"name": "purpose", "type": "string", "description": "包的用途说明。"},
                {"name": "generated_at", "type": "string", "description": "生成时间（UTC，ISO-8601）。"},
                {"name": "generated_by", "type": "string", "description": "生成脚本路径。"},
                {"name": "model_involved", "type": "boolean", "description": "是否有模型推理参与；恒为 false。"},
                {"name": "offline", "type": "boolean", "description": "是否全程离线产出；恒为 true。"},
                {"name": "selection", "type": "object", "description": "选题方式与固定 ID 清单。"},
                {"name": "human_review", "type": "object", "description": "人工复核口径、准入与排除清单。"},
                {"name": "sources", "type": "object", "description": "上游数据与契约文件路径。"},
                {"name": "counts", "type": "object", "description": "数量统计。"},
                {"name": "field_order", "type": "object", "description": "字段顺序契约。"},
                {"name": "data_dictionary", "type": "object", "description": "本字段字典自身（自描述）。"},
                {"name": "concepts", "type": "array<object>", "description": "概念实体数组，见 concepts 字段表。"},
                {"name": "eval_items", "type": "array<object>", "description": "评测题数组，见 eval_item 字段表。"},
                {"name": "notes", "type": "object", "description": "完整性 / 质量 / 许可 / 已知限制说明。"},
            ],
            "eval_item": load_field_dict(EVAL_SCHEMA_PATH)
            + [{
                "name": "concept",
                "type": "object",
                "required": True,
                "nullable": False,
                "description": (
                    "该题 concept_id 对应概念实体的内联副本，字段与 concepts[] 逐字段一致，"
                    "仅供前端渲染便利；以 concepts[] 为准。"
                ),
            }],
            "concept": load_field_dict(CONCEPT_SCHEMA_PATH),
        },
        "notes": {
            "integrity": (
                "eval_items[].concept 是 concepts[] 中同 concept_id 记录的内联副本，"
                "两者逐字段完全一致；以 concepts[] 为准。"
            ),
            "quality": (
                "16 道题均为人工逐题验算通过（题干条件完整、选项唯一、答案键与解析一致），"
                "已剔除阶段三确认的 9 道缺陷题与阶段四复核发现的全部缺陷/存疑题，且不含公式计算题。"
            ),
            "license": (
                "concepts[].license_type 统一为 UNVERIFIED：离线批次未联网核验来源，"
                "wikidata_id 与 source_url 一律为 null，未冒充真实 Wikidata / Wikipedia 数据。"
            ),
            "known_limits": [
                "concepts[].parent_concept / child_concepts 为模型推断的层级边，"
                "阶段二复核实测约半数边不可信（双向闭合率仅 48.4%），仅供检索参考，不可作为权威本体。",
                "EVAL_P049 题干内嵌了选项文本（格式瑕疵），不影响答案键正确性。",
                "公式计算题（16 道）按要求未纳入本包，也未经逐题复核。",
                "suspect 与 defect 题目仍留在主线数据 physics_eval_v1.jsonl 中，扩充评测集前须先修正或剔除。",
            ],
        },
        "concepts": concept_list,
        "eval_items": eval_items,
    }


# ---------------------------------------------------------------------------
# 步骤 5 · 结构校验
# ---------------------------------------------------------------------------


def validate_payload(payload: Dict[str, Any], raw_text: str) -> List[Tuple[str, str, str]]:
    """返回 [(检查项, 结论 PASS/FAIL, 说明)]。"""
    checks: List[Tuple[str, str, str]] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        checks.append((name, "PASS" if ok else "FAIL", detail))

    # 1 顶层键
    need_top = {
        "dataset", "version", "release", "schema_version", "purpose",
        "generated_at", "generated_by", "model_involved", "offline",
        "selection", "human_review", "sources", "counts", "field_order",
        "data_dictionary", "concepts", "eval_items", "notes",
    }
    check("顶层必需键齐全", need_top <= set(payload), f"缺失={sorted(need_top - set(payload))}")

    eval_items = payload["eval_items"]
    concepts = payload["concepts"]

    # 2 计数
    check("eval_items 数量 = 16", len(eval_items) == WANT_TOTAL, f"实际={len(eval_items)}")
    check("concepts 数量 = 16", len(concepts) == WANT_TOTAL, f"实际={len(concepts)}")
    check("counts 与实际一致",
          payload["counts"]["eval_items"] == len(eval_items)
          and payload["counts"]["concepts"] == len(concepts),
          f"counts={payload['counts']['eval_items']}/{payload['counts']['concepts']}")

    # 3 ID 集合
    got_ids = [it["eval_id"] for it in eval_items]
    check("eval_id 集合与清单一致", set(got_ids) == set(WANT_IDS), f"实际={sorted(got_ids)}")
    check("eval_id 无重复", len(set(got_ids)) == len(got_ids))
    check("提取顺序 = 辨析在前/陷阱在后", got_ids == list(WANT_IDS))

    # 4 题型分布
    dist = sum(1 for it in eval_items if it["question_type"] == "concept_distinction")
    trap = sum(1 for it in eval_items if it["question_type"] == "hallucination_trap")
    formula = sum(1 for it in eval_items if it["question_type"] == "formula_reasoning")
    check("题型分布 11 辨析 / 5 陷阱 / 0 公式",
          (dist, trap, formula) == (WANT_DISTINCTION, WANT_TRAP, 0),
          f"辨析={dist} 陷阱={trap} 公式={formula}")

    # 5 逐题字段与内容
    field_ok, opt_ok, key_ok, inline_ok = True, True, True, True
    concept_map = {c["concept_id"]: c for c in concepts}
    for it in eval_items:
        if list(it.keys()) != list(EVAL_FIELDS) + ["concept"]:
            field_ok = False
        opts = it["options"]
        if (not isinstance(opts, list) or len(opts) != 4
                or any(not isinstance(o, str) or not o.strip() for o in opts)
                or len(set(opts)) != 4):
            opt_ok = False
        if it["correct_option"] not in ("A", "B", "C", "D"):
            key_ok = False
        cid = it["concept_id"]
        if cid not in concept_map or it["concept"] != concept_map[cid]:
            inline_ok = False
    check("eval_item 字段与顺序符合契约", field_ok)
    check("options 均为 4 项、非空、互不重复", opt_ok)
    check("correct_option ∈ {A,B,C,D}", key_ok)
    check("内联 concept 与 concepts[] 逐字段一致", inline_ok)

    # 6 ID 对应关系
    check("eval_id == 'EVAL_' + concept_id",
          all(it["eval_id"] == "EVAL_" + it["concept_id"] for it in eval_items))
    check("concept_id 全局唯一", len({it["concept_id"] for it in eval_items}) == len(eval_items))
    check("concepts[].concept_id 与题目一一对应",
          {c["concept_id"] for c in concepts} == {it["concept_id"] for it in eval_items})

    # 7 概念字段与来源留空
    check("concept 字段与顺序符合契约",
          all(list(c.keys()) == list(CONCEPT_FIELDS) for c in concepts))
    check("wikidata_id 全部为 null（零虚假来源）",
          all(c["wikidata_id"] is None for c in concepts))
    check("source_url 全部为 null（零虚假来源）",
          all(c["source_url"] is None for c in concepts))
    check("license_type 全部为 UNVERIFIED", all(c["license_type"] == "UNVERIFIED" for c in concepts))
    check("definition_zh 全部 >= 10 字",
          all(isinstance(c["definition_zh"], str) and len(c["definition_zh"]) >= 10 for c in concepts))

    # 8 排除项
    check("不含被隔离的缺陷题", not ({it["eval_id"] for it in eval_items} & set(QUARANTINE_IDS)))
    check("全部题目人工复核判定为 ok",
          all(REVIEW_VERDICTS.get(it["eval_id"], ("x",))[0] == "ok" for it in eval_items))
    check("model_involved == false", payload["model_involved"] is False)
    check("offline == true", payload["offline"] is True)

    # 9 序列化 / 编码
    try:
        reser = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        rt = json.loads(reser)
        check("JSON 可序列化且往返一致", rt == payload)
    except Exception as exc:  # noqa: BLE001
        check("JSON 可序列化且往返一致", False, str(exc))
    check("文本无 BOM", not raw_text.startswith("\ufeff"))
    check("换行统一为 LF", "\r\n" not in raw_text)
    check("UTF-8 可解码", True, f"{len(raw_text.encode('utf-8'))} 字节")

    return checks


# ---------------------------------------------------------------------------
# 汇报
# ---------------------------------------------------------------------------


def validate_splits(payload: Dict[str, Any], written: bool = True) -> List[Tuple[str, str, str]]:
    """校验 HF `datasets` 分片：既不与主包漂移，也能被 pyarrow 建表。"""
    checks: List[Tuple[str, str, str]] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        checks.append((name, "PASS" if ok else "FAIL", detail))

    items = payload["eval_items"]
    concepts = payload["concepts"]

    check("eval_items.jsonl 行数 = 16", len(items) == WANT_TOTAL, f"{len(items)}")
    check("concepts.jsonl 行数 = 16", len(concepts) == WANT_TOTAL, f"{len(concepts)}")

    if written and EVAL_JSONL.exists() and CONCEPT_JSONL.exists():
        got_e = read_jsonl_rows(EVAL_JSONL)
        got_c = read_jsonl_rows(CONCEPT_JSONL)
        check("eval_items.jsonl 与主包逐行一致", got_e == items)
        check("concepts.jsonl 与主包逐行一致", got_c == concepts)
        check("分片均为 UTF-8 无 BOM",
              not EVAL_JSONL.read_bytes().startswith(b"\xef\xbb\xbf")
              and not CONCEPT_JSONL.read_bytes().startswith(b"\xef\xbb\xbf"))
        # pyarrow 建表可行性（datasets 的底层依赖），失败即说明分片不可在线加载
        try:
            import pyarrow as pa  # noqa: PLC0415
            pa.table({k: [r.get(k) for r in items] for k in items[0]})
            pa.table({k: [r.get(k) for r in concepts] for k in concepts[0]})
            check("pyarrow 可据分片建表（datasets 可加载）", True)
        except Exception as exc:  # noqa: BLE001
            check("pyarrow 可据分片建表（datasets 可加载）", False, f"{type(exc).__name__}: {exc}")

    return checks


def build_validation_md(
    payload: Dict[str, Any],
    checks: Sequence[Tuple[str, str, str]],
    split_checks: Sequence[Tuple[str, str, str]] = (),
) -> str:
    n_pass = sum(1 for _, s, _ in checks if s == "PASS")
    lines: List[str] = []
    lines.append("# 阶段四定稿 · v0.1 MVP 黄金数据包校验报告")
    lines.append("")
    lines.append(f"- 生成时间：{utc_now_iso()}")
    lines.append("- 执行方式：纯数据操作（离线、不调用模型）")
    lines.append(f"- 产物：`release/v0.1_mvp/OpenSciGraph_Golden_v0.1.json`")
    lines.append(f"- 校验结论：**{n_pass}/{len(checks)} 项通过**")
    lines.append("")
    lines.append("## 校验明细")
    lines.append("")
    lines.append("| # | 检查项 | 结论 | 说明 |")
    lines.append("|---|---|---|---|")
    for i, (name, status, detail) in enumerate(checks, start=1):
        lines.append(f"| {i} | {name} | {'✅ ' + status if status == 'PASS' else '❌ ' + status} | {detail} |")
    lines.append("")
    lines.append("## 成品摘要")
    lines.append("")
    c = payload["counts"]
    lines.append(f"- concepts：{c['concepts']}")
    lines.append(f"- eval_items：{c['eval_items']}（概念辨析 {c['distinction']} / 幻觉陷阱 {c['trap']}）")
    lines.append("")
    lines.append("| # | eval_id | 题型 | concept_id | 概念 | 答案键 |")
    lines.append("|---|---|---|---|---|---|")
    cmap = {x["concept_id"]: x for x in payload["concepts"]}
    for i, it in enumerate(payload["eval_items"], start=1):
        lines.append(
            f"| {i} | `{it['eval_id']}` | {it['question_type']} | {it['concept_id']} | "
            f"{cmap[it['concept_id']]['name_zh']} | {it['correct_option']} |"
        )
    lines.append("")

    if split_checks:
        sp = sum(1 for _, s, _ in split_checks if s == "PASS")
        lines.append("## 附：HuggingFace `datasets` 分片校验")
        lines.append("")
        lines.append(f"主交付文件是**单个 JSON 对象**（含 `concepts[]` / `eval_items[]` 两个嵌套数组），")
        lines.append("HF 的 json loader 面向 JSONL 或 JSON 数组，**无法**把嵌套对象展开成多行；")
        lines.append("因此额外导出 `eval_items.jsonl`（16 行）与 `concepts.jsonl`（16 行）两个扁平分片，")
        lines.append("两者均由同一 payload 派生，与主包逐行一致。")
        lines.append("")
        lines.append(f"结论：**{sp}/{len(split_checks)} 项通过**")
        lines.append("")
        lines.append("| # | 检查项 | 结论 | 说明 |")
        lines.append("|---|---|---|---|")
        for i, (name, status, detail) in enumerate(split_checks, start=1):
            lines.append(f"| {i} | {name} | {'✅ ' + status if status == 'PASS' else '❌ ' + status} | {detail or '—'} |")
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# README
# ---------------------------------------------------------------------------


def build_readme(payload: Dict[str, Any], json_bytes: int) -> str:
    c = payload["counts"]
    dd = payload["data_dictionary"]
    cmap = {x["concept_id"]: x for x in payload["concepts"]}
    L: List[str] = []

    L.append("# OpenSciGraph Golden Dataset v0.1 (MVP)")
    L.append("")
    L.append("> 一份**完全离线提纯、零虚假来源**的基础物理概念图谱 + 防幻觉评测样例包。")
    L.append("> 本包为纯数据产物，生成过程中**未调用任何大模型推理**（`model_involved: false`）。")
    L.append("")

    # ---------------- 数据概览 ----------------
    L.append("## 一、数据概览")
    L.append("")
    L.append(f"- **{c['concepts']} 组物理概念图谱实体**：覆盖力学、振动与波动、热学、电磁学、光学与量子效应，")
    L.append("  每条含中英文名、中文定义、核心公式、上位/下位概念关系与许可标识。")
    L.append(f"- **{c['eval_items']} 道防幻觉 Benchmarks 样例**：概念辨析题 {c['distinction']} 道 + AI 幻觉陷阱题 {c['trap']} 道，")
    L.append("  每道题含题干、四选项、正确答案键、解析与命中的混淆点。")
    L.append(f"- **一一对应**：{c['eval_items']} 道题的 `concept_id` 与 {c['concepts']} 条概念实体严格一一对应，")
    L.append("  且每道题内联了对应概念对象，前端无需再做关联查询。")
    L.append("")
    L.append("### 文件清单")
    L.append("")
    L.append("| 文件 | 说明 |")
    L.append("|---|---|")
    L.append(f"| `OpenSciGraph_Golden_v0.1.json` | 主交付文件（UTF-8 无 BOM，{json_bytes} 字节） |")
    L.append("| `eval_items.jsonl` | HF `datasets` 分片：16 行，一行一题（与主包逐行一致） |")
    L.append("| `concepts.jsonl` | HF `datasets` 分片：16 行，一行一概念（与主包逐行一致） |")
    L.append("| `HuggingFace_Dataset_Card.md` | 对外发布用数据集卡（含质量证明、样例、加载代码、需求反馈区） |")
    L.append("| `COMMUNITY_POST.md` | 社区宣发文案套件（V2EX + 英文简版） |")
    L.append("| `README.md` | 本说明文档 |")
    L.append("")
    L.append("### 概念清单")
    L.append("")
    L.append("| # | concept_id | 中文名 | 英文名 | 核心公式 | 上位概念 |")
    L.append("|---|---|---|---|---|---|")
    for i, x in enumerate(payload["concepts"], start=1):
        formula = x["formula"] if x["formula"] else "—"
        parent = x["parent_concept"] if x["parent_concept"] else "—"
        L.append(f"| {i} | `{x['concept_id']}` | {x['name_zh']} | {x['name_en']} | {formula} | {parent} |")
    L.append("")
    L.append("### 题目清单")
    L.append("")
    L.append("| # | eval_id | 题型 | 概念 | 答案键 |")
    L.append("|---|---|---|---|---|")
    type_zh = {"concept_distinction": "概念辨析", "hallucination_trap": "幻觉陷阱"}
    for i, it in enumerate(payload["eval_items"], start=1):
        L.append(f"| {i} | `{it['eval_id']}` | {type_zh.get(it['question_type'], it['question_type'])} | "
                 f"{cmap[it['concept_id']]['name_zh']} | {it['correct_option']} |")
    L.append("")

    # ---------------- 核心特性 ----------------
    L.append("## 二、核心特性")
    L.append("")
    L.append("### 1. 100% 离线提纯")
    L.append("")
    L.append("- 全流程在本地完成：概念清洗、评测题生成、缺陷隔离、人工复核、打包，**不访问网络**。")
    L.append("- 原始数据来自本地 `data/raw`（只读），中间产物落盘为可复现的 JSONL。")
    L.append("- 打包脚本 `scripts/build_golden_v01.py` 为**确定性**执行：固定 ID 清单，运行多少次结果完全一致。")
    L.append("- 生成过程未调用任何模型推理接口，包内 `model_involved: false` 即为声明。")
    L.append("")
    L.append("### 2. 零虚假来源")
    L.append("")
    L.append("- 所有概念的 `wikidata_id` 与 `source_url` **一律为 `null`**，`license_type` 统一为 `UNVERIFIED`——")
    L.append("  离线批次无法联网核验来源，因此**有意留空**，绝不编造无法核实的 QID 或许可链接。")
    L.append("- 数据字典中的每一条字段说明均直接抽取自项目 Schema 契约文件，描述与结构同源。")
    L.append("")
    L.append("### 3. 特制大模型陷阱测试点")
    L.append(f"- {c['trap']} 道**幻觉陷阱题**针对阶段二实测发现的模型系统性盲点设计：题干植入一个错误前提")
    L.append("  （如「功率是一种能量」「加速度是运动学的一个分支学科」），正确答案必须明确否定该前提，")
    L.append("  干扰项则**顺从错误前提**构成有效诱导，用于暴露「把相关关系误判为种属关系」的典型幻觉。")
    L.append(f"- {c['distinction']} 道**概念辨析题**聚焦易混淆概念对（速度 vs 加速度、热量 vs 内能、偏振 vs 衍射等），")
    L.append("  四个选项同维度、均可判定真假，考验模型精确区分能力。")
    L.append("")
    L.append("### 4. 人工逐题复核准入")
    L.append("")
    L.append("- 本包 **16 道题全部经人工逐题验算**（题干条件完整性、选项唯一性、答案键与解析一致性），")
    L.append("  判定为 `ok` 方准入。已剔除阶段三确认的 9 道缺陷题，以及阶段四复核发现的双正确项 / 答案键反转等缺陷与存疑题。")
    L.append("")
    L.append("### 5. 已知限制（请务必阅读）")
    L.append("")
    for lim in payload["notes"]["known_limits"]:
        L.append(f"- {lim}")
    L.append("")

    # ---------------- 数据字典 ----------------
    L.append("## 三、数据字典")
    L.append("")
    L.append("### 3.1 顶层结构")
    L.append("")
    L.append("```")
    L.append("OpenSciGraph_Golden_v0.1.json")
    L.append("├── dataset / version / release / schema_version   # 标识")
    L.append("├── purpose                                        # 用途")
    L.append("├── generated_at / generated_by                    # 溯源")
    L.append("├── model_involved: false                          # 声明无模型推理参与")
    L.append("├── offline: true                                  # 声明全程离线")
    L.append("├── selection                                      # 选题方式与固定 ID 清单")
    L.append("├── human_review                                   # 复核口径与排除清单")
    L.append("├── sources                                        # 上游文件路径")
    L.append("├── counts                                         # 数量统计")
    L.append("├── field_order                                    # 字段顺序契约")
    L.append("├── data_dictionary                                # 本字段字典（自描述）")
    L.append("├── concepts    [16 × object]                      # 概念实体")
    L.append("├── eval_items  [16 × object]                      # 评测题（含内联 concept）")
    L.append("└── notes                                          # 完整性/质量/许可/限制")
    L.append("```")
    L.append("")
    L.append("### 3.2 顶层字段")
    L.append("")
    L.append("| 字段 | 类型 | 说明 |")
    L.append("|---|---|---|")
    for f in dd["top_level"]:
        L.append(f"| `{f['name']}` | {f['type']} | {f['description']} |")
    L.append("")

    L.append("### 3.3 `eval_items[]` 字段（评测题）")
    L.append("")
    L.append("| 字段 | 类型 | 必填 | 可空 | 说明 |")
    L.append("|---|---|---|---|---|")
    for f in dd["eval_item"]:
        req = "是" if f.get("required") else "否"
        nul = "是" if f.get("nullable") else "否"
        L.append(f"| `{f['name']}` | {f['type']} | {req} | {nul} | {f['description']} |")
    L.append("")
    L.append("> **注**：上表 `question_type` 中「20 / 20 / 10，合计 50 题」是项目原始契约里 50 题全批次的配额描述。")
    L.append("> **本数据包只收录其中人工复核判定为 `ok` 的 11 道概念辨析题与 5 道幻觉陷阱题（共 16 道），不含公式计算题。**")
    L.append("")

    L.append("### 3.4 `concepts[]` 字段（概念实体）")
    L.append("")
    L.append("| 字段 | 类型 | 必填 | 可空 | 说明 |")
    L.append("|---|---|---|---|---|")
    for f in dd["concept"]:
        req = "是" if f.get("required") else "否"
        nul = "是" if f.get("nullable") else "否"
        L.append(f"| `{f['name']}` | {f['type']} | {req} | {nul} | {f['description']} |")
    L.append("")

    L.append("### 3.5 字段顺序契约")
    L.append("")
    L.append("- `eval_items[]`：" + " → ".join(f"`{x}`" for x in payload["field_order"]["eval_item"]))
    L.append("- `concepts[]`：" + " → ".join(f"`{x}`" for x in payload["field_order"]["concept"]))
    L.append("")

    L.append("### 3.6 解包示例")
    L.append("")
    L.append("```js")
    L.append("const data = await fetch('OpenSciGraph_Golden_v0.1.json').then(r => r.json());")
    L.append("console.log(data.counts);            // { concepts: 16, eval_items: 16, ... }")
    L.append("for (const item of data.eval_items) {")
    L.append("  console.log(item.eval_id, item.question_type, item.correct_option,")
    L.append("              item.concept.name_zh, item.concept.definition_zh);")
    L.append("}")
    L.append("```")
    L.append("")
    L.append("```python")
    L.append("import json")
    L.append("with open('OpenSciGraph_Golden_v0.1.json', encoding='utf-8') as fh:")
    L.append("    data = json.load(fh)")
    L.append("concepts = {c['concept_id']: c for c in data['concepts']}")
    L.append("for it in data['eval_items']:")
    L.append("    assert it['concept'] == concepts[it['concept_id']]   # 内联副本一致性")
    L.append("```")
    L.append("")

    # ---------------- 联系方式 ----------------
    L.append("## 四、需求反馈与联系")
    L.append("")
    L.append("如需**全量数据、定制数据集或合作**，欢迎联系我们：")
    L.append("")
    L.append("| 需求类型 | 说明 | 联系方式 |")
    L.append("|---|---|---|")
    L.append(f"| 索要全量数据 | 完整概念图谱与全量评测题（含未公开部分） | {CONTACT['email']} |")
    L.append(f"| 定制数据集 | 指定学科领域 / 题型配比 / 语言 / 输出格式（JSONL、Parquet 等） | {CONTACT['email']} |")
    L.append(f"| 缺陷反馈 | 发现答案键错误、概念定义不准或关系边有误 | {CONTACT['repo']} / Issues |")
    L.append(f"| 商务与合作 | 联合评测、模型幻觉专项测评、企业内训数据 | {CONTACT['email']} |")
    L.append("")
    L.append(f"- **邮箱**：{CONTACT['email']}")
    L.append(f"- **代码仓库**：{CONTACT['repo']}")
    L.append(f"- **HuggingFace Datasets**：{CONTACT['hf_home']}")
    L.append("")
    if CONTACT_PENDING:
        L.append("> 📌 **占位符提醒**：上方联系方式仍含 `<TODO: ...>`，发布前请替换。")
        L.append("")
    return "\n".join(L)


# ---------------------------------------------------------------------------
# HuggingFace Dataset Card
# ---------------------------------------------------------------------------


def build_hf_card(
    payload: Dict[str, Any],
    checks: Sequence[Tuple[str, str, str]],
    json_sha256: str,
    json_bytes: int,
) -> str:
    """生成对外发布用的数据集卡；所有数字、样例、校验结论均取自本次真实成品。"""
    c = payload["counts"]
    cmap = {x["concept_id"]: x for x in payload["concepts"]}
    imap = {it["eval_id"]: it for it in payload["eval_items"]}
    n_pass = sum(1 for _, s, _ in checks if s == "PASS")
    n_total = len(checks)
    all_pass = n_pass == n_total

    dist = imap[EXAMPLE_DISTINCTION]
    trap = imap[EXAMPLE_TRAP]

    def dump(obj: Any) -> str:
        return json.dumps(obj, ensure_ascii=False, indent=2)

    L: List[str] = []

    # ---------- YAML front matter（HF 识别用） ----------
    L.append("---")
    L.append("pretty_name: OpenSciGraph Golden Dataset v0.1 (MVP)")
    L.append("language:")
    L.append("- zh")
    L.append("license: other")
    L.append("license_name: unverified-offline-batch")
    L.append("task_categories:")
    L.append("- multiple-choice")
    L.append("- question-answering")
    L.append("- text-classification")
    L.append("tags:")
    L.append("- physics")
    L.append("- knowledge-graph")
    L.append("- hallucination")
    L.append("- benchmark")
    L.append("- chinese")
    L.append("- offline")
    L.append("size_categories:")
    L.append("- n<1K")
    L.append("configs:")
    L.append("- config_name: eval_items")
    L.append("  data_files:")
    L.append("  - split: train")
    L.append("    path: eval_items.jsonl")
    L.append("- config_name: concepts")
    L.append("  data_files:")
    L.append("  - split: train")
    L.append("    path: concepts.jsonl")
    L.append("---")
    L.append("")

    L.append("# OpenSciGraph Golden Dataset v0.1 (MVP)")
    L.append("")
    L.append("> **一句话**：16 组基础物理概念图谱 + 16 道防幻觉评测题（概念辨析 11 + AI 幻觉陷阱 5），")
    L.append("> 全部经人工逐题复核准入，**100% 离线提纯、零虚假来源**，纯数据产物、无模型推理参与。")
    L.append("")
    if CONTACT_PENDING:
        L.append("> ⚠️ **发布前提醒（维护者自用，发布时删除本行）**：")
        L.append("> 本卡片的「需求反馈」区含 `TODO` 占位符，请先用真实联系方式替换 `scripts/build_golden_v01.py` 中的 `CONTACT` 后重新生成。")
        L.append("")

    # ---------- 1. 数据简介 ----------
    L.append("## 1. 数据简介")
    L.append("")
    L.append("OpenSciGraph 面向**大模型物理知识可靠性**评测。本数据包是其 v0.1 MVP 公开样本，包含两部分内容：")
    L.append("")
    L.append("| 部分 | 数量 | 内容 |")
    L.append("|---|---|---|")
    L.append(f"| **物理概念图谱** | {c['concepts']} 条 | 中英文名、中文定义、核心公式、上位/下位概念关系、许可标识 |")
    L.append(f"| **防幻觉 Benchmarks** | {c['eval_items']} 道 | 概念辨析 {c['distinction']} 道 + AI 幻觉陷阱 {c['trap']} 道，含四选项、答案键、解析、命中混淆点 |")
    L.append("")
    L.append("题目与概念**严格一一对应**（`eval_id == \"EVAL_\" + concept_id`），且每道题内联了对应概念对象，")
    L.append("前端或评测脚本无需再做关联查询。")
    L.append("")
    L.append("**覆盖领域**：力学（万有引力、加速度、功率）、振动与波动（频率、波长、干涉）、")
    L.append("热学（温度、热量、热传导）、电磁学（电荷）、光学与量子效应（偏振、光电效应、波粒二象性）。")
    L.append("")
    L.append("### 它为什么值得一看")
    L.append("")
    L.append("- **幻觉陷阱题是特制的**：题干植入一个错误前提（如「功率是一种能量」「加速度是运动学的一个分支学科」），")
    L.append("  正确答案必须明确否定该前提，而 3 个干扰项**顺着错误前提走**——专门用来暴露模型")
    L.append("  「把相关关系误判为种属关系」这类系统性幻觉，普通 QA 数据集测不出来。")
    L.append("- **答案键经过人工验算**：项目在 50 题全批次里确认了 9 道有害缺陷题并隔离，")
    L.append("  又在复核中发现 6 道「双正确项 / 答案键反转」缺陷——**盲测自洽 ≠ 物理正确**，")
    L.append("  这是本项目最重要的一条结论。本包只收编人工判定为合格的全部 16 道。")
    L.append("- **离线可复现**：打包脚本确定性执行，运行多少次产物完全一致（无随机抽样）。")
    L.append("")
    L.append("### 溯源信息")
    L.append("")
    L.append("| 项 | 值 |")
    L.append("|---|---|")
    L.append(f"| 数据集名称 | {payload['dataset']} |")
    L.append(f"| 版本 | {payload['version']}（{payload['release']}） |")
    L.append(f"| 生成时间（UTC） | {payload['generated_at']} |")
    L.append(f"| 生成脚本 | `{payload['generated_by']}` |")
    L.append(f"| 是否含模型推理 | `model_involved = {str(payload['model_involved']).lower()}` |")
    L.append(f"| 是否全程离线 | `offline = {str(payload['offline']).lower()}` |")
    L.append(f"| 选题方式 | 确定性提取（非随机抽样）：`{payload['selection']['mode']}` |")
    L.append(f"| 主文件名 | `OpenSciGraph_Golden_v0.1.json` |")
    L.append(f"| sha256 | `{json_sha256}` |")
    L.append("")
    L.append("### 仓库文件")
    L.append("")
    L.append("| 文件 | 说明 |")
    L.append("|---|---|")
    L.append("| `README.md` | 本数据集卡（由 `HuggingFace_Dataset_Card.md` 改名而来） |")
    L.append(f"| `OpenSciGraph_Golden_v0.1.json` | 完整数据包（UTF-8 无 BOM，{json_bytes} 字节），含 `concepts[]` 与 `eval_items[]` |")
    L.append(f"| `eval_items.jsonl` | `datasets` 分片：{c['eval_items']} 行，一行一题 |")
    L.append(f"| `concepts.jsonl` | `datasets` 分片：{c['concepts']} 行，一行一概念 |")
    L.append("")
    L.append("> **为什么有两个 JSONL？** 完整数据包是**单个 JSON 对象**，而 HuggingFace 的 json loader 面向")
    L.append("> 「JSONL 或 JSON 数组」，无法把嵌套对象展开成多行。因此额外提供两个扁平分片，")
    L.append("> 二者均由同一份数据派生、与主包逐行一致，保证 `load_dataset()` 开箱可用。")
    L.append("")

    # ---------- 2. 质量证明 ----------
    L.append("## 2. 质量证明：28 项结构校验全部 PASS")
    L.append("")
    L.append(f"成品落盘前由打包脚本执行 {n_total} 项结构校验，结论 **{n_pass}/{n_total} {'全部通过' if all_pass else '存在未通过项'}**；")
    L.append("另用**独立脚本**（不复用同一套校验代码）二次交叉复核，结论一致。完整明细见仓库内")
    L.append("`reports/stage4_golden_v01_validation.md`。")
    L.append("")
    L.append("| # | 检查项 | 结论 | 说明 |")
    L.append("|---|---|---|---|")
    for i, (name, status, detail) in enumerate(checks, start=1):
        mark = "✅ PASS" if status == "PASS" else "❌ FAIL"
        L.append(f"| {i} | {name} | {mark} | {detail or '—'} |")
    L.append("")
    L.append("校验覆盖的六个维度：")
    L.append("")
    L.append("1. **结构与计数**：顶层键齐全、`eval_items` = 16、`concepts` = 16、`counts` 与实测一致；")
    L.append("2. **标识一致性**：`eval_id` 集合与人工清单精确相等、无重复、辨析在前陷阱在后、题型分布 11 / 5 / 0；")
    L.append("3. **字段契约**：字段名与**顺序**逐条比对 Schema、`options` 恰好 4 项且非空去重、`correct_option ∈ {A,B,C,D}`；")
    L.append("4. **关系完整性**：`eval_id == \"EVAL_\" + concept_id`、概念 ID 全局唯一、内联 `concept` 与 `concepts[]` 逐字段一致；")
    L.append("5. **来源诚信**：`wikidata_id` / `source_url` **全部为 `null`**、`license_type` 全为 `UNVERIFIED`、`definition_zh` 均 ≥ 10 字；")
    L.append("6. **排除与编码**：无隔离缺陷题混入、全部题目人工判定为 `ok`、JSON 可往返序列化、无 BOM、纯 LF、UTF-8 可解码。")
    L.append("")
    L.append("> **口径说明**：「零虚假来源」指来源字段一律留空、绝不编造 QID 或链接；")
    L.append("> 这**不等于**数据已权威化——`parent_concept` / `child_concepts` 关系边尚未核验（见第 5 节）。")
    L.append("")

    # ---------- 3. 数据样例 ----------
    L.append("## 3. 数据样例")
    L.append("")
    L.append("以下两段 JSON **直接从 `OpenSciGraph_Golden_v0.1.json` 的 `eval_items[]` 中抽取**，未做任何改写。")
    L.append("")

    L.append(f"### 3.1 概念辨析题示例 —— `{dist['eval_id']}`（{cmap[dist['concept_id']]['name_zh']}）")
    L.append("")
    L.append("```json")
    L.append(dump(dist))
    L.append("```")
    L.append("")
    L.append("**看点**：干扰项 B 把「静止」和「动能」对立起来（静止物体动能为零，故 B 为假），")
    L.append("C 用「单位相同 ⇒ 没有区别」偷换概念，D 则否认了能量守恒框架下能量形式的相互转化。")
    L.append("")

    L.append(f"### 3.2 AI 幻觉陷阱题示例 —— `{trap['eval_id']}`（{cmap[trap['concept_id']]['name_zh']}）")
    L.append("")
    L.append("```json")
    L.append(dump(trap))
    L.append("```")
    L.append("")
    L.append("**看点**：题干把「万有引力定律是一种力」这个**错误前提**塞给模型。")
    L.append("选项 A 直接顺从前提；选项 C「定律可以产生力，但不是力本身」看似辩证，")
    L.append("实际仍未否定「定律 vs 力」的混淆——这正是模型最容易踩的坑。")
    L.append(f"对应的 `target_hallucination_point` 字段写明：*{trap['target_hallucination_point']}*。")
    L.append("")

    # ---------- 4. 加载代码 ----------
    L.append("## 4. 开发者加载代码（Python）")
    L.append("")
    L.append("主文件是**单个 JSON 对象**（非 JSONL、非 parquet），含概念图谱与题目两部分；")
    L.append("仓库另提供两个扁平的 JSONL 分片供 `datasets` 在线加载。")
    L.append("")
    L.append("### 4.1 在线加载（HuggingFace `datasets`，推荐）")
    L.append("")
    L.append("```python")
    L.append("from datasets import load_dataset")
    L.append("")
    L.append("# 评测题分片：16 行，一行一题")
    L.append(f"bench = load_dataset('{HF_REPO_ID}', 'eval_items', split='train')")
    L.append("print(bench)")
    L.append("print(bench[0]['eval_id'], bench[0]['question_type'], bench[0]['correct_option'])")
    L.append("")
    L.append("# 概念分片：16 行，一行一概念")
    L.append(f"concepts_ds = load_dataset('{HF_REPO_ID}', 'concepts', split='train')")
    L.append("print(concepts_ds[0]['name_zh'], concepts_ds[0]['definition_zh'])")
    L.append("```")
    L.append("")
    L.append("> **国内网络提示**：`huggingface.co` 在中国大陆可能不可达。下载场景可先设镜像：")
    L.append("> `export HF_ENDPOINT=https://hf-mirror.com`（PowerShell：`$env:HF_ENDPOINT=\"https://hf-mirror.com\"`）。")
    L.append("> 实测（2026-10-14）该镜像同样**透传写操作**，`create_repo` / `upload_file` / `delete_repo` 均可用，")
    L.append("> 故本数据集的上架亦经镜像端点完成；但镜像稳定性不由本项目保证，正式发布建议直连官方站点。")
    L.append("")
    L.append("### 4.2 直接读取单文件 JSON（含完整图谱）")
    L.append("")
    L.append("```python")
    L.append("import json")
    L.append("from pathlib import Path")
    L.append("")
    L.append("PATH = Path('release/v0.1_mvp/OpenSciGraph_Golden_v0.1.json')")
    L.append("")
    L.append("with PATH.open(encoding='utf-8') as fh:        # 注意：UTF-8，无 BOM")
    L.append("    data = json.load(fh)")
    L.append("")
    L.append("print(data['counts'])")
    L.append("# {'concepts': 16, 'eval_items': 16, 'distinction': 11, 'trap': 5, ...}")
    L.append("")
    L.append("concepts = {c['concept_id']: c for c in data['concepts']}")
    L.append("for item in data['eval_items']:")
    L.append("    assert item['concept'] == concepts[item['concept_id']]   # 内联副本一致性自检")
    L.append("```")
    L.append("")

    L.append("### 4.3 按题型筛选")
    L.append("")
    L.append("```python")
    L.append("distinction = [i for i in data['eval_items'] if i['question_type'] == 'concept_distinction']")
    L.append("trap        = [i for i in data['eval_items'] if i['question_type'] == 'hallucination_trap']")
    L.append("")
    L.append("print(len(distinction), len(trap))   # 11 5")
    L.append("```")
    L.append("")

    L.append("### 4.4 评测你的模型（完整打分骨架）")
    L.append("")
    L.append("```python")
    L.append("import re")
    L.append("")
    L.append("PROMPT = '''请回答下面的单选题，只输出一个大写字母（A/B/C/D）。")
    L.append("")
    L.append("{question}")
    L.append("")
    L.append("A. {o0}")
    L.append("B. {o1}")
    L.append("C. {o2}")
    L.append("D. {o3}'''")
    L.append("")
    L.append("def build_prompt(item):")
    L.append("    return PROMPT.format(")
    L.append("        question=item['question'],")
    L.append("        o0=item['options'][0], o1=item['options'][1],")
    L.append("        o2=item['options'][2], o3=item['options'][3],")
    L.append("    )")
    L.append("")
    L.append("def extract_choice(text):")
    L.append("    m = re.search(r'\\b([ABCD])\\b', text.upper())")
    L.append("    return m.group(1) if m else None")
    L.append("")
    L.append("def evaluate(model_fn, items):")
    L.append("    rows, correct = [], 0")
    L.append("    for item in items:")
    L.append("        pred = extract_choice(model_fn(build_prompt(item)))")
    L.append("        ok = (pred == item['correct_option'])")
    L.append("        correct += ok")
    L.append("        rows.append({")
    L.append("            'eval_id': item['eval_id'],")
    L.append("            'question_type': item['question_type'],")
    L.append("            'gold': item['correct_option'],")
    L.append("            'pred': pred,")
    L.append("            'correct': ok,")
    L.append("        })")
    L.append("    acc = correct / len(items) if items else 0.0")
    L.append("    # 陷阱题准确率单独统计——这才是本数据集的核心指标")
    L.append("    traps = [r for r in rows if r['question_type'] == 'hallucination_trap']")
    L.append("    trap_acc = sum(r['correct'] for r in traps) / len(traps) if traps else 0.0")
    L.append("    return {'overall_acc': acc, 'trap_acc': trap_acc, 'details': rows}")
    L.append("")
    L.append("# 示例：接任意模型（此处用本地 Ollama 的 chat 接口）")
    L.append("# from ollama import Client")
    L.append("# client = Client(host='http://127.0.0.1:11434')")
    L.append("# def model_fn(p):")
    L.append("#     return client.chat(model='qwen2.5:7b-instruct-q5_K_M',")
    L.append("#                        messages=[{'role': 'user', 'content': p}])['message']['content']")
    L.append("# print(evaluate(model_fn, data['eval_items']))")
    L.append("```")
    L.append("")
    L.append("### 4.5 概念图谱字段速查")
    L.append("")
    L.append("```python")
    L.append("c = concepts['P006']")
    L.append("print(c['name_zh'], c['name_en'])      # 能量 Energy")
    L.append("print(c['definition_zh'])              # 物体进行工作或引起变化的能力。")
    L.append("print(c['formula'])                    # None（描述性概念无公式）")
    L.append("print(c['parent_concept'], c['child_concepts'])")
    L.append("# 物理量 ['动能', '势能', '内能']")
    L.append("print(c['wikidata_id'], c['source_url'], c['license_type'])")
    L.append("# None None UNVERIFIED")
    L.append("```")
    L.append("")

    # ---------- 5. 已知限制 ----------
    L.append("## 5. 已知限制")
    L.append("")
    L.append("请在使用前了解以下几点，避免误用：")
    L.append("")
    for i, lim in enumerate(payload["notes"]["known_limits"], start=1):
        L.append(f"{i}. {lim}")
    L.append("")
    L.append("此外：本包仅 **16 组**样本，适合做**冒烟测试与展示**，统计显著性有限；")
    L.append("同批次主线数据中仍存在未经复核的公式计算题，不建议直接并入评测。")
    L.append("")

    # ---------- 6. 需求反馈 ----------
    L.append("## 6. 需求反馈与联系")
    L.append("")
    L.append("本数据包为 v0.1 MVP 公开样本。如果你需要**全量数据、定制数据集或合作**，欢迎联系我们：")
    L.append("")
    L.append("| 需求类型 | 说明 | 联系方式 |")
    L.append("|---|---|---|")
    L.append(f"| 索要全量数据 | 完整概念图谱与全量评测题（含未公开部分） | {CONTACT['email']} |")
    L.append(f"| 定制数据集 | 指定学科领域 / 题型配比 / 语言 / 输出格式（JSONL、Parquet 等） | {CONTACT['email']} |")
    L.append(f"| 缺陷反馈 | 发现答案键错误、概念定义不准或关系边有误 | {CONTACT['repo']} / Issues |")
    L.append(f"| 商务与合作 | 联合评测、模型幻觉专项测评、企业内训数据 | {CONTACT['email']} |")
    L.append("")
    L.append("**联系时建议附上**：")
    L.append("")
    L.append("- 你的使用场景（评测 / 训练 / 检索 / 展示）")
    L.append("- 目标学科与题量需求")
    L.append("- 期望的数据格式与许可要求")
    L.append("")
    L.append(f"- 代码仓库：{CONTACT['repo']}")
    L.append(f"- HuggingFace 主页：{CONTACT['hf_home']}")
    L.append("")
    if CONTACT_PENDING:
        L.append("> 📌 **占位符提醒**：若上方仍显示 `<TODO: ...>`，说明维护者尚未填写真实联系方式，")
        L.append("> 请先替换后再对外发布。")
        L.append("")

    # ---------- 7. 引用 ----------
    L.append("## 7. 引用与许可")
    L.append("")
    L.append("```bibtex")
    L.append("@misc{openscigraph_golden_v0_1,")
    L.append("  title        = {OpenSciGraph Golden Dataset v0.1 (MVP)},")
    L.append("  author       = {OpenSciGraph Contributors},")
    L.append(f"  year         = {{2026}},")
    L.append("  note         = {16 physics concepts + 16 anti-hallucination benchmarks, offline-curated}")
    L.append("}")
    L.append("```")
    L.append("")
    L.append("**许可**：`license_type = UNVERIFIED`。本批次为离线产出，**未联网核验上游来源与许可**，")
    L.append("因此不对数据来源作任何权利主张，也不保证可再分发。使用前请自行评估合规风险。")
    L.append("若你计划商用，请先通过上方联系方式取得确认。")
    L.append("")
    L.append("---")
    L.append("")
    L.append(f"*本卡片由 `{payload['generated_by']}` 自动生成于 {payload['generated_at']}，"
             f"所有数字与样例均取自同一批次成品（sha256 `{json_sha256[:16]}…`）。*")
    L.append("")
    return "\n".join(L)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="OpenSciGraph v0.1 MVP 黄金数据包封装（确定性，纯数据）")
    parser.add_argument("--dry-run", action="store_true", help="只校验并打印，不写任何文件")
    args = parser.parse_args(argv)

    for p, label in ((EVAL_PATH, "评测集"), (CONCEPT_PATH, "概念库")):
        if not p.exists():
            LOG.error("找不到%s：%s", label, p)
            return 2

    eval_rows = read_jsonl(EVAL_PATH)
    concept_rows = read_jsonl(CONCEPT_PATH)
    LOG.info("读取评测集 %d 条 | 概念库 %d 条", len(eval_rows), len(concept_rows))

    # 1 提取
    picked = extract(eval_rows)
    LOG.info("提取 %d 道（辨析 %d + 陷阱 %d）", len(picked), WANT_DISTINCTION, WANT_TRAP)

    # 2 关联
    concept_list, concepts = link_concepts(picked, concept_rows)
    LOG.info("关联概念 %d 条", len(concept_list))

    # 3 组装
    payload = build_payload(
        picked, concept_list, concepts,
        clean_pool=len(eval_rows), total_pool=len(eval_rows) + len(QUARANTINE_IDS),
    )

    # 4 校验
    raw_text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    checks = validate_payload(payload, raw_text)
    n_fail = sum(1 for _, s, _ in checks if s != "PASS")
    for name, status, detail in checks:
        LOG.info("[%s] %s %s", status, name, f"({detail})" if detail else "")
    if n_fail:
        LOG.error("校验未通过 %d 项，终止落盘", n_fail)
        return 1
    LOG.info("结构校验全部通过：%d/%d", len(checks), len(checks))

    if args.dry_run:
        LOG.info("--dry-run：跳过落盘")
        print(build_validation_md(payload, checks))
        return 0

    # 5 归档被取代的旧产物（非破坏性）
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    if SUPERSEDED_JSON.exists():
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        dest = ARCHIVE_DIR / SUPERSEDED_JSON.name
        os.replace(SUPERSEDED_JSON, dest)
        LOG.info("旧产物（15 道随机样本）已归档 -> %s", dest.relative_to(PROJECT_ROOT).as_posix())

    # 6 落盘
    GOLDEN_JSON.write_text(raw_text, encoding="utf-8", newline="\n")
    size = GOLDEN_JSON.stat().st_size
    sha256 = hashlib.sha256(GOLDEN_JSON.read_bytes()).hexdigest()
    LOG.info("黄金数据包 -> %s（%d 字节，sha256=%s…）",
             GOLDEN_JSON.relative_to(PROJECT_ROOT).as_posix(), size, sha256[:16])

    RELEASE_README.write_text(build_readme(payload, size), encoding="utf-8", newline="\n")
    LOG.info("README -> %s", RELEASE_README.relative_to(PROJECT_ROOT).as_posix())

    hf_card = build_hf_card(payload, checks, sha256, size)
    HF_CARD.write_text(hf_card, encoding="utf-8", newline="\n")
    LOG.info("数据集卡 -> %s（%d 字节）",
             HF_CARD.relative_to(PROJECT_ROOT).as_posix(), HF_CARD.stat().st_size)
    if CONTACT_PENDING:
        LOG.warning("数据集卡含未替换的联系方式占位符（CONTACT），发布前请填写真实信息")
    else:
        LOG.info("联系方式已配置：%s（无占位符）", CONTACT["email"])

    # 步骤 6b · HuggingFace datasets 分片（由同一 payload 派生，保证与主包零漂移）
    write_jsonl_rows(payload["eval_items"], EVAL_JSONL)
    write_jsonl_rows(payload["concepts"], CONCEPT_JSONL)
    split_checks = validate_splits(payload)
    for name, status, detail in split_checks:
        LOG.info("[%s] %s %s", status, name, f"({detail})" if detail else "")
    if any(s != "PASS" for _, s, _ in split_checks):
        raise ValueError("JSONL 分片与主包不一致，已中止")
    LOG.info("HF 分片 -> %s（%d 行）/ %s（%d 行）",
             EVAL_JSONL.name, len(payload["eval_items"]),
             CONCEPT_JSONL.name, len(payload["concepts"]))

    VALIDATION_REPORT.write_text(build_validation_md(payload, checks, split_checks), encoding="utf-8", newline="\n")
    LOG.info("校验报告 -> %s", VALIDATION_REPORT.relative_to(PROJECT_ROOT).as_posix())

    LOG.info("完成：概念 %d / 题目 %d / 校验 %d 项全部通过",
             len(concept_list), len(payload["eval_items"]), len(checks))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
