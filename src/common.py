# -*- coding: utf-8 -*-
"""
OpenSciGraph - 公共工具模块（阶段一）

本模块提供所有脚本共用的基础设施：

- 项目路径常量（config / data / src / tests / reports / docs / logs）
- 配置加载（config/settings.json，失败时回退到内置默认值）
- 日志初始化（同时写入控制台与 logs/*.log，全部 UTF-8）
- JSONL 小批次流式读取（不把整个文件读进内存）
- 写入保护（禁止任何脚本写入 data/raw）
- Wikidata QID 校验
- 统一的时间戳与报告写出辅助函数

设计约束（第一阶段）：
- 只读原始数据，绝不写入或覆盖 data/raw
- 不调用任何网络接口、收费 API
- 不记录任何密钥、令牌或凭据（本模块也从不读取环境变量）
"""

from __future__ import annotations

import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

# ---------------------------------------------------------------------------
# 路径常量
# ---------------------------------------------------------------------------

PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent

CONFIG_DIR: Path = PROJECT_ROOT / "config"
DATA_DIR: Path = PROJECT_ROOT / "data"
RAW_DIR: Path = DATA_DIR / "raw"
INTERIM_DIR: Path = DATA_DIR / "interim"
PROCESSED_DIR: Path = DATA_DIR / "processed"
SRC_DIR: Path = PROJECT_ROOT / "src"
TESTS_DIR: Path = PROJECT_ROOT / "tests"
REPORTS_DIR: Path = PROJECT_ROOT / "reports"
DOCS_DIR: Path = PROJECT_ROOT / "docs"
LOGS_DIR: Path = PROJECT_ROOT / "logs"

CONFIG_FILE: Path = CONFIG_DIR / "settings.json"

#: 受保护目录：任何脚本都不得向其中写入文件（保护原始输入）
PROTECTED_DIRS: Tuple[Path, ...] = (RAW_DIR,)

#: 目录集合，供 ensure_dirs() 一次性创建
ALL_DIRS: Tuple[Path, ...] = (
    CONFIG_DIR,
    RAW_DIR,
    INTERIM_DIR,
    PROCESSED_DIR,
    SRC_DIR,
    TESTS_DIR,
    REPORTS_DIR,
    DOCS_DIR,
    LOGS_DIR,
)

# ---------------------------------------------------------------------------
# Wikidata QID
# ---------------------------------------------------------------------------

#: 合法 QID = 字母 Q + 不以 0 开头的正整数（例如 Q42、Q100001）
QID_PATTERN = re.compile(r"^Q[1-9][0-9]*$")


def is_valid_qid(value: Any) -> bool:
    """判断给定值是否是合法的 Wikidata QID 字符串。"""
    return isinstance(value, str) and bool(QID_PATTERN.match(value))


def qid_number(value: Any) -> Optional[int]:
    """提取 QID 中的数字部分；非法 QID 返回 None。"""
    if is_valid_qid(value):
        return int(value[1:])
    return None


def is_blank(value: Any) -> bool:
    """判断值是否为空：None、空字符串或纯空白字符串。"""
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False


# ---------------------------------------------------------------------------
# 时间戳
# ---------------------------------------------------------------------------


def utc_now() -> datetime:
    """返回当前的 UTC 时间。"""
    return datetime.now(timezone.utc)


def utc_now_iso() -> str:
    """返回 ISO-8601 格式的 UTC 时间字符串（秒级，带 Z 后缀）。"""
    return utc_now().strftime("%Y-%m-%dT%H:%M:%SZ")


def timestamp_slug() -> str:
    """返回适合放入文件名的 UTC 时间戳，例如 20261012T075530Z。"""
    return utc_now().strftime("%Y%m%dT%H%M%SZ")


# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------

