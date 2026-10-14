# -*- coding: utf-8 -*-
"""
OpenSciGraph 阶段二 —— 基础物理概念结构化提纯（本地离线）

用本地 Ollama 上的 qwen2.5:7b-instruct-q5_K_M，把 config 中的物理概念清单
提纯成 V2 结构化记录，写入 data/processed/physics_concepts_v2.jsonl。

设计要点
--------
1. **全程离线**：只访问 http://127.0.0.1:11434/api/chat。
   脚本内部显式禁用 urllib 的代理（ProxyHandler({})），
   因此不存在走 HTTP(S)_PROXY 出网的可能。
2. **结构化输出**：请求体带 "format": "json"，由 Ollama 的
   JSON 语法约束采样，从生成层面杜绝 Markdown 围栏等杂质。
   脚本仍保留一层防御性清洗，并据此统计「零污染率」。
3. **标识字段不由模型决定**：concept_id / name_zh / name_en 以
   config 清单为权威值，模型输出会被覆盖，防止 ID 漂移。
   wikidata_id / source_url 离线无法核验，按项目纪律一律写 null，
   不填写模型凭记忆生成的未核验值（README 第 5 节）。
4. **写入保护**：输出路径统一走 src.common.assert_writable()，
   data/raw 依旧不可写。
5. **幂等**：默认跳过输出文件中已存在的 concept_id；--force 才整体重建。

用法（在 E:\\OpenSciGraph 下）
------------------------------
    .\\.venv\\Scripts\\python.exe scripts\\clean_physics_v2.py --seed-only --force

常用参数
--------
    --limit N        只处理清单中前 N 条（与 --seed-only 二选一）
    --seed-only      只处理清单里 seed_batch 标记的 10 条
    --force          覆盖已有输出（默认断点续跑，跳过已完成的 concept_id）
    --no-format-json 关闭 Ollama 的 JSON 约束，用于对比实验
    --qid-policy     留空字段策略：null（默认，推荐）/ model（会写入未核验 QID）
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# 复用阶段一基础设施（src/common.py）
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.common import (  # noqa: E402
    CONFIG_DIR,
    INTERIM_DIR,
    PROCESSED_DIR,
    QID_PATTERN,
    REPORTS_DIR,
    assert_writable,
    is_blank,
    load_config,
    relative_to_project,
    setup_logger,
    timestamp_slug,
    utc_now_iso,
    write_json_report,
)

LOG = setup_logger("physics_v2")

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

SCHEMA_FILE = CONFIG_DIR / "physics_v2_schema.json"
DEFAULT_CATALOG = CONFIG_DIR / "physics_concepts_100_catalog.json"
DEFAULT_OUTPUT = PROCESSED_DIR / "physics_concepts_v2.jsonl"
DEFAULT_RAW_OUTPUT = INTERIM_DIR / "physics_concepts_v2_modelraw.jsonl"

DEFAULT_API = "http://127.0.0.1:11434/api/chat"
DEFAULT_MODEL = "qwen2.5:7b-instruct-q5_K_M"

#: V2 记录字段顺序（与 config/physics_v2_schema.json 保持一致）
V2_FIELDS: Tuple[str, ...] = (
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

#: 要求模型输出的键（内容字段）
MODEL_KEYS: Tuple[str, ...] = (
    "name_zh",
    "name_en",
    "definition_zh",
    "formula",
    "parent_concept",
    "child_concepts",
)

#: 离线批次许可占位：来源与许可未核验
LICENSE_UNVERIFIED = "UNVERIFIED"

#: definition_zh 最短长度（与 schema min_length 对齐）
DEF_MIN_LEN = 10

#: child_concepts 最多保留条数，防止模型无限列举
CHILD_MAX = 8

#: 常见学科分类名：出现 parent_concept 里通常意味着模型把「类别」当成了「上位概念」
CATEGORY_LIKE = frozenset({
    "物理学", "力学", "运动学", "动力学", "静力学", "经典力学", "量子力学",
    "热学", "热力学", "统计力学", "电磁学", "电学", "磁学", "光学", "声学",
    "流体力学", "近代物理", "核物理", "粒子物理", "相对论", "物理量",
})


# ---------------------------------------------------------------------------
# 清单读取
# ---------------------------------------------------------------------------


def load_catalog(path: Path) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """读取概念清单，返回 (概念列表, 清单元信息)。"""
    if not path.exists():
        raise FileNotFoundError(f"概念清单不存在：{path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    concepts = payload.get("concepts")
    if not isinstance(concepts, list) or not concepts:
        raise ValueError(f"清单缺少非空的 concepts 数组：{path}")
    for idx, item in enumerate(concepts, start=1):
        for key in ("concept_id", "name_zh", "name_en"):
            if key not in item:
                raise ValueError(f"清单第 {idx} 条缺少字段 {key}")
    return concepts, payload


# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------

PROMPT_TEMPLATE = """你是一位物理学科数据库编辑。请为下面这个物理概念输出一个 JSON 条目。

