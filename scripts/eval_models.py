#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OpenSciGraph · 大模型防幻觉自动化评测脚本（v0.1 MVP）

用途
----
把 ``release/v0.1_mvp/OpenSciGraph_Golden_v0.1.json`` 里的 **16 道黄金防幻觉评测题**
（11 道概念辨析 + 5 道幻觉陷阱）喂给任意 OpenAI 兼容 API 的大模型，逐题判定对错，
并把「模型原始输出 + 判定依据 + 汇总准确率」落盘为结构化报告。

设计原则
--------
1. **零硬编码凭据**：API Key 只从环境变量读取（如 ``DEEPSEEK_API_KEY``）。
   本脚本刻意**不提供** ``--api-key`` 命令行参数 —— 避免密钥进入 shell 历史与进程列表。
   报告里只记录「环境变量名 + 密钥长度 + sha256 前 8 位指纹」，绝不记录密钥本身。
2. **确定性**：``temperature=0.0``；逐题串行调用（不做并发），保证同一模型多次运行可比。
3. **判定可追溯**：每道题都记录模型原始回答、解析出的选项、预期选项、判定结论与判定依据文本，
   便于人工复核 —— 本项目的一贯要求是「模型输出必须过独立正确性闸门」。
4. **只上传公开数据**：评测题本身已随 GitHub / HuggingFace 公开发布，
   因此调用第三方 API 时不存在私有语料外泄；脚本**不会**读取或上传任何本地原始语料。
5. **失败不中断**：单题 API 报错会被记录为该题 ``error``（计入 Fail），整轮评测继续跑完。

判定口径（四类，互不混算）
--------------------------
- ``pass``        模型给出的选项 == 预期选项
- ``fail``        模型给出了选项，但与预期不符
- ``unparseable`` 模型输出里找不到 A/B/C/D，无法判定（计入 Fail）
- ``error``       API 调用失败（超时 / 鉴权 / 额度等），未获得有效输出（计入 Fail）

用法
----
    # 1) 先看有哪些内置服务商预设
    python scripts/eval_models.py --list-presets

    # 2) 干跑：只渲染提示词、不发网络请求、不落盘（用来验证环境）
    python scripts/eval_models.py --provider deepseek --dry-run

    # 3) 真跑（PowerShell 环境变量注入，密钥不落盘）
    $env:DEEPSEEK_API_KEY = "你的密钥"
    python scripts/eval_models.py --provider deepseek --model deepseek-chat

    # 4) 本地 Ollama（无需外部密钥，走 127.0.0.1）
    python scripts/eval_models.py --provider ollama --model qwen2.5:7b-instruct-q5_K_M

    # 5) 任意兼容端点
    python scripts/eval_models.py --base-url https://example.com/v1 --model my-model \\
        --api-key-env MY_API_KEY

结果落盘：``reports/eval_<model_name>.json``
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.common import (  # noqa: E402
    PROJECT_ROOT,
    REPORTS_DIR,
    assert_writable,
    load_config,
    relative_to_project,
    setup_logger,
    utc_now_iso,
    write_json_report,
)

# 日志器：与其它脚本同名，输出到 logs/openscigraph.log（UTF-8 追加）
LOG = logging.getLogger("openscigraph")

SCRIPT_NAME = "scripts/eval_models.py"
REPORT_TYPE = "llm_hallucination_eval"

#: 黄金数据包（16 道评测题的唯一来源）
GOLDEN_JSON: Path = PROJECT_ROOT / "release" / "v0.1_mvp" / "OpenSciGraph_Golden_v0.1.json"

#: 目标输出目录（模型名会自动拼进文件名）
OUTPUT_DIR: Path = REPORTS_DIR

# ---------------------------------------------------------------------------
# 服务商预设
# ---------------------------------------------------------------------------
# 全部走 OpenAI 兼容接口（/chat/completions），因此统一用 openai SDK。
# ``api_key_env`` 是**环境变量名**，不是密钥本身。
# ``api_key_optional=True`` 表示本地服务端不校验密钥（如 Ollama），可缺省。

