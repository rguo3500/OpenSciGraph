# 推送到 GitHub 的标准流程

> **状态：已完成（2026-10-14 22:32 首次推送成功）**
> 仓库 <https://github.com/rguo3500/OpenSciGraph> 已公开上线，
> 远端 `main` 与本地 `HEAD` 均为 `546d14f`。
>
> **本机走 SSH 通道**（`git@github.com:rguo3500/OpenSciGraph.git`），
> **不要走 HTTPS** —— 原因见下面「为什么必须用 SSH」一节。

---

## 第 0 步 · 前置状态（已完成，留存备查）

仓库已在 GitHub 网页端建好：`rguo3500/OpenSciGraph`，**Public**，
**建仓时未勾选** README / .gitignore / license（避免与本地已有提交冲突）。

---

## 第 1 步 · 确认 SSH 凭据可用

本机 `~/.ssh/id_ed25519` 已注册在该 GitHub 账号下。验证：

```powershell
ssh -T git@github.com
```

**预期输出**（实测通过）：

```
Hi rguo3500! You've successfully authenticated, but GitHub does not provide shell access.
```

> 看到 `Hi rguo3500!` 即表示 SSH 鉴权成功，**推送无需任何 PAT、无需浏览器登录**。

---

## 第 2 步 · 推送

```powershell
cd E:\OpenSciGraph

# 确认远程是 SSH 形式（若曾是 HTTPS，执行下面这条切换）
git remote set-url origin git@github.com:rguo3500/OpenSciGraph.git

git push -u origin main
```

**实测输出**：

```
To github.com:rguo3500/OpenSciGraph.git
 * [new branch]      main -> main
branch 'main' set up to track 'origin/main'.
```

> 若要在自动化脚本里跑（避免任何交互式提示），加一句
> `$env:GIT_SSH_COMMAND = "ssh -o BatchMode=yes -o ConnectTimeout=20"`。

---

## 为什么必须用 SSH（HTTPS 在本机走不通）

2026-10-14 实测，HTTPS 这条路在本机有**两层**障碍，缺一层都推不上去：

| 层 | 现象 | 说明 |
|---|---|---|
| 网络 | `fatal: unable to access ...: CONNECT tunnel failed, response 502` | 自动化沙箱注入的出口代理白名单**不含 `github.com`**（放行的是 `api.github.com` / `codeload.github.com` / `raw.githubusercontent.com`），代理对 `CONNECT github.com:443` 直接回 502 |
| 凭据 | `fatal: could not read Username for 'https://github.com'` | 本机**不存在任何 GitHub 凭据**：无 `~/.git-credentials`、无 `GH_TOKEN`/`GITHUB_TOKEN`、Windows 凭据管理器为空，`credential.helper` 只指向 PortableGit 的 GUI 选择器 |

**注意**：报错**不是** `Connection was reset`（中国大陆 HTTPS 被 RST 的典型症状）。
本次与 TLS 干扰无关，因此"换代理端口 / 重试 / 调 `http.sslVerify`"这类处置都无效 ——
代理端口即使配对，第二层凭据障碍依然会让推送失败。

SSH 协议天然绕开这两层：不需要 HTTP 代理，也不依赖 HTTPS 凭据。

---

## 备选 · HTTPS + 本地代理（仅在 SSH 不可用时）

若换机后没有可用 SSH key，可退回 HTTPS，但需**同时**解决代理与凭据：

```powershell
# 1) 代理端口按自己软件的实际端口填 —— 本机实测是 7897，不是 7890
#    （7890 / 10809 / 10808 / 1080 / 7891 实测均无监听）
git config --global http.proxy http://127.0.0.1:7897
git config --global https.proxy http://127.0.0.1:7897

# 2) 首次推送仍需交互式登录（Git Credential Manager 会弹浏览器）
git push -u origin main

# 3) 不需要全局代理时取消
# git config --global --unset http.proxy
# git config --global --unset https.proxy
```

---

## 凭据免落盘约定（强制）

| 项 | 约定 |
|---|---|
| HuggingFace 令牌 | **只由 `HF_TOKEN` 环境变量注入**（`$env:HF_TOKEN = "hf_..."`，仅当前会话有效）。`scripts/upload_to_hf.py` 内**零硬编码令牌**，且默认**不读取**本地登录缓存（需显式 `--use-login-cache` 才放行） |
| 本地 HF 令牌缓存 | **已于 2026-10-14 永久清除**（详见下表），全机复扫零残留 |
| GitHub 凭据 | 走 SSH key，不产生任何磁盘明文凭据文件 |
| 仓库内令牌 | 全历史扫描 **0 命中**；`.env*` 已被 `.gitignore` 排除，`.env.example` 只含尖括号占位符 |

**已清除的本地明文残留（删除前 sha256 留档）**：

| 文件 | 大小 | 内容性质 | sha256（审计痕迹） |
|---|---|---|---|
| `~\.cache\huggingface\token` | 37 B | 明文令牌 | `c14516c88cf8b87b23bedf9784741ce4ab165748467ebf2dfb3a4a67d7a0a613` |
| `~\.cache\huggingface\stored_tokens` | 65 B | INI 明文 `hf_token = ...` | `2718f239b9287f3405a2d9b317dcc8c3f12e1fc610e6e1fbfeb002fff862ca2a` |

> 两者均由早期 `huggingface-cli login` 写入。采用**永久删除而非备份/回收站**：
> 凭据文件做备份等于把明文换个位置继续留存，与「彻底消除残留」的目标冲突。
> 留 sha256 指纹是为了保留可核对的审计痕迹。