【概念信息】
- 中文名：{name_zh}
- 英文名：{name_en}
- 学科分类：{category}

【输出要求】
1. 只输出一个 JSON 对象。不要输出任何解释、前言、结语，不要使用 Markdown 代码块。
2. JSON 必须且只能包含下列 6 个键，键名必须完全一致：
   - "name_zh"：中文名，必须与给定的中文名完全一致
   - "name_en"：英文名，必须与给定的英文名完全一致
   - "definition_zh"：用现代汉语写的一句话物理定义，20 到 80 字，简洁准确。
     不要出现公式符号；不要用被定义的概念本身来解释自己（避免循环定义）。
   - "formula"：该概念最核心的公式，例如 "F = ma"；确实没有核心公式时填 null
   - "parent_concept"：上位概念的中文名，即比本概念更一般、更抽象的相关概念。
     判定标准：「本概念 是一种 parent_concept」应大致成立。
     不要填同义词、下位概念或无关概念。确实没有上位概念时填 null
   - "child_concepts"：下位概念中文名称组成的数组。
     对该数组中的每个 Y，「Y 是一种 本概念」应大致成立。
     尽量给出 1 到 5 个；只有该概念确实处于知识树末端时才填空数组 []
3. 除 name_en 与 formula 外，其余文字一律使用简体中文。
4. 只写物理学的标准表述，不确定的内容不要编造。

