#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OpenSciGraph v0.1 MVP · HuggingFace Datasets 自动上架脚本

功能
----
1. **凭据解析**：``--token`` 参数 → ``HF_TOKEN`` 环境变量 → 本地 ``huggingface-cli login``
   缓存（后者需显式加 ``--use-login-cache``），按序回退；全都没有时打印明确的
   PowerShell 设置指引并**安全退出**。
   ⚠️ 脚本内**不存在**任何硬编码令牌，令牌只能由环境注入，禁止提交进代码库。
2. **命名空间自检**：用 ``whoami()`` 取当前 token 的账号名；若仓库命名空间与账号不一致
   （例如仓库写成组织名 ``OpenSciGraph/...`` 但 token 属于个人账号），会**明确警告**，
   并可加 ``--use-token-namespace`` 自动改写为 ``<账号>/<仓库名>``。
3. **建仓/更新**：``create_repo(..., repo_type="dataset", exist_ok=True)``，已存在则复用。
4. **上传**：完整数据包 + 两个 JSONL 分片 + 数据集卡（改名为 ``README.md``）。
5. **回读校验**：上传后把远端文件**真实下载回来**，按内容计算 sha256 与本地逐字节比对。
6. **在线冒烟**：``--smoke`` 时调用 ``datasets.load_dataset`` 远程拉取并打印解析结果。

用法
----
**方式一（推荐）· 环境变量鉴权**：令牌由**环境变量**注入并直接传给
``HfApi`` / ``hf_hub_download``，**不调用 ``login()``、不写入任何磁盘位置**，
也**完全不依赖 PATH 中的 ``huggingface-cli``**。令牌绝不写进脚本或版本库。

::

    # 0) 先在当前 PowerShell 会话设置令牌（仅本次会话有效，不落盘）
    $env:HF_TOKEN = "hf_xxxxxxxxxxxxxxxx"

    # 一条命令完成：鉴权 → 建仓 → 上传 → 回读校验 → 在线冒烟
    .venv\\Scripts\\python.exe scripts\\upload_to_hf.py --smoke

    # 只做干跑自检（不写任何远端数据）
    .venv\\Scripts\\python.exe scripts\\upload_to_hf.py --check

    # 只做在线冒烟（公开仓库甚至无需令牌）
    .venv\\Scripts\\python.exe scripts\\upload_to_hf.py --smoke-only

**方式二 · 通过虚拟环境的 Python 调用 CLI**（若确实要用命令行登录）::

    .venv\\Scripts\\python.exe -m huggingface_hub.cli.hf_cli login

> ⚠️ 该命令会把令牌**明文写入** ``~/.cache/huggingface/token``。若在意磁盘残留，
> 请改用方式一（环境变量），或登录后自行删除该文件。
> 脚本默认**不会**读取这份缓存，除非显式加 ``--use-login-cache``。

网络提示
--------
本机实测（2026-10-14）：

* ``https://huggingface.co`` —— **不可达**（出口代理返回 502 Tunnel connection failed）；
* ``https://hf-mirror.com`` —— 可达，且**透传写操作**：``create_repo`` /
  ``upload_file`` / ``list_repo_files`` / ``delete_repo`` 全部实测成功。

因此本脚本默认 ``--endpoint https://hf-mirror.com``。镜像的稳定性不由本项目保证，
若你的网络能直连官方站点，请显式加 ``--endpoint https://huggingface.co``。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.common import PROJECT_ROOT, setup_logger, utc_now_iso  # noqa: E402

LOG = setup_logger("upload_to_hf")

RELEASE_DIR: Path = PROJECT_ROOT / "release" / "v0.1_mvp"
GOLDEN_JSON: Path = RELEASE_DIR / "OpenSciGraph_Golden_v0.1.json"
HF_CARD: Path = RELEASE_DIR / "HuggingFace_Dataset_Card.md"
EVAL_JSONL: Path = RELEASE_DIR / "eval_items.jsonl"
CONCEPT_JSONL: Path = RELEASE_DIR / "concepts.jsonl"