⚠️ **待办**：上述令牌明文曾出现在对话记录与工具输出中，**建议作废并重新签发**。

---

## SSH 验证状态（2026-10-14 实测）

| 检查项 | 结果 |
|---|---|
| `ssh -T git@github.com` | `Hi rguo3500!` ✓ |
| 密钥 | `~/.ssh/id_ed25519`（ed25519，注释 `dev@pdftoolbox.com`） |
| `~/.ssh/known_hosts` | 已含 github.com 记录 ✓ |
| 远程地址 | `git@github.com:rguo3500/OpenSciGraph.git` ✓ |
| 推送 | `* [new branch] main -> main` ✓ |
| 远端 `main` = 本地 `HEAD` | `546d14f2e105e3521a32c3505e9629dad92bcac4` ✓ |
| 仓库可见性 | Public ✓ |
| 页面渲染 | HTTP 200，无 "Quick setup" 空仓库引导 ✓ |

---

## 推送前自检清单

```powershell
cd E:\OpenSciGraph

# 1) 工作区干净（期望：无任何输出）
git status --short

# 2) 全历史不含令牌（期望：0）
#    注意：不要写 "hf_xxxx…" 这类长占位符，会被本检查误判为令牌。
(git grep -n -E "hf_[A-Za-z0-9]{30,}" (git rev-list --all) 2>$null | Measure-Object).Count

# 3) 未误纳管虚拟环境 / 模型权重 / HF 缓存（期望：0）
@(git ls-files | Select-String -Pattern "\.venv|\.gguf|\.hf_smoke_cache|\.ollama").Count

# 4) 发布产物锁定 LF（期望：eol: lf）
git check-attr eol -- release/v0.1_mvp/eval_items.jsonl
```

**实测记录**：

| 检查 | 结果 |
|---|---|
| `git status --short` | 空 ✓ |
| 全历史令牌扫描 | **0** 命中 ✓ |
| 误纳管文件 | **0** ✓ |
| `eval_items.jsonl` 换行属性 | `eol: lf` ✓ |
| 受控文件数 | 49 ✓ |

> 🔍 **`git check-ignore` 的坑**：查 `.hf_smoke_cache/` 这类目录规则时，
> **不要传裸目录名**（目录不存在时 git 判定不了类型，会返回"未忽略"的假阴性）。
> 正确姿势：`git check-ignore --no-index -v ".hf_smoke_cache/anything"`。

---

## 本机环境备忘（与环境绑定，换机请忽略）

| 项 | 值 |
|---|---|
| 本地代理实测端口 | **`127.0.0.1:7897`**（Clash Verge 默认 mixed 口）；7890/10809/10808/1080/7891 均无监听 |
| 自动化沙箱出口代理 | `127.0.0.1:14705`，白名单不含 `github.com`；**非注册表持久化，仅存在于自动化会话** |
| 沙箱内直连 GitHub | `curl -x http://127.0.0.1:7897 ...`，或 `env -u https_proxy -u HTTPS_PROXY -u http_proxy -u HTTP_PROXY` |
| ⚠️ 全局 SSL 配置 | `http.sslVerify = false`、`http.sslBackend = schannel` —— **全局关闭 TLS 校验属安全隐患**，非本次故障原因，但建议评估是否恢复为 `true` |
| `gh` CLI | **未安装**（PATH 与常见安装目录均无 `gh.exe`） |

---

## 附 · 以后想装 `gh` CLI（可选）

装上之后可以一条命令建仓 + 绑定 + 推送：

```powershell
winget install --id GitHub.cli
gh auth login
gh repo create rguo3500/OpenSciGraph --public --source=. --remote=origin --push
```

> ⚠️ 本机 `winget` 是否可用未验证。若不可用，从 <https://cli.github.com> 下载安装包。

---

## 已知遗留项

| # | 事项 | 处理方式 |
|---|---|---|
| 1 | `data/interim/*`、`data/processed/*` 被 `.gitignore` 排除 | 全量 100 条概念图谱与 50 题评测集**不会进仓库**（仅 `release/v0.1_mvp/` 的 16 组黄金包会进）。若希望开源全量数据，需调整 `.gitignore` 并提交 —— **这是产品决策，需要 Owner 拍板** |
| 2 | `data/raw/README_DO_NOT_OVERWRITE.txt` 会进仓库 | 该文件在 `.gitignore` 里有白名单（`!data/raw/...`），刻意保留用于声明「原始目录只读」，属预期 |
| 3 | `logs/*.log` 被排除 | 运行日志不入库，属预期 |
| 4 | `reports/repair_p042_audit.jsonl` 会进仓库 | 是审计留档（扩展名为 `.jsonl`，未命中 `reports/*.json` 规则），刻意保留 |
| 5 | 早期 HF 令牌明文残留（原遗留项） | **已解决**：`~/.cache/huggingface/token` 与 `stored_tokens` 均已永久清除，全机复扫零残留。待办仅剩「作废并重新签发该令牌」 |
| 6 | GitHub 仓库 Description / Topics 为空 | 建议补上；当前 `description: null`、无 topics |
| 7 | HF 远端内容核验方式 | `hf-mirror.com` 的 `/raw/main/...` 存在**分支级缓存**，可能返回旧版本。核验一律用 `/raw/<commit-sha>/<file>` 固定 revision |