直接输出 JSON："""


def build_prompt(concept: Dict[str, Any]) -> str:
    """按概念信息构造提示词。"""
    return PROMPT_TEMPLATE.format(
        name_zh=concept.get("name_zh", ""),
        name_en=concept.get("name_en", ""),
        category=concept.get("category", "未分类"),
    )


# ---------------------------------------------------------------------------
# 本地模型调用（离线）
# ---------------------------------------------------------------------------


def make_localhost_opener() -> urllib.request.OpenerDirector:
    """
    构造一个**禁用所有代理**的 opener。

    这样即使环境里存在 HTTP_PROXY / HTTPS_PROXY，请求也不会被转发出去，
    从机制上保证脚本只能访问本机地址。
    """
    return urllib.request.build_opener(urllib.request.ProxyHandler({}))


def call_ollama(
    opener: urllib.request.OpenerDirector,
    api_url: str,
    model: str,
    prompt: str,
    timeout: int,
    temperature: float,
    use_json_format: bool,
    num_predict: int,
) -> Dict[str, Any]:
    """调用本地 Ollama /api/chat，返回原始响应字典。"""
    if not api_url.startswith(("http://127.0.0.1", "http://localhost")):
        raise ValueError(f"离线约束：只允许访问本机回环地址，收到 {api_url}")

    options: Dict[str, Any] = {
        "temperature": temperature,
        "num_predict": num_predict,
    }
    body: Dict[str, Any] = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": options,
    }
    if use_json_format:
        # Ollama 的 JSON 语法约束采样，从生成层面保证输出是合法 JSON
        body["format"] = "json"

    request = urllib.request.Request(
        api_url,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with opener.open(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


# ---------------------------------------------------------------------------
# JSON 提取与清洗
# ---------------------------------------------------------------------------

_FENCE_RE = re.compile(r"^\s*```(?:json)?\s*|\s*```\s*$", re.IGNORECASE)


def extract_json(text: str) -> Tuple[Optional[Dict[str, Any]], str, Optional[str]]:
    """
    从模型输出中提取 JSON 对象。

    返回 ``(对象, 模式, 错误)``，模式取值：

    - ``"direct"``   直接 json.loads 成功（零污染）
    - ``"repaired"`` 需要剥离 Markdown 围栏 / 截取首尾花括号后才成功
    - ``"failed"``   无法解析

    该分级是「格式校验通过率」与「零污染率」两项指标的原始依据。
    """
    if not isinstance(text, str) or not text.strip():
        return None, "failed", "模型返回空内容"

    raw = text.strip()

    # 一级：直接解析
    try:
        obj = json.loads(raw)
        if isinstance(obj, dict):
            return obj, "direct", None
        return None, "failed", f"顶层不是 JSON 对象，而是 {type(obj).__name__}"
    except json.JSONDecodeError:
        pass

    # 二级：剥离 Markdown 围栏
    stripped = _FENCE_RE.sub("", raw).strip()
    if stripped != raw:
        try:
            obj = json.loads(stripped)
            if isinstance(obj, dict):
                return obj, "repaired", None
        except json.JSONDecodeError:
            pass

    # 三级：截取第一个 { 到最后一个 }
    start, end = stripped.find("{"), stripped.rfind("}")
    if start != -1 and end > start:
        candidate = stripped[start : end + 1]
        try:
            obj = json.loads(candidate)
            if isinstance(obj, dict):
                return obj, "repaired", None
        except json.JSONDecodeError as exc:
            return None, "failed", f"JSON 解析失败：{exc.msg} (line {exc.lineno}, col {exc.colno})"

    return None, "failed", "输出中找不到可解析的 JSON 对象"


# ---------------------------------------------------------------------------
# 字段归一化与校验
# ---------------------------------------------------------------------------


def _as_text(value: Any) -> str:
    """把任意标量安全地转成去空白字符串。"""
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, list):
        return "；".join(_as_text(v) for v in value if not is_blank(v))
    return ""


def _as_nullable_text(value: Any) -> Optional[str]:
    """转成可为空的字符串，空值统一返回 None。"""
    text = _as_text(value)
    if text == "" or text.lower() in {"null", "none", "n/a", "na", "未知", "无"}:
        return None
    return text


def _as_str_list(value: Any) -> List[str]:
    """转成去重的字符串列表，缺失返回空列表。"""
    if value is None:
        return []
    if isinstance(value, str):
        parts = re.split(r"[、,，;；\n]+", value)
    elif isinstance(value, list):
        parts = value
    else:
        return []
    result: List[str] = []
    for part in parts:
        text = _as_text(part)
        if text and text.lower() not in {"null", "none", "n/a"} and text not in result:
            result.append(text)
    return result[:CHILD_MAX]


def validate_record(
    record: Dict[str, Any], expected: Dict[str, Any]
) -> Tuple[Dict[str, Any], List[str]]:
    """
    校验并归一化一条 V2 记录。

    返回 ``(归一化后的记录, 问题列表)``。问题列表为空表示完全合规。
    标识字段以清单为准强制覆盖；缺失的中文字段按既定策略保留空值并记录原因。
    """
    issues: List[str] = []

    # --- 标识字段：清单为权威值 ---
    concept_id = expected["concept_id"]
    catalog_zh = expected.get("name_zh", "")
    catalog_en = expected.get("name_en", "")

    model_zh = _as_text(record.get("name_zh"))
    if model_zh and model_zh != catalog_zh:
        issues.append(f"name_zh 与清单不一致（模型: {model_zh} / 清单: {catalog_zh}），已按清单覆盖")

    model_en = _as_text(record.get("name_en"))
    if model_en and model_en != catalog_en:
        issues.append(f"name_en 与清单不一致（模型: {model_en} / 清单: {catalog_en}），已按清单覆盖")

    name_zh = catalog_zh
    # 缺失策略：保留空值 + 记录原因
    if is_blank(name_zh):
        missing_zh_reason = "清单 name_zh 为空；离线批次无法从本地模型获得可信中文名称"
    else:
        missing_zh_reason = None

    # --- 内容字段 ---
    definition_zh = _as_text(record.get("definition_zh"))
    if len(definition_zh) < DEF_MIN_LEN:
        issues.append(f"definition_zh 过短（{len(definition_zh)} 字，要求 >= {DEF_MIN_LEN}）")

    formula = _as_nullable_text(record.get("formula"))
    parent_concept = _as_nullable_text(record.get("parent_concept"))

    if parent_concept == name_zh:
        issues.append("parent_concept 与自身同名，已置空")
        parent_concept = None
    if parent_concept and parent_concept in CATEGORY_LIKE:
        issues.append(
            f"parent_concept「{parent_concept}」疑似学科分类名而非上位概念，建议人工复核"
        )

    child_raw = record.get("child_concepts")
    if child_raw is None or isinstance(child_raw, str):
        if not is_blank(child_raw):
            issues.append("child_concepts 不是数组类型，已做归一化")
    child_concepts = _as_str_list(child_raw)
    if parent_concept and parent_concept in child_concepts:
        child_concepts = [c for c in child_concepts if c != parent_concept]
        issues.append("child_concepts 中含与 parent_concept 相同的项，已剔除")

    # --- 离线不可核验字段（依项目纪律）---
    wikidata_id = None
    source_url = None

    normalized: Dict[str, Any] = {
        "concept_id": concept_id,
        "name_zh": name_zh,
        "name_en": catalog_en,
        "wikidata_id": wikidata_id,
        "definition_zh": definition_zh,
        "formula": formula,
        "parent_concept": parent_concept,
        "child_concepts": child_concepts,
        "license_type": LICENSE_UNVERIFIED,
        "source_url": source_url,
        "missing_zh_reason": missing_zh_reason,
    }

    # --- 契约复检 ---
    if list(normalized.keys()) != list(V2_FIELDS):
        issues.append("字段顺序与 V2 契约不一致")
    if not re.match(r"^P[0-9]{3}$", str(normalized["concept_id"])):
        issues.append("concept_id 不符合 ^P[0-9]{3}$")
    if normalized["wikidata_id"] is not None and not QID_PATTERN.match(str(normalized["wikidata_id"])):
        issues.append("wikidata_id 不符合 QID 格式")
    if not isinstance(normalized["child_concepts"], list):
        issues.append("child_concepts 不是数组")
    if len(definition_zh) < DEF_MIN_LEN:
        issues.append("definition_zh 未达到 schema 最小长度要求")

    # 只有「实质性问题」才计入合规失败；名称覆盖属于正常防御
    fatal = [
        i for i in issues
        if i.startswith("definition_zh") or i.startswith("concept_id")
        or i.startswith("wikidata_id") or i.startswith("child_concepts 不是数组")
        or i.startswith("字段顺序")
    ]
    return normalized, fatal


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------


def load_done_ids(output_path: Path) -> set:
    """读取已存在的输出，收集已完成的 concept_id（用于断点续跑）。"""
    done = set()
    if not output_path.exists():
        return done
    with output_path.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict) and obj.get("concept_id"):
                done.add(obj["concept_id"])
    return done


def analyze_graph(output_path: Path) -> Dict[str, Any]:
    """
    对输出文件做事后关系质量分析（只读，用于度量「上位/下位」边的可信度）。

    统计项：
    - dangling_*_refs   ：指向本批次中不存在概念的悬空引用（知识图谱里的断边）
    - bidirectional_*   ：A 声明 parent=B 时，B 是否也把 A 列进 child_concepts
    - category_like_parent_count：把学科分类名当成上位概念的情况
    """
    records: List[Dict[str, Any]] = []
    if output_path.exists():
        with output_path.open("r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(obj, dict):
                    records.append(obj)

    if not records:
        return {"records": 0}

    by_name: Dict[str, Dict[str, Any]] = {}
    for record in records:
        for key in ("name_zh", "name_en"):
            value = record.get(key)
            if value:
                by_name.setdefault(value, record)

    parent_edges: List[Tuple[str, str]] = []
    dangling_parent: List[Dict[str, str]] = []
    for record in records:
        parent = record.get("parent_concept")
        if not parent:
            continue
        parent_edges.append((record["name_zh"], parent))
        if parent not in by_name:
            dangling_parent.append({"concept": record["name_zh"], "parent": parent})

    child_edges: List[Tuple[str, str]] = []
    dangling_child: List[Dict[str, str]] = []
    for record in records:
        for child in record.get("child_concepts") or []:
            child_edges.append((record["name_zh"], child))
            if child not in by_name:
                dangling_child.append({"concept": record["name_zh"], "child": child})

    checked = closed = 0
    for concept, parent in parent_edges:
        if parent not in by_name:
            continue  # 跨批次的外部概念，暂不计入闭合率分母
        checked += 1
        if concept in (by_name[parent].get("child_concepts") or []):
            closed += 1

    return {
        "records": len(records),
        "parent_edges": len(parent_edges),
        "child_edges": len(child_edges),
        "null_parent_count": sum(1 for r in records if not r.get("parent_concept")),
        "avg_children_per_record": round(
            sum(len(r.get("child_concepts") or []) for r in records) / len(records), 2
        ),
        "category_like_parent_count": sum(
            1 for r in records if (r.get("parent_concept") or "") in CATEGORY_LIKE
        ),
        "dangling_parent_refs": dangling_parent,
        "dangling_child_refs": dangling_child,
        "bidirectional_checked": checked,
        "bidirectional_closed": closed,
        "bidirectional_closure_rate": round(closed / checked, 4) if checked else None,
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="OpenSciGraph 阶段二：基础物理概念结构化提纯（本地离线）"
    )
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG, help="概念清单 JSON")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="输出 JSONL")
    parser.add_argument("--raw-output", type=Path, default=DEFAULT_RAW_OUTPUT, help="模型原始输出留档 JSONL")
    parser.add_argument("--report", type=Path, default=None, help="报告 JSON 路径（默认带时间戳）")
    parser.add_argument("--api-url", default=DEFAULT_API, help="Ollama 接口地址（仅允许本机）")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="模型名")
    parser.add_argument("--limit", type=int, default=0, help="只处理前 N 条；0 表示全部")
    parser.add_argument("--seed-only", action="store_true", help="只处理清单 seed_batch 中的种子概念")
    parser.add_argument("--force", action="store_true", help="覆盖已有输出（默认断点续跑）")
    parser.add_argument("--temperature", type=float, default=0.2, help="采样温度")
    parser.add_argument("--num-predict", type=int, default=512, help="单条最大生成 token 数")
    parser.add_argument("--timeout", type=int, default=300, help="单次请求超时（秒）")
    parser.add_argument("--no-format-json", action="store_true", help="关闭 Ollama JSON 约束（对比实验用）")
    parser.add_argument("--qid-policy", choices=["null", "model"], default="null",
                        help="wikidata_id 填充策略：null（默认，离线不臆造）/ model（写入未核验值）")
    args = parser.parse_args(argv)

    cfg = load_config()
    use_json_format = not args.no_format_json

    # ---- 清单 ----
    concepts, catalog_meta = load_catalog(args.catalog)
    if args.seed_only:
        seed_ids = set(catalog_meta.get("seed_batch", {}).get("concept_ids", []))
        concepts = [c for c in concepts if c["concept_id"] in seed_ids]
    elif args.limit and args.limit > 0:
        concepts = concepts[: args.limit]

    # ---- 输出路径（写入保护）----
    output_path = assert_writable(args.output)
    raw_path = assert_writable(args.raw_output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.parent.mkdir(parents=True, exist_ok=True)

    report_path = args.report or (REPORTS_DIR / f"physics_v2_run_{timestamp_slug()}.json")
    assert_writable(report_path)

    # ---- 幂等处理 ----
    done_ids = set() if args.force else load_done_ids(output_path)
    todo = [c for c in concepts if c["concept_id"] not in done_ids]

    LOG.info("=" * 68)
    LOG.info("OpenSciGraph 阶段二 · 物理概念结构化提纯（离线）")
    LOG.info("模型      : %s", args.model)
    LOG.info("接口      : %s", args.api_url)
    LOG.info("JSON 约束 : %s", "开启 (format=json)" if use_json_format else "关闭")
    LOG.info("QID 策略  : %s", args.qid_policy)
    LOG.info("清单总数  : %d 条；本次待处理 %d 条（已完成跳过 %d 条）",
             len(concepts), len(todo), len(concepts) - len(todo))
    LOG.info("输出      : %s", relative_to_project(output_path))
    LOG.info("=" * 68)

    opener = make_localhost_opener()

    # ---- 逐条处理 ----
    mode_counter: Dict[str, int] = {"direct": 0, "repaired": 0, "failed": 0}
    schema_ok = 0
    api_errors = 0
    total_eval_tokens = 0
    total_eval_ns = 0
    total_prompt_tokens = 0
    per_item: List[Dict[str, Any]] = []

    mode = "a" if (done_ids and not args.force) else "w"
    raw_mode = "a" if (done_ids and not args.force) else "w"

    run_start = time.perf_counter()
    with output_path.open(mode, encoding="utf-8", newline="\n") as out_fh, \
            raw_path.open(raw_mode, encoding="utf-8", newline="\n") as raw_fh:

        for index, concept in enumerate(todo, start=1):
            cid = concept["concept_id"]
            prompt = build_prompt(concept)
            t0 = time.perf_counter()
            error: Optional[str] = None
            response: Dict[str, Any] = {}

            try:
                response = call_ollama(
                    opener=opener,
                    api_url=args.api_url,
                    model=args.model,
                    prompt=prompt,
                    timeout=args.timeout,
                    temperature=args.temperature,
                    use_json_format=use_json_format,
                    num_predict=args.num_predict,
                )
            except urllib.error.URLError as exc:
                error = f"接口调用失败：{exc}"
            except json.JSONDecodeError as exc:
                error = f"接口返回非 JSON：{exc}"
            except Exception as exc:  # noqa: BLE001
                error = f"{type(exc).__name__}: {exc}"

            elapsed = time.perf_counter() - t0

            if error:
                api_errors += 1
                mode_counter["failed"] += 1
                LOG.error("[%d/%d] %s %s -> %s", index, len(todo), cid, concept.get("name_zh"), error)
                per_item.append({"concept_id": cid, "name_zh": concept.get("name_zh"),
                                 "status": "api_error", "error": error, "wall_s": round(elapsed, 3)})
                continue

            content = (response.get("message") or {}).get("content", "")
            obj, parse_mode, parse_error = extract_json(content)
            mode_counter[parse_mode] += 1

            eval_count = int(response.get("eval_count") or 0)
            eval_ns = int(response.get("eval_duration") or 0)
            prompt_count = int(response.get("prompt_eval_count") or 0)
            total_eval_tokens += eval_count
            total_eval_ns += eval_ns
            total_prompt_tokens += prompt_count

            # 原始输出留档（审计用）
            raw_fh.write(json.dumps({
                "concept_id": cid,
                "model": response.get("model"),
                "created_at": response.get("created_at"),
                "raw_content": content,
                "parse_mode": parse_mode,
                "parse_error": parse_error,
                "wall_s": round(elapsed, 3),
                "eval_count": eval_count,
                "eval_duration_ns": eval_ns,
                "prompt_eval_count": prompt_count,
                "load_duration_ns": int(response.get("load_duration") or 0),
                "total_duration_ns": int(response.get("total_duration") or 0),
            }, ensure_ascii=False) + "\n")

            if obj is None:
                LOG.error("[%d/%d] %s %s -> 格式校验失败：%s",
                          index, len(todo), cid, concept.get("name_zh"), parse_error)
                per_item.append({"concept_id": cid, "name_zh": concept.get("name_zh"),
                                 "status": "parse_failed", "parse_mode": parse_mode,
                                 "error": parse_error, "wall_s": round(elapsed, 3)})
                continue

            # QID 策略
            if args.qid_policy == "model":
                candidate = _as_text(obj.get("wikidata_id"))
                obj["wikidata_id"] = candidate if QID_PATTERN.match(candidate) else None

            record, issues = validate_record(obj, concept)
            ok = not issues
            schema_ok += 1 if ok else 0

            out_fh.write(json.dumps(record, ensure_ascii=False) + "\n")
            out_fh.flush()

            tok_s = eval_count / (eval_ns / 1e9) if eval_ns else 0.0
            LOG.info("[%d/%d] %s %-16s | %s | %5.2fs | %3d tok | %5.1f tok/s%s",
                     index, len(todo), cid, concept.get("name_zh", ""),
                     parse_mode, elapsed, eval_count, tok_s,
                     "" if ok else f" | 告警 {len(issues)}")
            for issue in issues:
                LOG.warning("        · %s", issue)

            per_item.append({
                "concept_id": cid,
                "name_zh": concept.get("name_zh"),
                "status": "ok",
                "parse_mode": parse_mode,
                "schema_ok": ok,
                "issues": issues,
                "wall_s": round(elapsed, 3),
                "eval_count": eval_count,
                "prompt_eval_count": prompt_count,
                "tokens_per_sec": round(tok_s, 2),
                "definition_len": len(record["definition_zh"]),
                "has_formula": record["formula"] is not None,
            })

    total_wall = time.perf_counter() - run_start
    processed = len(todo)
    parse_ok = mode_counter["direct"] + mode_counter["repaired"]

    summary: Dict[str, Any] = {
        "run_at": utc_now_iso(),
        "stage": 2,
        "task": "物理概念结构化提纯（离线）",
        "model": args.model,
        "api_url": args.api_url,
        "json_format_enforced": use_json_format,
        "qid_policy": args.qid_policy,
        "catalog": relative_to_project(args.catalog),
        "catalog_total": len(catalog_meta.get("concepts", [])),
        "selected": len(concepts),
        "processed": processed,
        "skipped_already_done": len(concepts) - processed,
        "output": relative_to_project(output_path),
        "raw_output": relative_to_project(raw_path),
        "elapsed_seconds": round(total_wall, 3),
        "elapsed_per_item_avg_s": round(total_wall / processed, 3) if processed else None,
        "tokens": {
            "prompt_total": total_prompt_tokens,
            "generated_total": total_eval_tokens,
            "generated_per_item_avg": round(total_eval_tokens / processed, 1) if processed else None,
            "decode_seconds_total": round(total_eval_ns / 1e9, 3),
            "overall_tokens_per_sec": round(total_eval_tokens / (total_eval_ns / 1e9), 2)
            if total_eval_ns else None,
        },
        "format_quality": {
            "direct_json": mode_counter["direct"],
            "repaired_json": mode_counter["repaired"],
            "failed": mode_counter["failed"],
            "json_parse_rate": round(parse_ok / processed, 4) if processed else None,
            "zero_cleaning_rate": round(mode_counter["direct"] / processed, 4) if processed else None,
            "schema_pass_rate": round(schema_ok / processed, 4) if processed else None,
            "api_errors": api_errors,
        },
        "graph_quality": analyze_graph(output_path),
        "items": per_item,
    }

    write_json_report(summary, report_path)

    LOG.info("-" * 68)
    LOG.info("完成：处理 %d 条，耗时 %.1f 秒（平均 %.2f 秒/条）",
             processed, total_wall, total_wall / processed if processed else 0)
    LOG.info("生成 token %d，解码 %.1f 秒，整体 %.1f tok/s",
             total_eval_tokens, total_eval_ns / 1e9,
             total_eval_tokens / (total_eval_ns / 1e9) if total_eval_ns else 0)
    LOG.info("JSON 可解析率 %.1f%% | 零污染率 %.1f%% | Schema 合规率 %.1f%%",
             (parse_ok / processed * 100) if processed else 0,
             (mode_counter["direct"] / processed * 100) if processed else 0,
             (schema_ok / processed * 100) if processed else 0)
    gq = summary["graph_quality"]
    closure = gq.get("bidirectional_closure_rate")
    LOG.info("关系质量：上位边 %d 条 | 下位边 %d 条 | 平均下位 %.2f 个 | 双向闭合率 %s",
             gq.get("parent_edges", 0), gq.get("child_edges", 0),
             gq.get("avg_children_per_record", 0),
             f"{closure * 100:.1f}%" if closure is not None else "n/a")
    if gq.get("category_like_parent_count"):
        LOG.warning("其中 %d 条 parent_concept 疑似学科分类名，需人工复核",
                    gq["category_like_parent_count"])
    if gq.get("dangling_parent_refs"):
        LOG.warning("%d 条 parent_concept 指向本批次外概念（属正常，待后续批次补齐）",
                    len(gq["dangling_parent_refs"]))
    LOG.info("输出文件：%s", output_path)
    LOG.info("报告文件：%s", report_path)
    LOG.info("-" * 68)

    return 0 if (processed and schema_ok == processed) else 1


if __name__ == "__main__":
    raise SystemExit(main())
