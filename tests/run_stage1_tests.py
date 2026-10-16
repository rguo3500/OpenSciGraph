# -*- coding: utf-8 -*-
"""
OpenSciGraph - 阶段一一键验收脚本

按顺序真实执行以下步骤，并把 **实际运行结果** 汇总为
reports/initial_test_report.md（不虚构任何通过结论）：

    1. 生成 10 条合成测试记录       -> src/make_sample_data.py
    2. 校验 JSONL                   -> src/check_jsonl.py
    3. 导出 Parquet                 -> src/jsonl_to_parquet.py
    4. 回读 Parquet 验证内容
    5. 运行单元测试                  -> python -m unittest discover -s tests -v

用法（在项目虚拟环境中执行）：
    python tests/run_stage1_tests.py
"""

from __future__ import annotations

import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
REPORTS_DIR = PROJECT_ROOT / "reports"
INTERIM_FILE = PROJECT_ROOT / "data" / "interim" / "sample_records.jsonl"
PARQUET_FILE = PROJECT_ROOT / "data" / "processed" / "sample_records.parquet"
REPORT_FILE = REPORTS_DIR / "initial_test_report.md"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import common  # noqa: E402

RUN_STAMP = common.utc_now_iso()


# ---------------------------------------------------------------------------
# 子进程执行
# ---------------------------------------------------------------------------