PROVIDER_PRESETS: Dict[str, Dict[str, Any]] = {
    "deepseek": {
        "label": "DeepSeek 官方",
        "base_url": "https://api.deepseek.com/v1",
        "api_key_env": "DEEPSEEK_API_KEY",
        "default_model": "deepseek-chat",
        "json_mode": True,
    },
    "openai": {
        "label": "OpenAI 官方",
        "base_url": "https://api.openai.com/v1",
        "api_key_env": "OPENAI_API_KEY",
        "default_model": "gpt-4o-mini",
        "json_mode": True,
    },
    "qwen": {
        "label": "阿里云百炼（通义千问，compatible-mode）",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "api_key_env": "DASHSCOPE_API_KEY",
        "default_model": "qwen-plus",
        "json_mode": True,
    },
    "siliconflow": {
        "label": "硅基流动 SiliconFlow",
        "base_url": "https://api.siliconflow.cn/v1",
        "api_key_env": "SILICONFLOW_API_KEY",
        "default_model": "Qwen/Qwen2.5-7B-Instruct",
        "json_mode": True,
    },
    "moonshot": {
        "label": "月之暗面 Kimi",
        "base_url": "https://api.moonshot.cn/v1",
        "api_key_env": "MOONSHOT_API_KEY",
        "default_model": "moonshot-v1-8k",
        "json_mode": True,
    },
    "zhipu": {
        "label": "智谱 GLM",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "api_key_env": "ZHIPUAI_API_KEY",
        "default_model": "glm-4-flash",
        "json_mode": True,
    },
    "ollama": {
        "label": "本地 Ollama（离线，走 127.0.0.1:11434）",
        "base_url": "http://127.0.0.1:11434/v1",
        "api_key_env": "OLLAMA_API_KEY",
        "default_model": "qwen2.5:7b-instruct-q5_K_M",
        "json_mode": False,  # Ollama 对 response_format 支持不完整，默认关闭
        "api_key_optional": True,
    },
}

#: 自动识别时的环境变量探测顺序（未显式指定 --provider 时使用）
AUTO_DETECT_ORDER: Tuple[str, ...] = (
    "deepseek",
    "openai",
    "qwen",
    "siliconflow",
    "moonshot",
    "zhipu",
)

# ---------------------------------------------------------------------------
# 提示词
# ---------------------------------------------------------------------------
# 关键：明确告知模型「不要迎合题干中的既有说法」—— 幻觉陷阱题正是靠这一点区分模型
# 是「顺着错误前提往下答」还是「识别并否定错误前提」。

SYSTEM_PROMPT = (
    "你是一位严谨的物理学评测作答者。你会收到一道四选一单选题。\n"
    "请只依据物理事实作答，不要为了迎合题干中的任何既有说法而改变判断；"
    "如果题干里的某个前提本身是错的，请选择能指出该错误前提的选项。\n"
    "输出要求（必须严格遵守）：\n"
    "1. 只输出一个 JSON 对象，不要输出任何解释性文字，不要使用 Markdown 代码块围栏。\n"
    '2. JSON 格式固定为：{"answer": "A", "reason": "不超过 80 字的判定理由"}\n'
    '3. "answer" 的值必须是 A、B、C、D 四个字母之一（大写，不要带选项文字）。'
)

USER_PROMPT_TEMPLATE = (
    "题目：{question}\n\n"
    "选项：\n"
    "A. {opt_a}\n"
    "B. {opt_b}\n"
    "C. {opt_c}\n"
    "D. {opt_d}\n\n"
    "请作答，并按规定 JSON 格式输出。"
)

OPTION_LETTERS: Tuple[str, ...] = ("A", "B", "C", "D")

# ---------------------------------------------------------------------------
# 回答解析
# ---------------------------------------------------------------------------