#: 默认仓库（与 build_golden_v01.py 中 HF_REPO_ID / CONTACT["hf_home"] 保持一致）
#: 说明：原定的 ``OpenSciGraph`` 组织在 huggingface.co 上不存在（2026-10-14 实测 404）。
#: 账号 ``guowei79`` 虽隶属组织 ``ruguo3500``，但所用细粒度 token 的 ``scoped`` 授权
#: **只覆盖用户实体 guowei79**，不含该组织，故对组织命名空间写入返回 403。
#: 因此发布命名空间定为 ``guowei79``（当前 token 唯一可写处）。
#: 若日后给 token 补上组织权限，只改这一处 + build_golden_v01.py 的 HF_REPO_ID 并重跑即可。
DEFAULT_REPO_ID = "guowei79/OpenSciGraph-Physics-Bench"

#: 默认端点。本机实测：``huggingface.co`` 经出口代理返回 502（不可达）；
#: ``hf-mirror.com`` 可达，且**实测透传写操作**（create_repo / upload_file /
#: list_repo_files / delete_repo 全部成功），故默认走镜像。
#: 若你的网络可直连官方站点，加 ``--endpoint https://huggingface.co`` 即可。
DEFAULT_ENDPOINT = os.environ.get("HF_ENDPOINT") or "https://hf-mirror.com"

#: 凭据来源环境变量名，按序探测（第一个非空者胜出）。
#: ⚠️ 本脚本**不含任何硬编码令牌**（2026-10-14 安全改造）。
#: 严禁把 token 写进代码或提交进版本库；一律通过环境变量注入。
TOKEN_ENV_KEYS: Tuple[str, ...] = ("HF_TOKEN", "HUGGING_FACE_HUB_TOKEN", "HUGGINGFACEHUB_API_TOKEN")

#: 未检测到 HF_TOKEN 时打印的操作指引（要求 Owner 在 PowerShell 里设置后重试）。
TOKEN_MISSING_HINT = '未检测到 HF_TOKEN 环境变量，请在 PowerShell 中执行 $env:HF_TOKEN="your_token" 后重试'

#: ⚠️ 必须在任何 huggingface_hub 导入**之前**把端点写进环境变量：
#: 该库在 import 期就把 ``HF_ENDPOINT`` 读进 ``constants.ENDPOINT`` 常量，
#: 之后再设环境变量对 ``login()`` 之类内部调用无效。
os.environ.setdefault("HF_ENDPOINT", DEFAULT_ENDPOINT)


def _probe_symlink_cache() -> bool:
    """探测「符号链接创建看似成功、内容却落成 0 字节」的异常文件系统。

    huggingface_hub 的缓存默认用**相对符号链接**把 ``snapshots/<rev>/x`` 指向
    ``blobs/<etag>``。在部分沙箱 / 容器 / 受限 Windows 环境里，``os.symlink()``
    不抛异常，但结果是一个 0 字节的普通空文件（不是重分析点），于是读到的文件
    永远是空的 —— 表现为 ``HFValidationError`` 之外的怪象：
    ``Repo card metadata block was not found`` / ``BuilderConfig not found``。

    本函数用一个临时目录做同样的相对符号链接探测；若读回内容不符预期，
    就把 ``HF_HUB_DISABLE_SYMLINKS=1`` 写进环境变量，让缓存改为**复制**落盘。

    ⚠️ 必须在任何 ``huggingface_hub`` 导入之前调用：该库在 import 期读取此变量。

    返回 True 表示符号链接可用（未改动环境变量）。
    """
    import tempfile  # noqa: PLC0415

    try:
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src.bin"
            payload = b"symlink-probe-0123456789"
            src.write_bytes(payload)
            dst = Path(td) / "dst.bin"
            try:
                os.symlink(src.name, dst)          # 与 huggingface_hub 一致：相对链接
            except (OSError, NotImplementedError) as exc:
                LOG.info("本机不支持创建符号链接（%s），缓存将改用复制方式。", type(exc).__name__)
                os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"
                return False
            try:
                size = dst.stat().st_size
                ok = size == len(payload)
            except OSError:
                ok = False
            if not ok:
                os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"
                LOG.warning(
                    "检测到符号链接会落为 0 字节空文件（本环境已知怪癖），"
                    "已自动设置 HF_HUB_DISABLE_SYMLINKS=1，缓存改用复制落盘。"
                )
                return False
            return True
    except Exception as exc:  # noqa: BLE001
        LOG.warning("符号链接探测本身失败（%s: %s），沿用 huggingface_hub 默认行为。",
                    type(exc).__name__, exc)
        return True


_SYMLINK_OK: bool = _probe_symlink_cache()

