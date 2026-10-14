#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OpenSciGraph v0.1 MVP · HuggingFace 在线加载冒烟测试

核心就 3 行（见 ``main()`` 内标注 ①②③），用来验证 ``datasets`` 能否远程加载本数据集
并输出解析结果。其余都是给失败场景加的可读诊断，不是必需逻辑。
"""

from __future__ import annotations

import sys

#: 数据集仓库 ID（可按需覆盖）
REPO = "OpenSciGraph/OpenSciGraph-Physics-Bench"


def main(repo: str = REPO) -> int:
    # ① 远程加载评测题分片（16 行，一行一题）
    # ② 远程加载概念分片（16 行，一行一概念）
    # ③ 打印解析结果
    from datasets import load_dataset
    bench = load_dataset(repo, "eval_items", split="train")
    concepts = load_dataset(repo, "concepts", split="train")
    print(bench, concepts, bench[0])

    print()
    print("=" * 72)
    print(f"eval_items：{bench.num_rows} 行 × {len(bench.column_names)} 列")
    print(f"  列名：{bench.column_names}")
    print(f"  首行：{bench[0]['eval_id']} | {bench[0]['question_type']} | 答案键 {bench[0]['correct_option']}")
    print(f"  题型分布：{ {t: bench['question_type'].count(t) for t in set(bench['question_type'])} }")
    print(f"  答案键分布：{ {k: bench['correct_option'].count(k) for k in 'ABCD'} }")
    print(f"concepts：{concepts.num_rows} 行 × {len(concepts.column_names)} 列")
    print(f"  首行：{concepts[0]['name_zh']} / {concepts[0]['name_en']}")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    repo_id = sys.argv[1] if len(sys.argv) > 1 else REPO
    try:
        raise SystemExit(main(repo_id))
    except Exception as exc:  # noqa: BLE001 - 冒烟测试要给出可读诊断而非堆栈
        print(f"\n❌ 远程加载失败：{type(exc).__name__}: {exc}\n", file=sys.stderr)
        print("可能原因：", file=sys.stderr)
        print("  1) 仓库尚未真正上传（先用 scripts/upload_to_hf.py 上架）", file=sys.stderr)
        print("  2) 仓库为私有但本地无 token（huggingface-cli login）", file=sys.stderr)
        print("  3) huggingface.co 不可达 —— 中国大陆需代理；", file=sys.stderr)
        print("     下载可临时走镜像：set HF_ENDPOINT=https://hf-mirror.com", file=sys.stderr)
        raise SystemExit(1) from exc