_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.S)
# 显式 answer / 答案 字段（容忍模型加引号、空格、中文冒号）
_ANSWER_FIELD_RE = re.compile(r'["\']?(?:answer|答案|choice|option)["\']?\s*[:：]\s*["\']?([ABCD])', re.I)
# 兜底：任意「独立出现」的 A/B/C/D。
# 注意不能直接用 \b([ABCD])\b —— 中文属于 \w，导致「选项A」里 A 两侧都不是词边界。
_LOOSE_LETTER_RE = re.compile(r"(?<![A-Za-z])([ABCD])(?![A-Za-z])")

_JSON_KEYS_ANSWER = ("answer", "答案", "choice", "option", "correct_option")
_JSON_KEYS_REASON = ("reason", "理由", "explanation", "解析", "rationale")


def parse_answer(text: Optional[str]) -> Tuple[Optional[str], str, Optional[str]]:
    """
    从模型原文中解析出选项字母与理由。

    返回 ``(选项字母 or None, 解析方式, 理由 or None)``。
    解析优先级：严格 JSON -> 代码块内 JSON -> ``"answer"`` 字段正则 -> 首个独立字母。
    """
    if not text or not text.strip():
        return None, "empty", None

    raw = text.strip()

    # 候选文本：优先剥掉 ``` 围栏
    candidates: List[str] = []
    fence = _FENCE_RE.search(raw)
    if fence:
        candidates.append(fence.group(1).strip())
    candidates.append(raw)

    # 1) 严格 JSON 解析
    for cand in candidates:
        try:
            obj = json.loads(cand)
        except (json.JSONDecodeError, ValueError):
            continue
        if not isinstance(obj, dict):
            continue
        reason = None
        for key in _JSON_KEYS_REASON:
            value = obj.get(key)
            if isinstance(value, str) and value.strip():
                reason = value.strip()
                break
        for key in _JSON_KEYS_ANSWER:
            value = obj.get(key)
            if isinstance(value, str):
                found = re.search(r"([ABCD])", value.upper())
                if found:
                    return found.group(1), f"json:{key}", reason
    if fence:
        # 围栏里不是合法 JSON，但可能仍带 answer 字段
        m = _ANSWER_FIELD_RE.search(fence.group(1))
        if m:
            return m.group(1).upper(), "regex:fenced_answer_field", None

    # 2) 字段正则
    m = _ANSWER_FIELD_RE.search(raw)
    if m:
        return m.group(1).upper(), "regex:answer_field", None

    # 3) 兜底：第一个独立字母
    m = _LOOSE_LETTER_RE.search(raw.upper())
    if m:
        return m.group(1), "regex:first_letter", None

    return None, "unparseable", None


# ---------------------------------------------------------------------------
# 数据加载
# ---------------------------------------------------------------------------


def load_eval_items(path: Path) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """读取黄金包，返回 ``(评测题列表, 数据集元信息)``。"""
    raw_bytes = path.read_bytes()
    payload = json.loads(raw_bytes.decode("utf-8"))

    items = payload.get("eval_items")
    if not isinstance(items, list) or not items:
        raise ValueError(f"{relative_to_project(path)} 中未找到非空 eval_items")

    invalid = [it.get("eval_id") for it in items
               if not isinstance(it.get("options"), list) or len(it.get("options") or []) != 4
               or it.get("correct_option") not in OPTION_LETTERS]
    if invalid:
        raise ValueError(f"以下题目结构不合规（非 4 选项 / 答案键非法）：{invalid}")

    meta = {
        "path": relative_to_project(path),
        "bytes": len(raw_bytes),
        "sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "dataset": payload.get("dataset"),
        "version": payload.get("version"),
        "release": payload.get("release"),
        "schema_version": payload.get("schema_version"),
        "generated_at": payload.get("generated_at"),
        "model_involved": payload.get("model_involved"),
        "counts": payload.get("counts"),
        "license_note": (payload.get("notes") or {}).get("license"),
    }
    return items, meta


