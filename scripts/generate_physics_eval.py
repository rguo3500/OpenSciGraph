# -*- coding: utf-8 -*-
"""
OpenSciGraph 阶段三 —— 基础物理 AI 评测数据集（Benchmark）衍生（本地离线）

读取阶段二产出的 100 条高精概念数据，用本地 qwen2.5:7b-instruct-q5_K_M
按 2:2:1 比例衍生 50 道四选一评测题：

    concept_distinction  概念辨析题      20 题
    formula_reasoning    公式应用与量纲题 20 题
    hallucination_trap   AI 幻觉陷阱题    10 题

设计要点
--------
1. **全程离线**：只访问 http://127.0.0.1:11434/api/chat，脚本内显式禁用代理，
   不存在走 HTTP(S)_PROXY 出网的可能。
2. **原始数据只读**：只读 data/processed/physics_concepts_v2.jsonl，绝不写入。
   输出统一走 src.common.assert_writable()，data/raw 依旧不可写。
3. **标识字段不由模型决定**：eval_id / concept_id / question_type 由脚本的
   确定性蓝图给出，模型输出会被覆盖，防止 ID 漂移与题型串位。
4. **出题蓝图是确定性的**：三类题的锚定概念、对比概念、错误前提都写死在
   TRAP_SPECS / FORMULA_SPECS / DISTINCTION_SPECS 中，模型只负责组织题干、
   选项、答案与解析。这样 50 道题的覆盖面可控、可复现。
5. **结构强约束**：请求体带 "format": "json" 做语法约束采样；
   脚本再做一层结构校验（恰好 4 个选项、互不重复、答案落在 A-D、
   解析长度达标等），不达标自动重掷，最多 --max-retry 次。
6. **盲测自洽校验**：出题完成后，把题目单独喂回模型（不给答案），
   让它盲答一次，与答案键比对。这是质量信号，不是正确率保证——
   幻觉陷阱题**期望**模型答错，那正是该题的测出能力所在。

用法（在 E:\\OpenSciGraph 下）
------------------------------
    .\\.venv\\Scripts\\python.exe scripts\\generate_physics_eval.py
    .\\.venv\\Scripts\\python.exe scripts\\generate_physics_eval.py --limit-per-type 1   # 冒烟测试
    .\\.venv\\Scripts\\python.exe scripts\\generate_physics_eval.py --no-verify           # 跳过盲测
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
import time
import urllib.error
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

# ---------------------------------------------------------------------------
# 复用基础设施
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(PROJECT_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from src.common import (  # noqa: E402
    CONFIG_DIR,
    INTERIM_DIR,
    PROCESSED_DIR,
    REPORTS_DIR,
    assert_writable,
    relative_to_project,
    setup_logger,
    timestamp_slug,
    utc_now_iso,
    write_json_report,
)

# Ollama 调用与 JSON 抽取逻辑复用阶段二脚本，避免两套实现漂移
from clean_physics_v2 import (  # noqa: E402
    extract_json,
    make_localhost_opener,
)
from clean_physics_v2 import call_ollama as _ollama_chat  # noqa: E402

LOG = setup_logger("physics_eval_v1")

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

SCHEMA_FILE = CONFIG_DIR / "physics_eval_schema.json"
DEFAULT_CONCEPTS = PROCESSED_DIR / "physics_concepts_v2.jsonl"
DEFAULT_OUTPUT = PROCESSED_DIR / "physics_eval_v1.jsonl"
DEFAULT_RAW_OUTPUT = INTERIM_DIR / "physics_eval_v1_modelraw.jsonl"

DEFAULT_API = "http://127.0.0.1:11434/api/chat"
DEFAULT_MODEL = "qwen2.5:7b-instruct-q5_K_M"

#: 评测记录字段顺序（与 config/physics_eval_schema.json 保持一致）
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

#: 模型负责的内容字段（其余字段由脚本注入）
MODEL_KEYS: Tuple[str, ...] = (
    "question",
    "options",
    "correct_option",
    "explanation",
    "target_hallucination_point",
)

OPTION_LETTERS: Tuple[str, ...] = ("A", "B", "C", "D")

#: 结构校验阈值
QUESTION_MIN_LEN = 8
EXPLANATION_MIN_LEN = 20
TARGET_MIN_LEN = 4
OPTION_MIN_LEN = 2

#: 幻觉陷阱题的「否定性」词汇（用于软校验正确答案是否真的否定了错误前提）
NEGATION_MARKERS: Tuple[str, ...] = (
    "不是", "不属于", "并非", "错误", "不成立", "无关", "混淆", "不能", "不应",
    "不是一种", "不属于同一", "两回事", "不同", "区别",
)


# ---------------------------------------------------------------------------
# 出题蓝图（确定性；模型只负责把蓝图书写成题目）
# ---------------------------------------------------------------------------
# 幻觉陷阱题：错误前提直接取自阶段二 graph_quality 实测到的模型易错边。
# 每条形如 (concept_id, 中文名, 错误前提, 命题方向)
TRAP_SPECS: Tuple[Tuple[str, str, str, str], ...] = (
    ("P005", "动量", "动量属于能量，是能量的一种形式。",
     "正确答案必须明确指出动量与能量是相互独立的物理量（动量是矢量、能量是标量），该错误前提不成立。"),
    ("P008", "功率", "功率是一种能量。",
     "正确答案必须指出功率是描述能量转化快慢的物理量，不是能量本身。"),
    ("P059", "温度", "温度是一种能量。",
     "正确答案必须指出温度是描述分子平均动能的强度量，不是能量的形式。"),
    ("P066", "熵", "熵是热力学第二定律的一个下位概念。",
     "正确答案必须指出熵是一个状态函数，热力学第二定律是描述熵增的规律，二者不是种属关系。"),
    ("P010", "加速度", "加速度是运动学的一个分支学科。",
     "正确答案必须指出加速度是一个物理量（概念），而运动学是学科分类，二者不是种属关系。"),
    ("P080", "电阻", "欧姆是电阻的一个下位概念。",
     "正确答案必须指出欧姆是电阻的单位（或人名），不是电阻的下位概念。"),
    ("P004", "万有引力定律", "万有引力定律是一种力。",
     "正确答案必须指出万有引力定律是一条物理定律（规律），力是一个物理量，二者类别不同。"),
    ("P078", "电容", "电容是电学的一个分支学科。",
     "正确答案必须指出电容是一个描述储电能力的物理量，电学是学科分类，二者不是种属关系。"),
    ("P098", "波粒二象性", "光电效应是波粒二象性的下位概念。",
     "正确答案必须指出光电效应是支持波粒二象性的实验现象（证据），不是它的下位概念。"),
    ("P099", "质能等价", "核反应是质能等价的下位概念。",
     "正确答案必须指出核反应是质能关系的一种应用实例，不是质能等价的下位概念。"),
)

# 公式应用与量纲题：(concept_id, 中文名, 考点)
FORMULA_SPECS: Tuple[Tuple[str, str, str], ...] = (
    ("P002", "牛顿第二运动定律", "F = ma 中加速度与合外力、质量的正反比关系，以及力的量纲/单位"),
    ("P007", "功", "W = Fd cosθ 中 cosθ 的物理含义，以及功的量纲与正负功判断"),
    ("P025", "动能", "Ek = ½mv² 中速度取平方带来的非线性，以及动能与速率的关系"),
    ("P029", "胡克定律", "F = -kx 中负号的含义、劲度系数 k 的物理意义与单位"),
    ("P035", "力", "力的国际单位与量纲（1 N = 1 kg·m/s²）"),
    ("P068", "理想气体状态方程", "PV = nRT 中各量成比例还是成反比，以及等温/等压过程的表现"),
    ("P074", "库仑定律", "F = k|q1q2|/r² 的平方反比关系与电量乘积关系"),
    ("P081", "欧姆定律", "I = U/R 的因果关系与串并联电路中电流电压的分配"),
    ("P082", "电功率", "P = IV 与 P = I²R 的等价推导与适用条件"),
    ("P019", "力矩", "M = FL 中力臂的定义与力矩的单位"),
    ("P053", "压强", "p = F/S 中受力面积的作用，以及 1 Pa 与常用单位的换算"),
    ("P056", "浮力", "F = ρgV 中排开液体体积与浮力的关系，及漂浮与沉底的区别"),
    ("P018", "角速度", "ω = Δθ/Δt 与线速度 v = ωr 的关系"),
    ("P021", "角动量", "L = Iω 的构成与角动量守恒的成立条件"),
    ("P043", "周期", "T = 1/f 与周期的单位，以及周期与频率的倒数关系"),
    ("P046", "波速", "v = λf 中波速由介质决定，频率改变时波长如何变化"),
    ("P061", "比热容", "Q = cmΔT 中比热容的物理意义与吸放热计算"),
    ("P076", "电势", "U = W/q 的定义与电势、电势能的区别"),
    ("P089", "光的折射", "折射率 n = sin i / sin r 与光在介质中速度的关系"),
    ("P095", "电磁波", "c = λf 中真空中波速为常量，波长与频率的反比关系"),
)

# 概念辨析题：(concept_id, 中文名, 对比概念, 辨析焦点)
DISTINCTION_SPECS: Tuple[Tuple[str, str, str, str], ...] = (
    ("P012", "速度", "P010 加速度", "速度描述位置变化快慢，加速度描述速度变化快慢，二者是不同的物理量"),
    ("P031", "静摩擦力", "P032 滑动摩擦力", "静摩擦力随外力变化且有最大值，滑动摩擦力近似恒定"),
    ("P049", "波的干涉", "P050 波的衍射", "干涉是两列波叠加形成稳定加强减弱，衍射是波绕过障碍物传播"),
    ("P088", "光的反射", "P089 光的折射", "反射是光返回原介质，折射是光进入另一介质并改变传播方向"),
    ("P060", "热量", "P067 内能", "热量是热传递过程中转移的能量（过程量），内能是物体内部能量总和（状态量）"),
    ("P026", "势能", "P027 重力势能 / P028 弹性势能", "势能是统称，重力势能与弹性势能是它的两种具体形式"),
    ("P075", "电场", "P076 电势", "电场是力的性质（矢量，描述受力），电势是能的性质（标量，描述做功）"),
    ("P073", "电荷", "P079 电流", "电荷是物质属性（量），电流是电荷定向移动的速率"),
    ("P044", "频率", "P043 周期", "频率是单位时间完成的次数，周期是完成一次所需时间，二者互为倒数"),
    ("P045", "波长", "P046 波速", "波长是相邻同相点距离，波速是波传播的快慢，二者量纲不同"),
    ("P063", "热力学第一定律", "P064 热力学第二定律", "第一定律是能量守恒，第二定律说明过程的方向性与熵增"),
    ("P096", "光电效应", "P097 光子", "光子是光的量子（粒子），光电效应是光子打出电子的现象"),
    ("P084", "洛伦兹力", "P085 安培力", "洛伦兹力作用于单个运动电荷，安培力是通电导体受到的宏观合力"),
    ("P037", "惯性", "P020 转动惯量", "惯性是保持运动状态的性质（取决于质量），转动惯量描述转动惯性大小"),
    ("P033", "弹力", "P030 摩擦力", "弹力由形变产生且垂直于接触面，摩擦力由接触面粗糙及相对运动趋势产生且沿切向"),
    ("P006", "能量", "P025 动能", "能量是统称，动能是能量的一种具体形式"),
    ("P051", "驻波", "P052 共振", "驻波是两列反向传播波叠加形成的稳定波形，共振是驱动频率接近固有频率时振幅剧增的现象"),
    ("P093", "光的偏振", "P092 光的衍射", "偏振说明光是横波，衍射说明波能绕过障碍物，二者是不同性质的波动现象"),
    ("P070", "热传导", "P071 热对流 / P072 热辐射", "热传导靠分子碰撞、热对流靠流体流动、热辐射靠电磁波，三种传热方式机理不同"),
    ("P086", "法拉第电磁感应定律", "P087 楞次定律", "法拉第定律给出感应电动势大小，楞次定律给出感应电流方向"),
)


# ---------------------------------------------------------------------------
# Prompt 构造
# ---------------------------------------------------------------------------

_JSON_OUTPUT_SPEC = """【输出格式】只输出一个 JSON 对象，且只能是一个 JSON 对象。
不要输出 Markdown 代码围栏，不要输出任何解释性文字，不要输出注释。
键名与结构必须严格如下（options 数组恰好 4 项，按 A/B/C/D 顺序）：
{
  "question": "题干，简体中文，完整自洽",
  "options": ["第一个选项内容", "第二个选项内容", "第三个选项内容", "第四个选项内容"],
  "correct_option": "A",
  "explanation": "解析，说明正确选项为何成立，并指出主要干扰项的错因，40 到 150 字",
  "target_hallucination_point": "本题针对的模型盲点，一句话"
}
注意：options 里只写选项内容本身，不要再写 "A." "B." 这类字母前缀。"""


def _concept_brief(record: Dict[str, Any]) -> str:
    """把一条阶段二记录压缩成可供出题参考的简要材料。"""
    parts = [f"{record.get('concept_id')} {record.get('name_zh')}（{record.get('name_en') or '—'}）"]
    if record.get("definition_zh"):
        parts.append(f"  定义：{record['definition_zh']}")
    if record.get("formula"):
        parts.append(f"  公式：{record['formula']}")
    if record.get("parent_concept"):
        parts.append(f"  上位概念：{record['parent_concept']}")
    if record.get("child_concepts"):
        parts.append(f"  下位概念：{'、'.join(record['child_concepts'])}")
    return "\n".join(parts)


def build_prompt(
    kind: str, spec: Dict[str, Any], records: Dict[str, Dict[str, Any]], extra: str = ""
) -> str:
    """按题型构造出题 prompt。标识字段由脚本给出，模型只写内容字段。"""
    if kind == "concept_distinction":
        main = records[spec["concept_id"]]
        other = records[spec["counterpart_id"]]
        return (
            "你是一位物理教学评测命题专家。请命制 1 道**概念辨析**四选一单选题。\n\n"
            f"【锚定概念】\n{_concept_brief(main)}\n\n"
            f"【对比概念】\n{_concept_brief(other)}\n\n"
            f"【本题必须考到的辨析焦点】{spec['focus']}\n\n"
            "【出题要求】\n"
            "1. 题干要让学生判断两个概念的差别、各自含义或适用条件，不能直接问「哪个是定义」。\n"
            "2. 四个选项必须是同一维度上看起来都合理的物理表述，干扰项要命中真实的混淆点，"
            "不得出现明显荒谬或与题干无关的凑数项。\n"
            "3. 只能有一个选项在物理学上完全正确，其余三个必须确实错误——"
            "不允许出现两个选项都对、或某个选项表述本身成立但不回答题干的情况。\n"
            "4. 解析要说明正确选项为何成立，并指出最主要干扰项的错因。\n\n"
            + extra + _JSON_OUTPUT_SPEC
        )

    if kind == "formula_reasoning":
        main = records[spec["concept_id"]]
        return (
            "你是一位物理教学评测命题专家。请命制 1 道**公式应用与量纲**四选一单选题。\n\n"
            f"【锚定概念】\n{_concept_brief(main)}\n\n"
            f"【本题必须考到的考点】{spec['focus']}\n\n"
            "【出题要求】\n"
            "1. 题目必须涉及具体公式或物理量之间的定量关系（正比、反比、平方关系、单位换算等），"
            "不能只考名词解释。\n"
            "2. **题干若给出数值，必须给全解题所需的全部已知量**，不能要求解答者自行假定缺失的量；"
            "确实需要时，请在题干里明确写出该前提。\n"
            "3. 干扰项要体现典型错误：公式记错、正比反比搞反、量纲/单位不匹配、混淆两个相近物理量。\n"
            "4. 只能有一个选项在物理学上完全正确。\n"
            "5. 解析必须写出用到的公式，逐步代入数值，并说明干扰项错在哪里；"
            "**解析最后算出的结果必须与你选定的正确选项完全一致**。\n\n"
            + extra + _JSON_OUTPUT_SPEC
        )

    if kind == "hallucination_trap":
        main = records[spec["concept_id"]]
        return (
            "你是一位专门探测大模型物理知识盲点的评测命题专家。"
            "请命制 1 道**幻觉陷阱**四选一单选题。\n\n"
            f"【锚定概念】\n{_concept_brief(main)}\n\n"
            f"【植入题干附近的错误前提（这是大模型真实犯过的错）】{spec['wrong_premise']}\n\n"
            f"【正确答案的硬性方向】{spec['direction']}\n\n"
            "【出题要求】\n"
            "1. 题干必须以自然的、像教科书复习题的方式把这个错误前提引入（"
            "例如让某位同学提出该说法，请你判断；或问「关于 X 与 Y 的关系，下列说法正确的是」）。"
            "诱导要隐蔽，不要一看就知道是错的。\n"
            "2. **三个干扰项必须顺从该错误前提**，写成看似合理、容易被语言模型接受的表述；\n"
            "   唯一正确的那个选项必须明确否定该错误前提，指出二者类别不同或关系不成立。\n"
            "3. 三个干扰项必须各自确实是错的，**不得出现某个干扰项换个措辞后本身也成立**的情况"
            "（例如错误前提是「A 是 B 的学科分支」，干扰项就不能写成「A 属于 B 中的一个概念」——"
            "后者其实是对的）。\n"
            "4. 解析要明确指出该错误前提错在哪里，以及为什么会构成常见误判。\n"
            "5. target_hallucination_point 要写清楚本题针对的盲点类型"
            "（如：把相关关系误判为种属关系、混淆概念与学科分类、把单位当概念）。\n\n"
            + extra + _JSON_OUTPUT_SPEC
        )

    raise ValueError(f"未知题型：{kind}")


#: 重制缺陷题时追加的自查指令（--repair / --strict 使用）
STRICT_SELFCHECK = (
    "【严格自查要求】上一轮生成的题目存在自相矛盾或条件不足的问题，本次必须避免：\n"
    "1. 若题干给出数值，先逐一列出已知量，确认足以求解；不足时补充明确前提或改成定性判断题。\n"
    "2. 逐步计算，把每一步的数值写进解析。\n"
    "3. **解析中最后得出的结果必须与你选定的正确选项完全一致**，"
    "不得出现解析算出 9J、却把 18J 选为正确答案这类矛盾。\n"
    "4. 逐项复核四个选项：确认只有一个是物理上正确的，"
    "另外三个必须确实错误（不能只是表述不同但同样成立）。\n\n"
)


def build_verify_prompt(record: Dict[str, Any]) -> str:
    """盲测 prompt：只给题干与选项，让模型独立作答。"""
    lines = ["以下是一道四选一物理单选题，请独立作答。", "", f"题目：{record['question']}", ""]
    for letter, text in zip(OPTION_LETTERS, record["options"]):
        lines.append(f"{letter}. {text}")
    lines += [
        "",
        "只输出一个 JSON 对象，格式为：{\"answer\": \"A\"}",
        "answer 的值只能是 A、B、C、D 之一。不要输出任何其他内容。",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 结果清洗与校验
# ---------------------------------------------------------------------------

_OPTION_PREFIX_RE = re.compile(r"^\s*(?:选项)?\s*[A-DＡ-Ｄ]\s*[.、．:：)）]\s*")


def strip_option_prefix(text: str) -> str:
    """去掉模型可能自行加上的 'A.' / 'B、' 之类前缀，保证 options 只含内容。"""
    cleaned = text.strip()
    for _ in range(2):  # 容忍 'A. A. xxx' 这种重复前缀
        new = _OPTION_PREFIX_RE.sub("", cleaned).strip()
        if new == cleaned:
            break
        cleaned = new
    return cleaned


def validate_eval_record(obj: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """
    校验并规范化模型输出。返回 (规范化后的内容字段 dict, 告警列表)。

    致命问题（选项数量不对、答案不在 A-D 等）会在调用方触发重掷。
    """
    issues: List[str] = []

    question = str(obj.get("question") or "").strip()
    if len(question) < QUESTION_MIN_LEN:
        issues.append("FATAL:question 过短或缺失")

    raw_options = obj.get("options")
    options: List[str] = []
    if isinstance(raw_options, list):
        for item in raw_options:
            if isinstance(item, str):
                cleaned = strip_option_prefix(item)
                if cleaned:
                    options.append(cleaned)
    if len(options) != 4:
        issues.append(f"FATAL:options 必须恰好 4 项，实际 {len(options)}")

    if any(len(o) < OPTION_MIN_LEN for o in options):
        issues.append("FATAL:存在过短的选项")

    if len(set(options)) != len(options):
        issues.append("FATAL:选项内容重复")

    if any(re.search(r"以上(都|均|全)?(对|正确|错|不正确|不对)", o) for o in options):
        issues.append("WARN:出现「以上都对/都不对」类元选项")

    # correct_option：容忍三种写法 —— 纯字母「A」、带前缀「A.」、以及误把选项原文当答案
    raw_correct = str(obj.get("correct_option") or "").strip()
    upper = raw_correct.upper()
    correct = ""
    letter_match = re.match(r"^\s*(?:选项)?\s*([A-D])\s*(?:[.、．:：)）]|$|\s)", upper)
    if letter_match:
        correct = letter_match.group(1)
    if not correct and options:
        probe = strip_option_prefix(raw_correct)
        if probe:
            for letter, opt in zip(OPTION_LETTERS, options):
                if probe == opt:
                    correct = letter
                    break
    if correct not in OPTION_LETTERS:
        issues.append(f"FATAL:correct_option 非法（{raw_correct!r}）")

    explanation = str(obj.get("explanation") or "").strip()
    if len(explanation) < EXPLANATION_MIN_LEN:
        issues.append("WARN:explanation 过短")

    target = str(obj.get("target_hallucination_point") or "").strip()
    if len(target) < TARGET_MIN_LEN:
        issues.append("WARN:target_hallucination_point 过短")

    normalized = {
        "question": question,
        "options": options,
        "correct_option": correct,
        "explanation": explanation,
        "target_hallucination_point": target,
    }
    return normalized, issues


def is_fatal(issues: Sequence[str]) -> bool:
    return any(i.startswith("FATAL:") for i in issues)


# ---------------------------------------------------------------------------
# 单题生成
# ---------------------------------------------------------------------------

def generate_one(
    *,
    opener: Any,
    api_url: str,
    model: str,
    kind: str,
    spec: Dict[str, Any],
    records: Dict[str, Dict[str, Any]],
    max_retry: int,
    temperature: float,
    num_predict: int,
    timeout: int,
    extra: str = "",
) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    生成一道题。返回 (规范化内容字段 or None, 每次尝试的审计记录列表)。
    """
    attempts: List[Dict[str, Any]] = []
    for attempt in range(1, max_retry + 1):
        prompt = build_prompt(kind, spec, records, extra=extra)
        if attempt > 1:
            prompt += (
                "\n\n【上次输出不合格的原因】"
                + "；".join(attempts[-1]["issues"])
                + "\n请严格修正后重新输出。"
            )
        t0 = time.perf_counter()
        try:
            response = _ollama_chat(
                opener=opener,
                api_url=api_url,
                model=model,
                prompt=prompt,
                timeout=timeout,
                temperature=temperature,
                use_json_format=True,
                num_predict=num_predict,
            )
        except (urllib.error.URLError, json.JSONDecodeError, Exception) as exc:  # noqa: BLE001
            attempts.append({
                "attempt": attempt, "status": "api_error",
                "error": f"{type(exc).__name__}: {exc}",
                "wall_s": round(time.perf_counter() - t0, 3),
            })
            continue

        elapsed = time.perf_counter() - t0
        content = (response.get("message") or {}).get("content", "")
        obj, parse_mode, parse_error = extract_json(content)

        if obj is None:
            attempts.append({
                "attempt": attempt, "status": "parse_failed", "parse_mode": parse_mode,
                "parse_error": parse_error, "raw_content": content,
                "wall_s": round(elapsed, 3),
                "eval_count": response.get("eval_count"),
                "eval_duration_ns": response.get("eval_duration"),
            })
            continue

        normalized, issues = validate_eval_record(obj)
        attempts.append({
            "attempt": attempt, "status": "ok" if not is_fatal(issues) else "invalid",
            "parse_mode": parse_mode, "issues": issues, "raw_content": content,
            "normalized": normalized, "wall_s": round(elapsed, 3),
            "eval_count": response.get("eval_count"),
            "eval_duration_ns": response.get("eval_duration"),
            "prompt_eval_count": response.get("prompt_eval_count"),
        })
        if not is_fatal(issues):
            return normalized, attempts

    return None, attempts