def run_step(
    label: str,
    args: List[str],
    expected_returncodes: tuple = (0,),
    expectation_note: str = "",
) -> Dict[str, Any]:
    """
    执行一个子进程步骤，返回其真实结果。

    expected_returncodes 用于声明"符合预期"的退出码集合：
    合成测试夹具故意包含非法 QID，因此校验脚本返回 1 属于预期行为，
    不能被误判为失败。任何未声明的退出码仍会如实标记为失败。
    """
    command = [sys.executable, "-X", "utf8", *args]
    proc = subprocess.run(
        command,
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    expected = proc.returncode in expected_returncodes
    return {
        "label": label,
        "command": " ".join(["python", *args]),
        "returncode": proc.returncode,
        "stdout": (proc.stdout or "").strip(),
        "stderr": (proc.stderr or "").strip(),
        "ok": expected,
        "expected_returncodes": list(expected_returncodes),
        "expectation_note": expectation_note,
    }


def package_version(name: str) -> str:
    """获取第三方库版本，缺失时返回「未安装」。"""
    try:
        module = __import__(name)
        return str(getattr(module, "__version__", "unknown"))
    except Exception:  # noqa: BLE001
        return "未安装"


# ---------------------------------------------------------------------------
# Parquet 回读验证
# ---------------------------------------------------------------------------


def verify_parquet(path: Path) -> Optional[Dict[str, Any]]:
    """读回 Parquet 并抽取验证信息；pandas 不可用或文件缺失时返回 None。"""
    if not path.exists():
        return None
    try:
        import pandas as pd
    except ImportError:
        return None

    df = pd.read_parquet(path, engine="pyarrow")
    samples = {
        "entity_label_zh": [v for v in df["entity_label_zh"].dropna().tolist()][:3],
        "entity_label_en": [v for v in df["entity_label_en"].dropna().tolist()][:3],
    }
    multilingual_probe = {}
    for keyword in ["合成", "日本語", "synthetischer", "ü", "fabricated"]:
        multilingual_probe[keyword] = bool(
            df.astype(str).apply(lambda col: col.str.contains(keyword, regex=False)).any().any()
        )
    return {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "column_names": list(df.columns),
        "null_counts": {c: int(n) for c, n in df.isna().sum().items()},
        "dtypes": {c: str(t) for c, t in df.dtypes.items()},
        "samples": samples,
        "multilingual_probe": multilingual_probe,
    }


# ---------------------------------------------------------------------------
# 项目文件清单
# ---------------------------------------------------------------------------


def list_project_files() -> List[Dict[str, Any]]:
    """列出项目内实际存在的文件（跳过虚拟环境与缓存目录）。"""
    skip_dirs = {".venv", "__pycache__", ".git", ".pytest_cache", ".mypy_cache"}
    files: List[Dict[str, Any]] = []
    for path in sorted(PROJECT_ROOT.rglob("*")):
        if any(part in skip_dirs for part in path.parts):
            continue
        if path.is_file():
            files.append(
                {
                    "path": common.relative_to_project(path),
                    "size": path.stat().st_size,
                    "size_human": common.human_bytes(path.stat().st_size),
                }
            )
    return files


def list_dirs() -> List[str]:
    skip_dirs = {".venv", "__pycache__", ".git"}
    dirs = []
    for path in sorted(PROJECT_ROOT.rglob("*")):
        if any(part in skip_dirs for part in path.parts):
            continue
        if path.is_dir():
            dirs.append(common.relative_to_project(path))
    return dirs


# ---------------------------------------------------------------------------
# 报告生成
# ---------------------------------------------------------------------------


def code_block(text: str, language: str = "") -> str:
    """把文本包成 Markdown 代码块；空文本给出占位符。"""
    body = text.strip() or "（无输出）"
    return f"```{language}\n{body}\n```"


def build_report(context: Dict[str, Any]) -> str:
    steps: List[Dict[str, Any]] = context["steps"]
    report_json: Optional[Dict[str, Any]] = context.get("validation_report")
    export_json: Optional[Dict[str, Any]] = context.get("export_report")
    parquet_info: Optional[Dict[str, Any]] = context.get("parquet_info")
    files: List[Dict[str, Any]] = context["files"]

    total_lines = []
    total_lines.append("# OpenSciGraph · 第一阶段初始测试报告")
    total_lines.append("")
    total_lines.append(f"- 生成时间（UTC）：`{RUN_STAMP}`")
    total_lines.append("- 生成脚本：`tests/run_stage1_tests.py`（基于真实运行结果自动汇总）")
    total_lines.append(f"- 项目根目录：`{PROJECT_ROOT}`")
    total_lines.append("")
    total_lines.append(
        "> **数据性质声明**：本次测试使用的 10 条记录由 `src/make_sample_data.py` 合成生成，"
        "**不是**真实 Wikipedia / Wikidata 数据，每条均标记 `is_synthetic = true`、"
        "`data_origin = SYNTHETIC_TEST_ONLY`。禁止将其作为真实数据使用或对外发布。"
    )
    total_lines.append("")

    # 1. 环境
    total_lines.append("## 1. 环境信息")
    total_lines.append("")
    total_lines.append("| 项目 | 值 |")
    total_lines.append("|---|---|")
    total_lines.append(f"| 操作系统 | {platform.platform()} |")
    total_lines.append(f"| Python | {sys.version.split()[0]} |")
    total_lines.append(f"| Python 路径 | `{sys.executable}` |")
    total_lines.append(f"| pandas | {package_version('pandas')} |")
    total_lines.append(f"| pyarrow | {package_version('pyarrow')} |")
    total_lines.append(f"| numpy | {package_version('numpy')} |")
    total_lines.append("")

    # 2. 步骤总览
    total_lines.append("## 2. 执行步骤与结果")
    total_lines.append("")
    total_lines.append("| # | 步骤 | 命令 | 退出码 | 结果 |")
    total_lines.append("|---|---|---|---|---|")
    for index, step in enumerate(steps, start=1):
        if not step["ok"]:
            mark = "**失败**"
        elif step["returncode"] == 0:
            mark = "通过"
        else:
            mark = f"通过（退出码 {step['returncode']} 属预期）"
        total_lines.append(
            f"| {index} | {step['label']} | `{step['command']}` | {step['returncode']} | {mark} |"
        )
    total_lines.append("")

    expectation_notes = [s for s in steps if s.get("expectation_note") and s["returncode"] != 0]
    if expectation_notes:
        total_lines.append("> **关于非零退出码**：")
        for step in expectation_notes:
            total_lines.append(f"> - `{step['label']}`：{step['expectation_note']}")
        total_lines.append("")

    for index, step in enumerate(steps, start=1):
        total_lines.append(f"### 2.{index} {step['label']}")
        total_lines.append("")
        total_lines.append(f"命令（工作目录 `{PROJECT_ROOT}`）：")
        total_lines.append("")
        total_lines.append(code_block(step["command"], "powershell"))
        total_lines.append("")
        total_lines.append(f"标准输出（退出码 {step['returncode']}）：")
        total_lines.append("")
        total_lines.append(code_block(step["stdout"], "text"))
        if step["stderr"]:
            total_lines.append("")
            total_lines.append("标准错误：")
            total_lines.append("")
            total_lines.append(code_block(step["stderr"], "text"))
        total_lines.append("")

    # 3. 校验结果
    total_lines.append("## 3. JSONL 校验结果（真实统计）")
    total_lines.append("")
    if report_json:
        totals = report_json["totals"]
        counts = report_json["issue_counts"]
        total_lines.append("| 指标 | 数值 |")
        total_lines.append("|---|---|")
        total_lines.append(f"| 输入文件 | `{report_json['input_file']}` |")
        total_lines.append(f"| 文件大小 | {report_json['input_size_human']} |")
        total_lines.append(f"| 总行数 | {totals['total_lines']} |")
        total_lines.append(f"| 可解析记录 | {totals['parsed_records']} |")
        total_lines.append(f"| 有效记录 | {totals['valid_records']} |")
        total_lines.append(f"| 错误记录 | {totals['error_records']} |")
        total_lines.append(f"| 告警记录 | {totals['warning_records']} |")
        total_lines.append(f"| 非法 QID | {counts['invalid_qid']} |")
        total_lines.append(f"| 重复 entity_id | {counts['duplicate_entity_id']} |")
        total_lines.append(f"| 空标签 | {counts['blank_labels']} |")
        total_lines.append(f"| JSON 解析失败 | {counts['invalid_json']} |")
        total_lines.append(f"| 缺必填字段 | {counts['missing_required_fields']} |")
        total_lines.append(f"| 标记为合成数据的记录 | {report_json['synthetic_records_marked_true']} |")
        total_lines.append("")
        total_lines.append("问题明细（QID 与去重）：")
        total_lines.append("")
        total_lines.append(code_block(
            json.dumps(
                {
                    "invalid_qid": report_json["issues"]["invalid_qid"],
                    "duplicate_entity_id": report_json["issues"]["duplicate_entity_id"],
                    "blank_labels": report_json["issues"]["blank_labels"],
                },
                ensure_ascii=False,
                indent=2,
            ),
            "json",
        ))
    else:
        total_lines.append("校验报告未生成。")
    total_lines.append("")

    # 4. Parquet
    total_lines.append("## 4. Parquet 导出结果（真实统计）")
    total_lines.append("")
    if export_json:
        total_lines.append("| 指标 | 数值 |")
        total_lines.append("|---|---|")
        total_lines.append(f"| 输入 | `{export_json['input_file']}`（{export_json['input_size_human']}） |")
        total_lines.append(f"| 输出 | `{export_json['output_file']}`（{export_json['output_size_human']}） |")
        total_lines.append(f"| 写出引擎 | {export_json['engine']} |")
        total_lines.append(f"| 压缩 | {export_json['compression']} |")
        total_lines.append(f"| 保留行数 | {export_json['parquet_stats']['rows']} |")
        total_lines.append(f"| 列数 | {export_json['parquet_stats']['columns']} |")
        total_lines.append(f"| 跳过行数 | {export_json['processing_stats']['skipped_rows']} |")
        total_lines.append(f"| 其中重复行 | {export_json['processing_stats']['duplicate_rows']} |")
        total_lines.append("")
        total_lines.append("被跳过的行（含原因）：")
        total_lines.append("")
        total_lines.append(code_block(json.dumps(export_json["skipped_rows"], ensure_ascii=False, indent=2), "json"))
    else:
        total_lines.append("Parquet 导出报告未生成（可能缺少 pandas / pyarrow）。")
    total_lines.append("")

    if parquet_info:
        total_lines.append("### 4.1 Parquet 回读验证（UTF-8 / 多语言）")
        total_lines.append("")
        total_lines.append("| 指标 | 数值 |")
        total_lines.append("|---|---|")
        total_lines.append(f"| 回读行数 | {parquet_info['rows']} |")
        total_lines.append(f"| 回读列数 | {parquet_info['columns']} |")
        total_lines.append(f"| 列名 | {', '.join(parquet_info['column_names'])} |")
        total_lines.append("")
        total_lines.append("多语言关键字命中情况：")
        total_lines.append("")
        total_lines.append("| 关键字 | 是否命中 |")
        total_lines.append("|---|---|")
        for key, hit in parquet_info["multilingual_probe"].items():
            total_lines.append(f"| `{key}` | {'是' if hit else '否'} |")
        total_lines.append("")
        total_lines.append("列空值统计：")
        total_lines.append("")
        total_lines.append(code_block(json.dumps(parquet_info["null_counts"], ensure_ascii=False, indent=2), "json"))
        total_lines.append("")

    # 5. 单元测试
    unit_step = next((s for s in steps if s["label"].startswith("单元测试")), None)
    total_lines.append("## 5. 单元测试结果")
    total_lines.append("")
    if unit_step:
        total_lines.append(f"- 命令：`{unit_step['command']}`")
        total_lines.append(f"- 退出码：{unit_step['returncode']}（0 = 全部通过）")
        if unit_step["stderr"]:
            total_lines.append("")
            total_lines.append("标准错误输出（unittest 将测试结果写入 stderr）：")
        total_lines.append("")
        total_lines.append(code_block(unit_step["stderr"] or unit_step["stdout"], "text"))
    else:
        total_lines.append("未执行单元测试。")
    total_lines.append("")

    # 6. 文件清单
    total_lines.append("## 6. 实际创建 / 生成的文件")
    total_lines.append("")
    total_lines.append("目录：")
    total_lines.append("")
    total_lines.append(code_block("\n".join(context["dirs"]), "text"))
    total_lines.append("")
    total_lines.append(f"文件共 {len(files)} 个：")
    total_lines.append("")
    total_lines.append("| 文件 | 大小 |")
    total_lines.append("|---|---|")
    for item in files:
        total_lines.append(f"| `{item['path']}` | {item['size_human']} |")
    total_lines.append("")

    # 7. 限制与下一步
    total_lines.append("## 7. 已知限制与未做的事")
    total_lines.append("")
    total_lines.append("- 本阶段 **未** 下载任何 Wikidata / Wikipedia 数据，`data/raw/` 目前仅含保护说明文件。")
    total_lines.append("- 本阶段 **未** 调用任何收费 API，也 **未** 上传任何本地文件。")
    total_lines.append("- `data/raw/` 被硬性保护：脚本向其写入会直接抛出 `PermissionError`（已由单元测试验证）。")
    total_lines.append("- 合成测试数据仅用于验证管道，不代表真实知识图谱分布。")
    total_lines.append("- 尚未定义真实数据源的字段映射与许可审核流程（留待后续阶段）。")
    total_lines.append("")
    total_lines.append("## 8. 下一步（需你确认后才执行）")
    total_lines.append("")
    total_lines.append("1. 确认阶段一产出是否符合预期。")
    total_lines.append("2. 明确第二阶段的数据来源与使用许可，再决定是否接入真实数据。")
    total_lines.append("3. 若来源许可不明，将先产出待审核报告，绝不进入发布环节。")
    total_lines.append("")
    return "\n".join(total_lines)


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------


def main() -> int:
    logger = common.setup_logger("run_stage1_tests")
    common.ensure_dirs()

    steps: List[Dict[str, Any]] = []

    logger.info("步骤 1/5：生成合成测试数据")
    step_gen = run_step("生成合成测试数据", ["src/make_sample_data.py", "--force"])
    steps.append(step_gen)
    logger.info("步骤 1 完成，退出码=%d", step_gen["returncode"])

    logger.info("步骤 2/5：校验 JSONL")
    check_report_path = REPORTS_DIR / "jsonl_check_stage1.json"
    step_check = run_step(
        "校验 JSONL",
        [
            "src/check_jsonl.py",
            "--input", "data/interim/sample_records.jsonl",
            "--output", check_report_path.relative_to(PROJECT_ROOT).as_posix(),
            "--batch-size", "3",
        ],
        # 合成夹具故意包含 2 条非法 QID，校验脚本返回 1 是预期结果
        expected_returncodes=(0, 1),
        expectation_note="退出码 1 属预期：合成夹具故意包含 2 条非法 QID（QABC123、42）",
    )
    steps.append(step_check)
    logger.info("步骤 2 完成，退出码=%d", step_check["returncode"])

    logger.info("步骤 3/5：导出 Parquet")
    export_report_path = REPORTS_DIR / "parquet_export_stage1.json"
    step_export = run_step(
        "导出 Parquet",
        [
            "src/jsonl_to_parquet.py",
            "--input", "data/interim/sample_records.jsonl",
            "--output", "data/processed/sample_records.parquet",
            "--report", export_report_path.relative_to(PROJECT_ROOT).as_posix(),
            "--batch-size", "4",
            "--force",
        ],
    )
    steps.append(step_export)
    logger.info("步骤 3 完成，退出码=%d", step_export["returncode"])

    validation_report = None
    if check_report_path.exists():
        validation_report = json.loads(check_report_path.read_text(encoding="utf-8"))

    export_report = None
    if export_report_path.exists():
        export_report = json.loads(export_report_path.read_text(encoding="utf-8"))

    logger.info("步骤 4/5：回读 Parquet 验证")
    parquet_info = verify_parquet(PARQUET_FILE)
    if parquet_info:
        logger.info("Parquet 回读成功：%d 行 x %d 列", parquet_info["rows"], parquet_info["columns"])
    else:
        logger.warning("Parquet 回读失败或依赖缺失（详见报告）")

    logger.info("步骤 5/5：运行单元测试")
    step_unit = run_step("单元测试（unittest）", ["-m", "unittest", "discover", "-s", "tests", "-v"])
    steps.append(step_unit)
    logger.info("步骤 5 完成，退出码=%d", step_unit["returncode"])

    context = {
        "steps": steps,
        "validation_report": validation_report,
        "export_report": export_report,
        "parquet_info": parquet_info,
        "files": list_project_files(),
        "dirs": list_dirs(),
    }

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    # newline="\n" 必须显式指定：Windows 下 text 模式默认把 \n 翻译成 \r\n，
    # 会把本文件写成 CRLF，与 .gitattributes 的 `* text=auto eol=lf` 冲突，
    # 且导致每次跑完测试工作区都出现无意义的换行差异。
    REPORT_FILE.write_text(build_report(context), encoding="utf-8", newline="\n")
    logger.info("验收报告已生成：%s", common.relative_to_project(REPORT_FILE))

    failed = [s for s in steps if not s["ok"]]
    if failed:
        logger.error("有 %d 个步骤未通过：%s", len(failed), ", ".join(s["label"] for s in failed))
        return 1
    logger.info("全部步骤执行完毕且通过。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