def build_prompt(item: Dict[str, Any]) -> List[Dict[str, str]]:
    """把一道评测题渲染成 OpenAI 兼容的 messages。"""
    options = item["options"]
    user = USER_PROMPT_TEMPLATE.format(
        question=item["question"],
        opt_a=options[0], opt_b=options[1], opt_c=options[2], opt_d=options[3],
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]


# ---------------------------------------------------------------------------
# 判定
# ---------------------------------------------------------------------------


def judge(item: Dict[str, Any], model_answer: Optional[str], reason: Optional[str]) -> Tuple[str, str]:
    """
    给出 ``(verdict, judgment_basis)``。

    verdict ∈ {pass, fail, unparseable}；``error`` 由调用方在 API 异常时直接给定。
    """
    expected = item["correct_option"]
    is_trap = item.get("question_type") == "hallucination_trap"

    if model_answer is None:
        basis = (
            f"预期答案={expected}；模型输出中未找到任何合法选项字母，无法判定，按未通过计。"
        )
        if reason:
            basis += f" 模型理由：{reason}"
        return "unparseable", basis

    matched = model_answer == expected
    basis = (
        f"预期答案={expected}；模型给出={model_answer}；"
        f"{'一致，判定通过。' if matched else '不一致，判定不通过。'}"
    )
    if reason:
        basis += f" 模型理由：{reason}"
    else:
        basis += " （模型未给出可解析的理由。）"

    target = item.get("target_hallucination_point")
    if is_trap and target:
        basis += f" 该题针对的幻觉点：{target}"
    return ("pass" if matched else "fail"), basis


# ---------------------------------------------------------------------------
# API 调用
# ---------------------------------------------------------------------------


def mask_key_fingerprint(api_key: Optional[str]) -> Dict[str, Any]:
    """产出密钥的可审计指纹（长度 + sha256 前 8 位），**绝不包含密钥原文**。"""
    if not api_key:
        return {"length": 0, "sha256_8": None}
    digest = hashlib.sha256(api_key.encode("utf-8")).hexdigest()
    return {"length": len(api_key), "sha256_8": digest[:8]}


def resolve_api_key(env_name: str, optional: bool) -> Tuple[Optional[str], str]:
    """
    从环境变量取密钥。

    返回 ``(密钥 or None, 结论说明)``。刻意不提供命令行明文参数。
    """
    value = os.environ.get(env_name)
    if value and value.strip():
        return value.strip(), f"已从环境变量 {env_name} 读取密钥"
    if optional:
        return None, f"未设置 {env_name}（该端点密钥可选，将使用占位符）"
    return None, f"未检测到环境变量 {env_name}"


def call_chat(
    client: Any,
    model: str,
    messages: List[Dict[str, str]],
    temperature: float,
    max_tokens: int,
    timeout: float,
    json_mode: bool,
) -> Tuple[Optional[Any], Optional[str], bool]:
    """
    调用一次 chat.completions。

    返回 ``(响应 or None, 错误信息 or None, json_mode 是否被降级)``。
    若端点不支持 ``response_format``，会自动去掉该参数重试一次。
    """
    kwargs: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "timeout": timeout,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    try:
        return client.chat.completions.create(**kwargs), None, False
    except Exception as exc:  # noqa: BLE001 - SDK 异常类型繁多，统一降级处理
        message = f"{type(exc).__name__}: {exc}"
        if json_mode and ("response_format" in message or "json_object" in message):
            kwargs.pop("response_format", None)
            try:
                return client.chat.completions.create(**kwargs), None, True
            except Exception as exc2:  # noqa: BLE001
                return None, f"{type(exc2).__name__}: {exc2}", False
        return None, message, False