DEFAULT_CONFIG: Dict[str, Any] = {
    "project_name": "OpenSciGraph",
    "stage": 1,
    "encoding": "utf-8",
    "batch_size": 500,
    "jsonl": {
        "required_fields": ["entity_id", "source", "is_synthetic", "data_origin"],
        "optional_fields": [
            "entity_label_zh",
            "entity_label_en",
            "entity_type",
            "description",
            "description_lang",
            "aliases",
            "license",
            "retrieved_at",
        ],
        "reject_invalid_qid": True,
        "drop_duplicates_by": "entity_id",
        "max_details_in_report": 50,
    },
    "parquet": {"compression": "snappy", "index": False},
    "logging": {"level": "INFO"},
}


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """递归合并两个字典，override 优先，返回新字典（不修改入参）。"""
    result: Dict[str, Any] = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    加载 config/settings.json，并与内置默认值深度合并。

    配置文件缺失或损坏时不会崩溃，而是回退到内置默认值，
    并通过日志给出警告（保证脚本在最小环境下也能跑通）。
    """
    path = Path(config_path) if config_path else CONFIG_FILE
    if not path.exists():
        logging.getLogger("openscigraph").warning(
            "配置文件不存在，使用内置默认配置：%s", path
        )
        return dict(DEFAULT_CONFIG)
    try:
        with path.open("r", encoding="utf-8") as fh:
            user_cfg = json.load(fh)
        if not isinstance(user_cfg, dict):
            raise ValueError("配置文件顶层必须是 JSON 对象")
        return _deep_merge(DEFAULT_CONFIG, user_cfg)
    except Exception as exc:  # noqa: BLE001 - 配置损坏时降级而非中断
        logging.getLogger("openscigraph").warning(
            "配置文件解析失败（%s），使用内置默认配置：%s", type(exc).__name__, exc
        )
        return dict(DEFAULT_CONFIG)


# ---------------------------------------------------------------------------
# 目录与日志
# ---------------------------------------------------------------------------


def ensure_dirs() -> None:
    """确保项目所有标准目录存在（幂等，可重复调用）。"""
    for directory in ALL_DIRS:
        directory.mkdir(parents=True, exist_ok=True)


def setup_logger(
    name: str = "openscigraph",
    log_dir: Optional[Path] = None,
    level: Optional[str] = None,
) -> logging.Logger:
    """
    初始化日志器：同时输出到控制台与 logs/<name>.log（UTF-8 追加）。

    重复调用不会重复添加 handler（通过私有标记判断）。
    """
    logger = logging.getLogger(name)
    if getattr(logger, "_openscigraph_configured", False):
        return logger

    resolved_level = getattr(logging, str(level or "INFO").upper(), logging.INFO)
    logger.setLevel(resolved_level)
    logger.propagate = False

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台输出：强制 UTF-8，避免 Windows 中文控制台出现乱码或编码异常
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
    except Exception:  # noqa: BLE001 - 老环境不支持 reconfigure 时忽略
        pass
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # 文件输出：始终 UTF-8
    target_dir = Path(log_dir) if log_dir else LOGS_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(
        target_dir / f"{name}.log", mode="a", encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger._openscigraph_configured = True  # type: ignore[attr-defined]
    return logger


# ---------------------------------------------------------------------------
# 写入保护
# ---------------------------------------------------------------------------


def assert_writable(path: Path) -> Path:
    """
    检查目标路径是否允许写入。

    任何位于 data/raw 之下的路径都会抛出 PermissionError，
    以保证原始输入永远不会被脚本覆盖。
    """
    resolved = Path(path).resolve()
    for protected in PROTECTED_DIRS:
        protected_resolved = protected.resolve()
        try:
            resolved.relative_to(protected_resolved)
        except ValueError:
            continue
        raise PermissionError(
            f"拒绝写入受保护目录 data/raw（原始输入不可覆盖）：{resolved}"
        )
    return resolved


# ---------------------------------------------------------------------------
# JSONL 读取
# ---------------------------------------------------------------------------


def iter_jsonl(
    path: Path, batch_size: int = 500
) -> Iterator[List[Tuple[int, str]]]:
    """
    按小批次流式读取 JSONL 文件。

    每次 yield 一个列表，元素为 ``(行号, 该行原始文本)``。
    行号从 1 开始（与文本编辑器一致，便于定位问题行）。

    使用 ``errors="replace"`` 打开文件：即使文件里混入少量非法字节，
    也不会整体崩溃，非法字符会被替换后再进入后续校验并计入报告。
    """
    path = Path(path)
    if batch_size < 1:
        raise ValueError("batch_size 必须 >= 1")
    with path.open("r", encoding="utf-8", errors="replace", newline="") as fh:
        batch: List[Tuple[int, str]] = []
        for lineno, raw_line in enumerate(fh, start=1):
            batch.append((lineno, raw_line))
            if len(batch) >= batch_size:
                yield batch
                batch = []
        if batch:
            yield batch


def parse_jsonl_line(raw_line: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    解析单行 JSONL。

    返回 ``(记录, 错误信息)``：
    - 成功时 ``(dict, None)``
    - 失败时 ``(None, "错误说明")``
    """
    text = raw_line.strip()
    if not text:
        return None, "空行"
    try:
        obj = json.loads(text)
    except json.JSONDecodeError as exc:
        return None, f"JSON 解析失败: 第 {exc.colno} 列 (line {exc.lineno}, col {exc.colno}): {exc.msg}"
    if not isinstance(obj, dict):
        return None, f"顶层结构不是 JSON 对象，而是 {type(obj).__name__}"
    return obj, None


# ---------------------------------------------------------------------------
# 报告输出
# ---------------------------------------------------------------------------


def write_json_report(payload: Dict[str, Any], path: Path) -> Path:
    """把报告以 UTF-8 + 缩进格式写入指定路径（自动创建父目录）。"""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    # newline="\n" 必须显式指定：Windows 下 text 模式会把 \n 翻译成 \r\n，
    # 生成 CRLF 报告，与 .gitattributes 的 `* text=auto eol=lf` 冲突。
    target.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    return target


def human_bytes(size: int) -> str:
    """把字节数格式化成人类可读字符串。"""
    value = float(size)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024.0 or unit == "TB":
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024.0
    return f"{size} B"


def relative_to_project(path: Path) -> str:
    """把绝对路径转成相对项目根目录的 POSIX 风格字符串，便于报告阅读。"""
    resolved = Path(path).resolve()
    try:
        return resolved.relative_to(PROJECT_ROOT.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


# ---------------------------------------------------------------------------
# 文本语言特征（用于多语言统计）
# ---------------------------------------------------------------------------


def contains_cjk(text: Any) -> bool:
    """文本中是否包含中日韩统一表意文字。"""
    if not isinstance(text, str):
        return False
    return any("\u4e00" <= ch <= "\u9fff" for ch in text)


def contains_latin(text: Any) -> bool:
    """文本中是否包含拉丁字母。"""
    if not isinstance(text, str):
        return False
    return any(("a" <= ch.lower() <= "z") for ch in text)