def blind_verify(
    *,
    opener: Any,
    api_url: str,
    model: str,
    record: Dict[str, Any],
    temperature: float,
    num_predict: int,
    timeout: int,
) -> Dict[str, Any]:
    """把题面单独喂回模型盲答，返回其答案与是否与答案键一致。"""
    t0 = time.perf_counter()
    try:
        response = _ollama_chat(
            opener=opener, api_url=api_url, model=model,
            prompt=build_verify_prompt(record), timeout=timeout,
            temperature=0.0, use_json_format=True, num_predict=32,
        )
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}",
                "wall_s": round(time.perf_counter() - t0, 3)}

    content = (response.get("message") or {}).get("content", "")
    obj, _, _ = extract_json(content)
    answer = None
    if isinstance(obj, dict):
        cand = str(obj.get("answer") or "").strip().upper()
        answer = cand[0] if cand[:1] in OPTION_LETTERS else None
    return {
        "ok": answer is not None,
        "model_answer": answer,
        "matches_key": answer == record["correct_option"],
        "raw_content": content,
        "wall_s": round(time.perf_counter() - t0, 3),
        "eval_count": response.get("eval_count"),
    }


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

def build_blueprint(limit_per_type: int = 0) -> List[Tuple[str, Dict[str, Any]]]:
    """把三类蓝图展开成待生成任务列表（题型, spec）。"""
    tasks: List[Tuple[str, Dict[str, Any]]] = []

    for cid, name, premise, direction in TRAP_SPECS:
        tasks.append(("hallucination_trap", {
            "concept_id": cid, "name_zh": name,
            "wrong_premise": premise, "direction": direction,
        }))
    for cid, name, focus in FORMULA_SPECS:
        tasks.append(("formula_reasoning", {
            "concept_id": cid, "name_zh": name, "focus": focus,
        }))
    for cid, name, other, focus in DISTINCTION_SPECS:
        tasks.append(("concept_distinction", {
            "concept_id": cid, "name_zh": name,
            "counterpart_id": other.split(" ")[0], "counterpart": other, "focus": focus,
        }))

    if limit_per_type > 0:
        trimmed: List[Tuple[str, Dict[str, Any]]] = []
        for kind in ("hallucination_trap", "formula_reasoning", "concept_distinction"):
            trimmed.extend([t for t in tasks if t[0] == kind][:limit_per_type])
        tasks = trimmed

    # 按题型顺序输出：概念辨析 → 公式 → 幻觉陷阱（报告里读起来更自然）
    order = {"concept_distinction": 0, "formula_reasoning": 1, "hallucination_trap": 2}
    tasks.sort(key=lambda t: order[t[0]])
    return tasks