def evaluate_item(
    client: Any,
    item: Dict[str, Any],
    model: str,
    temperature: float,
    max_tokens: int,
    timeout: float,
    retries: int,
    state: Dict[str, Any],
) -> Dict[str, Any]:
    """评测单题，返回结构化结果字典（无论成功失败都返回，绝不抛异常）。"""
    messages = build_prompt(item)
    started = time.perf_counter()
    raw_output: Optional[str] = None
    error: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None
    downgraded = False

    for attempt in range(retries + 1):
        response, err, was_downgraded = call_chat(
            client, model, messages, temperature, max_tokens, timeout, state["json_mode"]
        )
        if was_downgraded:
            downgraded = True
            state["json_mode"] = False
            LOG.warning("端点不支持 response_format=json_object，已自动降级为普通模式")
        if response is not None:
            error = None
            state["json_mode"] = state["json_mode"] and not downgraded
            choice = response.choices[0] if response.choices else None
            raw_output = (choice.message.content if choice and choice.message else None) or ""
            raw_output = (raw_output or "").strip() or None
            break
        error = err
        if attempt < retries:
            backoff = 2 ** attempt
            LOG.warning("第 %d 次调用失败（%s），%d 秒后重试", attempt + 1, err, backoff)
            time.sleep(backoff)

    latency_ms = int((time.perf_counter() - started) * 1000)

    # 抓取 token 用量（不同端点字段名一致，均为 OpenAI 兼容格式）
    try:
        if response is not None and getattr(response, "usage", None) is not None:
            usage = {
                "prompt_tokens": getattr(response.usage, "prompt_tokens", None),
                "completion_tokens": getattr(response.usage, "completion_tokens", None),
                "total_tokens": getattr(response.usage, "total_tokens", None),
            }
    except Exception:  # noqa: BLE001 - 用量缺失不影响评测结论
        usage = None

    if error is not None and raw_output is None:
        verdict = "error"
        basis = f"API 调用失败，未获得有效输出；错误信息：{error}"
        model_answer, parse_method, reason = None, "api_error", None
    else:
        model_answer, parse_method, reason = parse_answer(raw_output)
        verdict, basis = judge(item, model_answer, reason)

    return {
        "eval_id": item.get("eval_id"),
        "concept_id": item.get("concept_id"),
        "question_type": item.get("question_type"),
        "question": item.get("question"),
        "options": item.get("options"),
        "expected_answer": item.get("correct_option"),
        "model_answer": model_answer,
        "verdict": verdict,
        "judgment_basis": basis,
        "answer_parse_method": parse_method,
        "model_raw_output": raw_output,
        "target_hallucination_point": item.get("target_hallucination_point"),
        "reference_explanation": item.get("explanation"),
        "latency_ms": latency_ms,
        "usage": usage,
        "error": error,
    }


# ---------------------------------------------------------------------------
# 汇总与落盘
# ---------------------------------------------------------------------------


def slugify(name: str) -> str:
    """把模型名转成适合做文件名的 slug。"""
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", name or "model").strip("-._")
    return slug or "model"


def summarize(results: List[Dict[str, Any]], duration_s: float) -> Dict[str, Any]:
    """统计总题数 / 通过 / 未通过 / 准确率，并按题型分组。"""
    total = len(results)
    counts = {"pass": 0, "fail": 0, "unparseable": 0, "error": 0}
    by_type: Dict[str, Dict[str, int]] = {}
    total_tokens = 0

    for row in results:
        counts[row["verdict"]] = counts.get(row["verdict"], 0) + 1
        bucket = by_type.setdefault(row["question_type"] or "unknown", {"total": 0, "pass": 0})
        bucket["total"] += 1
        bucket["pass"] += 1 if row["verdict"] == "pass" else 0
        if row.get("usage") and isinstance(row["usage"].get("total_tokens"), int):
            total_tokens += row["usage"]["total_tokens"]

    for bucket in by_type.values():
        bucket["pass_rate_pct"] = round(100.0 * bucket["pass"] / bucket["total"], 2) if bucket["total"] else 0.0

    passed = counts["pass"]
    failed = total - passed
    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate_pct": round(100.0 * passed / total, 2) if total else 0.0,
        "pass_rate": f"{(100.0 * passed / total if total else 0.0):.2f}%",
        "breakdown": {
            "pass": counts["pass"],
            "fail": counts["fail"],
            "unparseable": counts["unparseable"],
            "error": counts["error"],
        },
        "by_question_type": dict(sorted(by_type.items())),
        "total_tokens": total_tokens,
        "duration_s": round(duration_s, 2),
    }