#: 在线冒烟专用的缓存目录（每次运行前清空，避免被历史脏缓存误导）
SMOKE_CACHE: Path = PROJECT_ROOT / ".hf_smoke_cache"

#: 待上传清单：(本地路径, 仓库内目标文件名)
UPLOAD_PLAN: Tuple[Tuple[Path, str], ...] = (
    (GOLDEN_JSON, "OpenSciGraph_Golden_v0.1.json"),
    (EVAL_JSONL, "eval_items.jsonl"),
    (CONCEPT_JSONL, "concepts.jsonl"),
    (HF_CARD, "README.md"),          # 数据集卡改名为主页 README
)


# ---------------------------------------------------------------------------
# 工具
# ---------------------------------------------------------------------------


def sha256_of(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def resolve_token(cli_token: Optional[str], allow_login_cache: bool = False) -> Optional[str]:
    """按 ``--token`` → ``HF_TOKEN`` 等环境变量 → 本地登录缓存 的顺序解析凭据。

    安全约定（2026-10-14）：
    * 脚本内**不存在**默认令牌，最后兜底的一律是环境变量；
    * 本地登录缓存（``huggingface-cli login`` 写入 ``~/.cache/huggingface/token``）
      属于**磁盘上的明文凭据**，因此默认**不启用**，必须显式传 ``allow_login_cache=True``
      （CLI 对应 ``--use-login-cache``）；
    * 全部失败返回 ``None``，由调用方打印指引并退出——不静默、不猜。
    """
    if cli_token and cli_token.strip():
        LOG.info("凭据来源：--token 参数（注意：命令行令牌会留在 shell 历史里）")
        return cli_token.strip()

    for key in TOKEN_ENV_KEYS:
        val = os.environ.get(key)
        if val and val.strip():
            LOG.info("凭据来源：环境变量 %s ✓", key)
            return val.strip()

    if allow_login_cache:
        try:
            from huggingface_hub import get_token  # noqa: PLC0415
            cached = get_token()
            if cached:
                LOG.warning("凭据来源：本地登录缓存（磁盘明文）。已按 --use-login-cache 显式放行。")
                return cached
        except Exception:  # noqa: BLE001
            pass

    return None


def check_files() -> bool:
    ok = True
    for local, remote in UPLOAD_PLAN:
        if local.exists():
            LOG.info("  待上传 %-34s -> %s（%d 字节）", local.name, remote, local.stat().st_size)
        else:
            LOG.error("  缺少文件：%s（请先运行 scripts/build_golden_v01.py）", local)
            ok = False
    return ok


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------


def _http_probe(url: str, timeout: int = 15) -> Tuple[bool, str]:
    """探测 URL 可达性。

    刻意使用**浏览器 User-Agent**：hf-mirror.com 会对 Python-urllib 的默认 UA
    返回 403，用默认 UA 探测会把「可达」误判成「不可达」。
    """
    import urllib.error  # noqa: PLC0415
    import urllib.request  # noqa: PLC0415

    req = urllib.request.Request(url, headers={"User-Agent": "curl/8.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status == 200, f"HTTP {resp.status}"
    except urllib.error.HTTPError as exc:
        # 401/403 说明网络通了，只是缺权限或仓库不存在
        return exc.code in (401, 403, 404), f"HTTP {exc.code}"
    except Exception as exc:  # noqa: BLE001
        return False, f"{type(exc).__name__}: {exc}"


def preflight(repo_id: str, endpoint: str, token: Optional[str]) -> Dict[str, Any]:
    """连通性 + 凭据有效性 + 命名空间一致性自检。"""
    report: Dict[str, Any] = {"endpoint": endpoint, "reachable": False, "whoami": None}

    ok, detail = _http_probe(f"{endpoint}/api/datasets?limit=1")
    report["reachable"] = ok
    report["reach_detail"] = detail
    if not ok:
        report["reach_error"] = detail
        return report

    if token:
        from huggingface_hub import HfApi  # noqa: PLC0415
        try:
            who = HfApi(endpoint=endpoint, token=token).whoami()
            report["whoami"] = who.get("name") or who.get("user")
            report["orgs"] = [o.get("name") for o in (who.get("orgs") or []) if o.get("name")]
        except Exception as exc:  # noqa: BLE001
            report["whoami_error"] = f"{type(exc).__name__}: {exc}"

    return report


def upload(repo_id: str, endpoint: str, token: str, private: bool) -> Dict[str, Any]:
    from huggingface_hub import HfApi  # noqa: PLC0415

    api = HfApi(endpoint=endpoint, token=token)

    LOG.info("创建或复用 Dataset 仓库：%s", repo_id)
    url = api.create_repo(
        repo_id=repo_id, repo_type="dataset", exist_ok=True, private=private
    )
    LOG.info("仓库地址：%s", url)

    results: List[Dict[str, Any]] = []
    for local, remote in UPLOAD_PLAN:
        LOG.info("上传 %s -> %s ...", local.name, remote)
        info = api.upload_file(
            path_or_fileobj=str(local),
            path_in_repo=remote,
            repo_id=repo_id,
            repo_type="dataset",
            commit_message=f"Add {remote} (OpenSciGraph v0.1 MVP)",
        )
        results.append({
            "local": local.name,
            "remote": remote,
            "local_sha256": sha256_of(local),
            "commit": getattr(info, "oid", None) or str(info),
        })
        LOG.info("  ✓ %s", remote)

    return {"repo_url": url, "files": results}


def verify(repo_id: str, endpoint: str, token: str) -> List[Tuple[str, str, str]]:
    """**真实回读**远端文件并逐字节比对 sha256。

    为什么不用 ``get_paths_info`` 的 ``blob_id`` 做比对：对非 LFS 文件它返回的是
    git blob 的 **SHA-1**（40 位十六进制），而非内容的 SHA-256。拿它和本地
    sha256 比会**永远不相等**，产生假 FAIL（本项目已踩过这个坑）。
    因此这里改为把远端文件下载下来算内容哈希 —— 既是真校验，也顺带证明文件可下载。
    """
    import shutil  # noqa: PLC0415
    import tempfile  # noqa: PLC0415
    from huggingface_hub import hf_hub_download  # noqa: PLC0415

    checks: List[Tuple[str, str, str]] = []
    tmp = Path(tempfile.mkdtemp(prefix="hf_verify_"))
    try:
        for local, remote in UPLOAD_PLAN:
            local_sha = sha256_of(local)
            try:
                got = hf_hub_download(
                    repo_id=repo_id, filename=remote, repo_type="dataset",
                    endpoint=endpoint, token=token, force_download=True,
                    local_dir=str(tmp / remote.replace("/", "_")),
                )
                remote_bytes = Path(got).read_bytes()
            except Exception as exc:  # noqa: BLE001
                checks.append((f"回读 {remote}", "FAIL", f"{type(exc).__name__}: {exc}"))
                continue

            remote_sha = hashlib.sha256(remote_bytes).hexdigest()
            same = remote_sha == local_sha
            checks.append((
                f"回读 {remote} 与本地逐字节一致",
                "PASS" if same else "FAIL",
                f"远端 {len(remote_bytes)} B / 本地 {local.stat().st_size} B, "
                f"sha256 {'一致' if same else f'不一致（{remote_sha[:16]}… vs {local_sha[:16]}…）'}",
            ))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return checks


def smoke(repo_id: str, endpoint: str = DEFAULT_ENDPOINT) -> int:
    """在线冒烟：用 datasets 远程加载并打印解析结果（核心就 3 行）。

    ``datasets`` 库通过 ``HF_ENDPOINT`` 环境变量决定走的站点，故先把它对齐到本次
    使用的 endpoint（默认镜像），否则在 huggingface.co 不可达的网络下必然超时。
    """
    os.environ["HF_ENDPOINT"] = endpoint
    LOG.info("在线冒烟测试：load_dataset('%s', 'eval_items')  端点=%s", repo_id, endpoint)
    try:
        from datasets import load_dataset  # noqa: PLC0415
    except ImportError:
        LOG.error("未安装 datasets，请执行：pip install datasets")
        return 2

    # 每次冒烟都从干净缓存开始：历史脏缓存（例如上传瞬间写入的 0 字节 / .no_exist
    # 条目）会让结果不可信，之前已经因此误判过一次。
    import shutil  # noqa: PLC0415
    if SMOKE_CACHE.exists():
        shutil.rmtree(SMOKE_CACHE, ignore_errors=True)
    SMOKE_CACHE.mkdir(parents=True, exist_ok=True)
    LOG.info("冒烟使用独立缓存目录：%s（已清空）", SMOKE_CACHE)

    try:
        bench = load_dataset(repo_id, "eval_items", split="train", cache_dir=str(SMOKE_CACHE))
        concepts = load_dataset(repo_id, "concepts", split="train", cache_dir=str(SMOKE_CACHE))
    except Exception as exc:  # noqa: BLE001
        LOG.error("远程加载失败：%s: %s", type(exc).__name__, exc)
        LOG.error("常见原因：① 仓库尚未真正上传；② 仓库是私有且当前无 token；")
        LOG.error("          ③ 端点不可达（换 --endpoint，或设 HF_ENDPOINT）；")
        LOG.error("          ④ 卡片 front matter 的 configs 未被镜像站索引（稍等重试）")
        return 1

    print()
    print("=" * 72)
    print(f"eval_items 分片：{bench}")
    print(f"  首行 -> {bench[0]['eval_id']} | {bench[0]['question_type']} | 答案键 {bench[0]['correct_option']}")
    print(f"  答案键分布 -> { {k: bench['correct_option'].count(k) for k in 'ABCD'} }")
    print(f"concepts 分片：{concepts}")
    print(f"  首行 -> {concepts[0]['name_zh']} / {concepts[0]['name_en']} | {concepts[0]['definition_zh']}")
    print("=" * 72)
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="OpenSciGraph v0.1 MVP · HuggingFace Datasets 自动上架",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--repo-id", default=DEFAULT_REPO_ID, help=f"仓库 ID，默认 {DEFAULT_REPO_ID}")
    parser.add_argument("--token", default=None,
                        help="HF 访问令牌（优先于环境变量；注意会留在 shell 历史里）")
    parser.add_argument("--use-login-cache", action="store_true",
                        help="允许回退到本地登录缓存（~/.cache/huggingface/token，磁盘明文，默认禁用）")
    parser.add_argument("--endpoint", default=os.environ.get("HF_ENDPOINT", DEFAULT_ENDPOINT),
                        help=f"HF 端点，默认 {DEFAULT_ENDPOINT}")
    parser.add_argument("--private", action="store_true", help="创建为私有仓库（默认公开）")
    parser.add_argument("--check", action="store_true", help="仅做干跑自检，不上传")
    parser.add_argument("--smoke", action="store_true", help="上传完成后立即做在线冒烟测试")
    parser.add_argument("--smoke-only", action="store_true", help="只做在线冒烟测试，不上传")
    parser.add_argument("--use-token-namespace", action="store_true",
                        help="把仓库命名空间改写为当前 token 所属账号名")
    args = parser.parse_args(argv)

    if args.smoke_only:
        return smoke(args.repo_id, args.endpoint)

    print("=" * 72)
    print("OpenSciGraph v0.1 MVP · HuggingFace 上架")
    print(f"时间：{utc_now_iso()}   端点：{args.endpoint}")
    print("=" * 72)

    LOG.info("第 1 步：检查待上传文件")
    if not check_files():
        LOG.error("文件不齐，中止。请先运行：python scripts/build_golden_v01.py")
        return 2

    LOG.info("第 2 步：解析凭据（环境变量优先，脚本内不含任何硬编码令牌）")
    token = resolve_token(args.token, allow_login_cache=args.use_login_cache)
    if not token:
        print()
        LOG.error("%s", TOKEN_MISSING_HINT)
        print()
        LOG.error("可选方式：")
        LOG.error("  A) 环境变量（推荐，仅当前会话有效、不落盘）：")
        LOG.error('       $env:HF_TOKEN = "hf_xxxxxxxxxxxxxxxx"')
        LOG.error("  B) 临时传参（会留在 shell 历史里）：")
        LOG.error("       .venv\\Scripts\\python.exe scripts\\upload_to_hf.py --token hf_xxxxxxxx")
        LOG.error("  C) 复用已登录的本地缓存（磁盘明文，需显式放行）：")
        LOG.error("       .venv\\Scripts\\python.exe scripts\\upload_to_hf.py --use-login-cache")
        LOG.error("  令牌申请：https://huggingface.co/settings/tokens （需要 write 权限）")
        LOG.error("  ⚠️ 无论哪种方式，都不要把令牌写进代码或提交进版本库。")
        return 3
    LOG.info("凭据已获取（%s…，共 %d 字符）", token[:8], len(token))

    LOG.info("第 2.5 步：凭据注入（环境变量方式，不调用 login()）")
    # login() 内部走 _validate_and_save_token()，**必然**把明文令牌写到
    # ~/.cache/huggingface/token，与"不留明文凭据"的诉求冲突。
    # 本脚本所有 API 调用都显式传 token=，无需登录态；改为仅注入进程环境变量，
    # 使 datasets / hf_hub_download 等下游库也能读到，且进程退出即失效。
    os.environ["HF_TOKEN"] = token
    # login() 内部按 ``constants.ENDPOINT``（import 期从 HF_ENDPOINT 读取）访问站点，
    # 若常量仍是官方站点而官方站不可达，就会 502。故同时改环境变量 + 打常量补丁。
    os.environ["HF_ENDPOINT"] = args.endpoint
    try:
        import huggingface_hub.constants as hf_constants  # noqa: PLC0415
        hf_constants.ENDPOINT = args.endpoint
    except Exception as exc:  # noqa: BLE001
        LOG.warning("无法改写 huggingface_hub.constants.ENDPOINT（%s）", exc)
    LOG.info("已注入 HF_TOKEN 到进程环境（仅本次运行有效，未写入磁盘）✓")
    LOG.info("如需持久化登录，请自行执行："
             ".venv\\Scripts\\python.exe -m huggingface_hub.commands.huggingface_cli login")

    LOG.info("第 3 步：连通性与账号自检")
    pf = preflight(args.repo_id, args.endpoint, token)
    if not pf["reachable"]:
        LOG.error("端点不可达：%s（%s）", args.endpoint, pf.get("reach_error", "?"))
        LOG.error("可尝试的端点：https://hf-mirror.com（实测可达且支持写入）")
        LOG.error("              https://huggingface.co（官方站点，国内通常需代理）")
        return 4
    LOG.info("端点可达 ✓")
    if pf.get("whoami"):
        LOG.info("token 账号：%s", pf["whoami"])
        orgs = pf.get("orgs") or []
        if orgs:
            LOG.info("所属组织：%s", ", ".join(orgs))
        ns = args.repo_id.split("/")[0]
        if ns == pf["whoami"]:
            LOG.info("命名空间 '%s' = token 账号本身 ✓", ns)
        elif ns in orgs:
            LOG.info("命名空间 '%s' 属于当前 token 的可写组织 ✓", ns)
        else:
            LOG.warning("仓库命名空间 '%s' 既不是 token 账号 '%s'，也不在其组织列表 %s 中，"
                        "直接上传很可能返回 403。", ns, pf["whoami"], orgs or "[]")
            if args.use_token_namespace:
                args.repo_id = f"{pf['whoami']}/{args.repo_id.split('/', 1)[-1]}"
                LOG.warning("已按 --use-token-namespace 改写为：%s", args.repo_id)
            else:
                LOG.warning("若该组织确实不存在，请改用：--repo-id %s/%s",
                            pf["whoami"], args.repo_id.split("/", 1)[-1])
    elif pf.get("whoami_error"):
        LOG.error("token 校验失败：%s", pf["whoami_error"])
        LOG.error("令牌可能无效或权限不足（需要 write）。")
        return 5

    if args.check:
        print()
        LOG.info("--check 干跑结束：凭据有效、端点可达、文件齐备，未上传任何数据。")
        return 0

    LOG.info("第 4 步：上传")
    try:
        up = upload(args.repo_id, args.endpoint, token, args.private)
    except Exception as exc:  # noqa: BLE001
        LOG.error("上传失败：%s: %s", type(exc).__name__, exc)
        return 6

    LOG.info("第 5 步：远端回读校验")
    checks = verify(args.repo_id, args.endpoint, token)
    for name, status, detail in checks:
        LOG.info("[%s] %s （%s）", status, name, detail)

    print()
    print("=" * 72)
    print(f"✅ 上架完成：{up['repo_url']}")
    print(f"   数据集页面：https://huggingface.co/datasets/{args.repo_id}")
    print("=" * 72)
    print(json.dumps(up, ensure_ascii=False, indent=2))

    if args.smoke:
        return smoke(args.repo_id, args.endpoint)
    print()
    LOG.info("可执行在线冒烟：python scripts/upload_to_hf.py --smoke-only --repo-id %s --endpoint %s",
             args.repo_id, args.endpoint)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