def load_records(path: Path) -> Dict[str, Dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"阶段二产出不存在：{path}")
    records: Dict[str, Dict[str, Any]] = {}
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            records[obj["concept_id"]] = obj
    return records


def run_repair(
    args: argparse.Namespace,
    records: Dict[str, Dict[str, Any]],
    output_path: Path,
    raw_path: Path,
    report_path: Path,
) -> int:
    """
    修复模式：对已有评测集逐题重新盲测，凡未通过自洽校验的题用严格自查 prompt 重制。

    判定原则：重制后的题必须**同时**通过结构校验与盲测自洽，才替换原题；
    否则保留原题并记入人工复核清单——不拿「换个说法但依然错」的题去充数。
    """
    if not output_path.exists():
        LOG.error("--repair 需要已存在的输出文件：%s", output_path)
        return 2

    existing: List[Dict[str, Any]] = [
        json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    blueprint = {spec["concept_id"]: (kind, spec) for kind, spec in build_blueprint(0)}
    opener = make_localhost_opener()

    LOG.info("=" * 68)
    LOG.info("阶段三 · 缺陷题重制（离线）")
    LOG.info("模型      : %s", args.model)
    LOG.info("待复核    : %d 题", len(existing))
    LOG.info("=" * 68)

    run_start = time.perf_counter()
    audit: List[Dict[str, Any]] = []
    before: Dict[str, bool] = {}
    need_fix: List[str] = []

    LOG.info("---- 第一轮：对全部题目重新盲测 ----")
    for rec in existing:
        v = blind_verify(opener=opener, api_url=args.api_url, model=args.model,
                         record=rec, temperature=0.0, num_predict=32, timeout=args.timeout)
        audit.append({"eval_id": rec["eval_id"], "phase": "before", **v})
        before[rec["eval_id"]] = bool(v.get("matches_key"))
        if not v.get("matches_key"):
            need_fix.append(rec["concept_id"])
        LOG.info("  %s %-14s %-19s -> %s", rec["eval_id"], blueprint[rec["concept_id"]][1]["name_zh"],
                 rec["question_type"], "答对" if v.get("matches_key") else "答错")

    LOG.info("-" * 68)
    LOG.info("初检不一致 %d 题，进入重制", len(need_fix))

    replaced: Dict[str, Dict[str, Any]] = {}
    for cid in need_fix:
        kind, spec = blueprint[cid]
        eval_id = f"EVAL_{cid}"
        normalized, attempts = generate_one(
            opener=opener, api_url=args.api_url, model=args.model, kind=kind, spec=spec,
            records=records, max_retry=args.max_retry, temperature=args.temperature,
            num_predict=args.num_predict, timeout=args.timeout, extra=STRICT_SELFCHECK,
        )
        for a in attempts:
            audit.append({"eval_id": eval_id, "phase": "regen", "question_type": kind, **a})
        if normalized is None:
            LOG.warning("  %s 结构校验未通过，保留原题", eval_id)
            continue

        candidate = {
            "eval_id": eval_id, "concept_id": cid, "question_type": kind,
            "question": normalized["question"], "options": normalized["options"],
            "correct_option": normalized["correct_option"],
            "explanation": normalized["explanation"],
            "target_hallucination_point": normalized["target_hallucination_point"],
        }
        v = blind_verify(opener=opener, api_url=args.api_url, model=args.model,
                         record=candidate, temperature=0.0, num_predict=32, timeout=args.timeout)
        audit.append({"eval_id": eval_id, "phase": "after", **v})
        if v.get("matches_key"):
            replaced[cid] = candidate
            LOG.info("  %s %-14s 重制后通过盲测 ✓", eval_id, spec["name_zh"])
        else:
            LOG.warning("  %s %-14s 重制后仍未通过盲测，保留原题", eval_id, spec["name_zh"])

    final: List[Dict[str, Any]] = [replaced.get(r["concept_id"], r) for r in existing]
    final.sort(key=lambda r: r["eval_id"])
    total_wall = time.perf_counter() - run_start

    with output_path.open("w", encoding="utf-8", newline="\n") as fh:
        for record in final:
            fh.write(json.dumps({k: record[k] for k in EVAL_FIELDS}, ensure_ascii=False) + "\n")

    with raw_path.open("a", encoding="utf-8", newline="\n") as fh:
        for a in audit:
            fh.write(json.dumps(a, ensure_ascii=False) + "\n")

    after_ok = sum(1 for eid, ok in before.items() if ok) + len(replaced)
    still_bad = [f"EVAL_{cid}" for cid in need_fix if cid not in replaced]

    summary = {
        "run_at": utc_now_iso(),
        "stage": 3,
        "task": "缺陷题重制与答案键复核（离线）",
        "model": args.model,
        "checked": len(existing),
        "mismatch_before": len(need_fix),
        "agreement_before": round(sum(1 for v in before.values() if v) / len(before), 4) if before else None,
        "repaired": len(replaced),
        "still_mismatch": len(still_bad),
        "agreement_after": round(after_ok / len(existing), 4) if existing else None,
        "elapsed_seconds": round(total_wall, 3),
        "repaired_ids": sorted(f"EVAL_{c}" for c in replaced),
        "manual_review_required": still_bad,
        "note": ("重制判定为：新题必须同时通过结构校验与盲测自洽才替换。"
                 "未通过的题保留原题并列入 manual_review_required，"
                 "人工复核前不得作为可信答案键使用。"),
    }
    write_json_report(summary, report_path)

    LOG.info("-" * 68)
    LOG.info("盲测自洽：重制前 %d/%d = %.1f%% → 重制后 %d/%d = %.1f%%",
             len(existing) - len(need_fix), len(existing), (1 - len(need_fix) / len(existing)) * 100,
             after_ok, len(existing), after_ok / len(existing) * 100)
    LOG.info("成功重制 %d 题；仍需人工复核 %d 题：%s",
             len(replaced), len(still_bad), ", ".join(still_bad) or "无")
    LOG.info("耗时      : %.1f 秒", total_wall)
    LOG.info("报告文件  : %s", relative_to_project(report_path))
    LOG.info("-" * 68)
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="OpenSciGraph 阶段三：基础物理 AI 评测数据集衍生（本地离线）"
    )
    parser.add_argument("--concepts", type=Path, default=DEFAULT_CONCEPTS, help="阶段二产出 JSONL（只读）")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="评测集输出 JSONL")
    parser.add_argument("--raw-output", type=Path, default=DEFAULT_RAW_OUTPUT, help="模型原始输出留档 JSONL")
    parser.add_argument("--report", type=Path, default=None, help="报告 JSON 路径（默认带时间戳）")
    parser.add_argument("--api-url", default=DEFAULT_API, help="Ollama 接口地址（仅允许本机）")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="模型名")
    parser.add_argument("--limit-per-type", type=int, default=0, help="每类只生成前 N 题（冒烟测试用）")
    parser.add_argument("--max-retry", type=int, default=3, help="单题最大生成次数")
    parser.add_argument("--temperature", type=float, default=0.7, help="出题采样温度")
    parser.add_argument("--num-predict", type=int, default=768, help="单题最大生成 token 数")
    parser.add_argument("--timeout", type=int, default=300, help="单次请求超时（秒）")
    parser.add_argument("--no-verify", action="store_true", help="跳过盲测自洽校验")
    parser.add_argument("--force", action="store_true", help="覆盖已有输出（默认断点续跑）")
    parser.add_argument("--seed", type=int, default=20261014, help="报告抽样随机种子")
    parser.add_argument("--strict", action="store_true", help="出题时附加严格自查指令（减少自相矛盾题）")
    parser.add_argument("--repair", action="store_true",
                        help="修复模式：对已有输出逐题重新盲测，重制未通过自洽校验的题")
    args = parser.parse_args(argv)

    records = load_records(args.concepts)
    LOG.info("已载入阶段二概念 %d 条", len(records))

    tasks = build_blueprint(args.limit_per_type)
    output_path = assert_writable(args.output)
    raw_path = assert_writable(args.raw_output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    report_path = args.report or (REPORTS_DIR / f"physics_eval_v1_run_{timestamp_slug()}.json")
    assert_writable(report_path)

    if args.repair:
        return run_repair(args, records, output_path, raw_path, report_path)

    # 断点续跑
    done: Dict[str, Dict[str, Any]] = {}
    if output_path.exists() and not args.force:
        for obj in (json.loads(l) for l in output_path.read_text(encoding="utf-8").splitlines() if l.strip()):
            done[obj["concept_id"]] = obj
    todo = [t for t in tasks if t[1]["concept_id"] not in done]

    LOG.info("=" * 68)
    LOG.info("阶段三 · 评测集衍生（离线）")
    LOG.info("模型      : %s", args.model)
    LOG.info("接口      : %s", args.api_url)
    LOG.info("本次计划  : %d 题（已完成跳过 %d 题）", len(todo), len(tasks) - len(todo))
    LOG.info("盲测校验  : %s", "关闭" if args.no_verify else "开启")
    LOG.info("输出      : %s", relative_to_project(output_path))
    LOG.info("=" * 68)

    opener = make_localhost_opener()

    results: List[Dict[str, Any]] = list(done.values())
    per_item: List[Dict[str, Any]] = []
    audit_attempts: List[Dict[str, Any]] = []
    failed: List[Dict[str, Any]] = []
    seen_questions = {r["question"] for r in done.values()}

    gen_tokens = gen_ns = 0
    run_start = time.perf_counter()

    for index, (kind, spec) in enumerate(todo, start=1):
        cid = spec["concept_id"]
        eval_id = f"EVAL_{cid}"

        normalized, attempts = generate_one(
            opener=opener, api_url=args.api_url, model=args.model,
            kind=kind, spec=spec, records=records, max_retry=args.max_retry,
            temperature=args.temperature, num_predict=args.num_predict, timeout=args.timeout,
            extra=STRICT_SELFCHECK if args.strict else "",
        )
        for a in attempts:
            audit_attempts.append({"eval_id": eval_id, "question_type": kind, **a})

        if normalized is None:
            LOG.error("[%d/%d] %s %s -> %d 次尝试均不合格", index, len(todo), eval_id, spec["name_zh"], len(attempts))
            failed.append({"eval_id": eval_id, "concept_id": cid, "name_zh": spec["name_zh"],
                           "question_type": kind, "attempts": len(attempts)})
            per_item.append({"eval_id": eval_id, "concept_id": cid, "question_type": kind,
                             "status": "failed", "attempts": len(attempts)})
            continue

        if normalized["question"] in seen_questions:
            LOG.warning("[%d/%d] %s 题干与已有题目重复，已记录待复核", index, len(todo), eval_id)
        seen_questions.add(normalized["question"])

        success_attempt = attempts[-1]
        gen_tokens += int(success_attempt.get("eval_count") or 0)
        gen_ns += int(success_attempt.get("eval_duration_ns") or 0)

        record = {
            "eval_id": eval_id,
            "concept_id": cid,
            "question_type": kind,
            "question": normalized["question"],
            "options": normalized["options"],
            "correct_option": normalized["correct_option"],
            "explanation": normalized["explanation"],
            "target_hallucination_point": normalized["target_hallucination_point"],
        }

        verification = {"skipped": True}
        if not args.no_verify:
            verification = blind_verify(
                opener=opener, api_url=args.api_url, model=args.model,
                record=record, temperature=0.0, num_predict=32, timeout=args.timeout,
            )

        results.append(record)
        per_item.append({
            "eval_id": eval_id, "concept_id": cid, "name_zh": spec["name_zh"],
            "question_type": kind, "status": "ok",
            "attempts": len(attempts),
            "issues": success_attempt.get("issues") or [],
            "wall_s": success_attempt.get("wall_s"),
            "eval_count": success_attempt.get("eval_count"),
            "verify_model_answer": verification.get("model_answer"),
            "verify_matches_key": verification.get("matches_key"),
            "verify_skipped": bool(verification.get("skipped")),
        })

        mark = "答对" if verification.get("matches_key") else (
            "答错" if verification.get("ok") else "盲测失败"
        )
        LOG.info("[%d/%d] %s %-14s | %-19s | %5.2fs | %3d tok | 盲测:%s",
                 index, len(todo), eval_id, spec["name_zh"], kind,
                 success_attempt.get("wall_s") or 0,
                 success_attempt.get("eval_count") or 0, mark)
        for issue in (success_attempt.get("issues") or []):
            LOG.warning("        · %s", issue)

    total_wall = time.perf_counter() - run_start

    # ---- 写输出（按 eval_id 排序，保证可复现）----
    results.sort(key=lambda r: r["eval_id"])
    with output_path.open("w", encoding="utf-8", newline="\n") as fh:
        for record in results:
            fh.write(json.dumps({k: record[k] for k in EVAL_FIELDS}, ensure_ascii=False) + "\n")

    raw_path.write_text(
        "".join(json.dumps(a, ensure_ascii=False) + "\n" for a in audit_attempts),
        encoding="utf-8", newline="\n",
    )

    # ---- 统计 ----
    by_type: Dict[str, int] = {}
    for r in results:
        by_type[r["question_type"]] = by_type.get(r["question_type"], 0) + 1

    verifiable = [i for i in per_item if i["status"] == "ok" and not i["verify_skipped"]]
    matched = [i for i in verifiable if i["verify_matches_key"]]
    verify_by_type: Dict[str, Dict[str, int]] = {}
    for i in verifiable:
        slot = verify_by_type.setdefault(i["question_type"], {"checked": 0, "matched": 0})
        slot["checked"] += 1
        slot["matched"] += 1 if i["verify_matches_key"] else 0

    retried = [i for i in per_item if i["status"] == "ok" and i["attempts"] > 1]
    warn_items = [i for i in per_item if i["status"] == "ok" and i["issues"]]

    summary: Dict[str, Any] = {
        "run_at": utc_now_iso(),
        "stage": 3,
        "task": "基础物理 AI 评测数据集衍生（离线）",
        "model": args.model,
        "api_url": args.api_url,
        "json_format_enforced": True,
        "schema": relative_to_project(SCHEMA_FILE),
        "source_data": relative_to_project(args.concepts),
        "output": relative_to_project(output_path),
        "raw_output": relative_to_project(raw_path),
        "planned": len(tasks),
        "generated": len(results),
        "failed": len(failed),
        "elapsed_seconds": round(total_wall, 3),
        "elapsed_per_item_avg_s": round(total_wall / len(todo), 3) if todo else None,
        "distribution": {
            "overall": by_type,
            "ratio_actual": {
                k: round(v / len(results), 4) for k, v in by_type.items()
            } if results else {},
        },
        "format_quality": {
            "structure_pass_rate": round((len(results) / len(tasks)), 4) if tasks else 0.0,
            "items_needing_retry": len(retried),
            "retry_rate": round(len(retried) / len(results), 4) if results else 0.0,
            "items_with_warnings": len(warn_items),
            "warn_rate": round(len(warn_items) / len(results), 4) if results else 0.0,
        },
        "tokens": {
            "generated_total": gen_tokens,
            "generated_per_item_avg": round(gen_tokens / len(results), 1) if results else 0,
            "decode_seconds_total": round(gen_ns / 1e9, 3),
            "overall_tokens_per_sec": round(gen_tokens / (gen_ns / 1e9), 2) if gen_ns else 0.0,
        },
        "blind_self_consistency": {
            "checked": len(verifiable),
            "matched_key": len(matched),
            "agreement_rate": round(len(matched) / len(verifiable), 4) if verifiable else None,
            "by_type": verify_by_type,
            "note": ("盲测自洽 = 把题面单独喂回模型，看它是否选到答案键。"
                     "对概念辨析/公式题，高一致率是好事；"
                     "对幻觉陷阱题，**低一致率恰恰说明陷阱有效**。"),
        },
        "failed_items": failed,
        "items": per_item,
    }

    write_json_report(summary, report_path)

    LOG.info("-" * 68)
    LOG.info("完成：生成 %d 题（失败 %d 题），耗时 %.1f 秒（平均 %.2f 秒/题）",
             len(results), len(failed), total_wall,
             total_wall / len(todo) if todo else 0)
    LOG.info("题型分布  : %s", json.dumps(by_type, ensure_ascii=False))
    LOG.info("结构通过率: %.1f%%（重掷 %d 题，告警 %d 题）",
             (len(results) / len(tasks) * 100) if tasks else 0, len(retried), len(warn_items))
    if verifiable:
        LOG.info("盲测自洽  : 一致 %d/%d = %.1f%%", len(matched), len(verifiable),
                 len(matched) / len(verifiable) * 100)
        for kind, slot in sorted(verify_by_type.items()):
            LOG.info("            · %-20s %d/%d", kind, slot["matched"], slot["checked"])
    LOG.info("生成 token: %d（%.1f tok/s）", gen_tokens,
             gen_tokens / (gen_ns / 1e9) if gen_ns else 0)
    LOG.info("输出文件  : %s", relative_to_project(output_path))
    LOG.info("报告文件  : %s", relative_to_project(report_path))
    LOG.info("-" * 68)

    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