def build_report(
    model_meta: Dict[str, Any],
    dataset_meta: Dict[str, Any],
    results: List[Dict[str, Any]],
    summary: Dict[str, Any],
    args: argparse.Namespace,
    key_note: str,
) -> Dict[str, Any]:
    """组装最终报告（不含任何密钥原文）。"""
    return {
        "report_type": REPORT_TYPE,
        "generated_at": utc_now_iso(),
        "script": SCRIPT_NAME,
        "dataset": dataset_meta,
        "model": model_meta,
        "evaluation_config": {
            "temperature": args.temperature,
            "max_tokens": args.max_tokens,
            "timeout_s": args.timeout,
            "retries": args.retries,
            "json_mode_requested": args.json_mode,
            "provider": args.provider,
            "api_key_env": args.api_key_env,
            "api_key_note": key_note,
            "limit": args.limit,
        },
        "prompt": {"system": SYSTEM_PROMPT, "user_template": USER_PROMPT_TEMPLATE},
        "summary": summary,
        "results": results,
        "notes": [
            "本评测只把 16 道公开黄金评测题发送给模型接口；未上传任何本地原始语料或私有数据。",
            "判定口径：pass=模型选项与答案键一致；fail=不一致；unparseable=输出中无合法选项（计入 Fail）；error=接口失败（计入 Fail）。",
            "temperature=0.0 只能降低随机性，不保证所有服务商都完全确定性；跨模型比较时请固定同一份数据包 sha256。",
            "答案键来自人工逐题验算（见 reports/eval_human_review_stage4.md），是判定基准。",
            "报告内不包含 API Key 原文，仅记录环境变量名与密钥指纹（长度 + sha256 前 8 位）。",
        ],
    }


# ---------------------------------------------------------------------------
# 命令行
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="OpenSciGraph v0.1 MVP · 大模型防幻觉自动化评测（OpenAI 兼容接口，密钥只走环境变量）。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例：\n"
            "  python scripts/eval_models.py --list-presets\n"
            "  python scripts/eval_models.py --provider deepseek --dry-run\n"
            "  $env:DEEPSEEK_API_KEY='xxx'; python scripts/eval_models.py --provider deepseek\n"
        ),
    )
    parser.add_argument("--provider", default=None,
                        choices=sorted(PROVIDER_PRESETS.keys()),
                        help="服务商预设（省略时按环境变量自动识别）")
    parser.add_argument("--model", default=None,
                        help="模型名（省略时取服务商预设的 default_model）")
    parser.add_argument("--base-url", default=None,
                        help="覆盖服务商预设的 API 基址（须含 /v1 之类的兼容路径）")
    parser.add_argument("--api-key-env", default=None,
                        help="覆盖读取密钥的环境变量名（默认取服务商预设）")
    parser.add_argument("--input", default=str(GOLDEN_JSON),
                        help="黄金数据包路径（默认 release/v0.1_mvp/OpenSciGraph_Golden_v0.1.json）")
    parser.add_argument("--output", default=None,
                        help="报告输出路径（默认 reports/eval_<model_name>.json）")
    parser.add_argument("--temperature", type=float, default=0.0,
                        help="采样温度，评测默认 0.0（确定性）")
    parser.add_argument("--max-tokens", type=int, default=512,
                        help="单题最大输出 token 数（默认 512）")
    parser.add_argument("--timeout", type=float, default=60.0,
                        help="单次请求超时秒数（默认 60）")
    parser.add_argument("--retries", type=int, default=2,
                        help="单题失败重试次数（默认 2，指数退避）")
    parser.add_argument("--limit", type=int, default=None,
                        help="只评测前 N 题（调试用；默认全部 16 题）")
    parser.add_argument("--json-mode", dest="json_mode", action="store_true", default=None,
                        help="强制启用 response_format=json_object")
    parser.add_argument("--no-json-mode", dest="json_mode", action="store_false",
                        help="禁用 response_format（部分端点不支持）")
    parser.add_argument("--dry-run", action="store_true",
                        help="只渲染提示词并打印，不调用接口、不落盘")
    parser.add_argument("--list-presets", action="store_true",
                        help="打印内置服务商预设后退出")
    return parser


def print_presets() -> None:
    print("内置服务商预设（全部走 OpenAI 兼容 /chat/completions）")
    print("-" * 96)
    print(f"{'provider':<12} {'key 环境变量':<22} {'默认模型':<32} {'base_url'}")
    print("-" * 96)
    for name, cfg in sorted(PROVIDER_PRESETS.items()):
        print(f"{name:<12} {cfg['api_key_env']:<22} {cfg['default_model']:<32} {cfg['base_url']}")
    print("-" * 96)
    print("密钥仅从环境变量读取，本脚本不提供 --api-key 参数（避免密钥进入 shell 历史）。")


def auto_detect_provider() -> Optional[str]:
    """按预设顺序探测环境变量，返回第一个命中的服务商名。"""
    for name in AUTO_DETECT_ORDER:
        env_name = PROVIDER_PRESETS[name]["api_key_env"]
        if os.environ.get(env_name, "").strip():
            return name
    return None


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_presets:
        print_presets()
        return 0

    config = load_config()
    setup_logger("openscigraph", level=config.get("logging", {}).get("level"))

    # ---- 1. 解析服务商与模型 ----
    provider = args.provider
    if provider is None:
        provider = auto_detect_provider()
        if provider:
            LOG.info("未指定 --provider，按环境变量自动识别为：%s", provider)
    if provider is None:
        provider = "openai"  # 仅用于取默认模型名，缺密钥会在下面被拦下

    preset = PROVIDER_PRESETS[provider]
    model = args.model or preset["default_model"]
    base_url = args.base_url or preset["base_url"]
    api_key_env = args.api_key_env or preset["api_key_env"]
    json_mode_default = preset.get("json_mode", True)
    if args.json_mode is None:
        args.json_mode = json_mode_default
    args.provider = provider
    args.api_key_env = api_key_env

    # ---- 2. 读取黄金包 ----
    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = (PROJECT_ROOT / input_path).resolve()
    if not input_path.exists():
        LOG.error("找不到黄金数据包：%s", input_path)
        return 2

    items, dataset_meta = load_eval_items(input_path)
    if args.limit is not None:
        items = items[: max(args.limit, 0)]
    LOG.info("数据集：%s（%d 道题，sha256=%s…）",
             dataset_meta["path"], len(items), (dataset_meta["sha256"] or "")[:16])

    # ---- 3. 干跑：只渲染提示词 ----
    if args.dry_run:
        LOG.info("--dry-run：不调用接口、不落盘")
        print("=" * 78)
        print(f"服务商      : {provider}（{preset['label']}）")
        print(f"模型        : {model}")
        print(f"base_url    : {base_url}")
        print(f"密钥环境变量: {api_key_env}")
        print(f"temperature : {args.temperature}")
        print(f"题目数      : {len(items)}")
        print("=" * 78)
        for item in items[:2]:
            messages = build_prompt(item)
            print(f"\n--- {item['eval_id']} · {item['question_type']} ---")
            print(f"[system] {messages[0]['content']}")
            print(f"[user]\n{messages[1]['content']}")
        if len(items) > 2:
            print(f"\n（其余 {len(items) - 2} 道略）")
        return 0

    # ---- 4. 解析密钥（只走环境变量）----
    optional = bool(preset.get("api_key_optional"))
    api_key, key_note = resolve_api_key(api_key_env, optional)
    if api_key is None and not optional:
        LOG.error(
            "未检测到 %s 环境变量，请在 PowerShell 中执行 $env:%s=\"your_key\" 后重试。",
            api_key_env, api_key_env,
        )
        LOG.error("本脚本不接受命令行明文密钥（避免进入 shell 历史）。")
        return 3
    if api_key is None:
        api_key = "ollama-local-no-key"  # 本地端点不校验，SDK 仍要求非空
    LOG.info("%s（%s）", key_note, mask_key_fingerprint(api_key))

    # ---- 5. 初始化客户端 ----
    try:
        from openai import OpenAI
    except ImportError:
        LOG.error("未安装 openai SDK。请执行：python -m pip install \"openai>=1.40\"")
        return 4

    client = OpenAI(api_key=api_key, base_url=base_url)

    # ---- 6. 逐题评测 ----
    LOG.info("开始评测：模型=%s，题目数=%d，temperature=%s", model, len(items), args.temperature)
    state: Dict[str, Any] = {"json_mode": bool(args.json_mode)}
    started = time.perf_counter()
    results: List[Dict[str, Any]] = []

    for index, item in enumerate(items, start=1):
        row = evaluate_item(
            client, item, model, args.temperature, args.max_tokens,
            args.timeout, args.retries, state,
        )
        results.append(row)
        mark = {"pass": "PASS", "fail": "FAIL", "unparseable": "UNPARSED", "error": "ERROR"}[row["verdict"]]
        LOG.info(
            "[%2d/%d] %-11s %-10s 预期=%s 模型=%s (%d ms)",
            index, len(items), row["eval_id"], mark,
            row["expected_answer"], row["model_answer"] or "-", row["latency_ms"],
        )

    duration = time.perf_counter() - started
    summary = summarize(results, duration)

    # ---- 7. 组装并落盘 ----
    model_meta = {
        "model": model,
        "provider": provider,
        "provider_label": preset["label"],
        "base_url": base_url,
        "api_key_env": api_key_env,
        "api_key_fingerprint": mask_key_fingerprint(api_key),
        "temperature": args.temperature,
    }
    report = build_report(model_meta, dataset_meta, results, summary, args, key_note)

    output_path = (
        Path(args.output) if args.output
        else OUTPUT_DIR / f"eval_{slugify(model)}.json"
    )
    if not output_path.is_absolute():
        output_path = (PROJECT_ROOT / output_path).resolve()
    assert_writable(output_path)  # 遵守项目写入保护（禁止写 data/raw）
    write_json_report(report, output_path)

    # ---- 8. 控制台摘要 ----
    print("=" * 78)
    print(f"模型            : {model}（{provider}）")
    print(f"数据集 sha256   : {(dataset_meta['sha256'] or '')[:16]}…")
    print(f"总题数          : {summary['total']}")
    print(f"通过 (Pass)     : {summary['passed']}")
    print(f"未通过 (Fail)   : {summary['failed']}")
    print(f"准确率          : {summary['pass_rate']}")
    print(f"细分            : pass={summary['breakdown']['pass']} / fail={summary['breakdown']['fail']} "
          f"/ unparseable={summary['breakdown']['unparseable']} / error={summary['breakdown']['error']}")
    for qtype, bucket in summary["by_question_type"].items():
        print(f"  · {qtype:<20} {bucket['pass']}/{bucket['total']}  ({bucket['pass_rate_pct']}%)")
    print(f"耗时 / tokens   : {summary['duration_s']} s / {summary['total_tokens']}")
    print("=" * 78)
    LOG.info("报告已写入：%s", relative_to_project(output_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
