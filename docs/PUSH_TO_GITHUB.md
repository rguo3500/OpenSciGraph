# 推送到 GitHub 的标准指令

> 本机 **没有安装 `gh` CLI**（2026-10-14 实测：PATH 与常见安装目录均无 `gh.exe`），
> 因此无法用 `gh repo create` 自动建仓。请按下面两步走：先在网页端建空仓库，再一键推送。
>
> 本地仓库已初始化完毕（分支 `main`，1 个初始提交，49 个文件，`.git` 约 494 KB），
> `origin` 已预先配好，**建完仓库只需执行最后一条 `git push`**。

---

## 第 1 步 · 在 GitHub 网页端建空仓库

1. 打开 <https://github.com/new>
2. **Repository name** 填：`OpenSciGraph`
3. Owner 选择：`rguo3500`
4. 可见性：**Public**（市场验证阶段需要公开可访问）
5. ⚠️ **不要勾选** "Add a README file"、".gitignore"、"license" —— 本地已有提交，
   勾了会产生冲突，推送时要额外处理
6. 点 **Create repository**

> 建仓完成后，`https://github.com/rguo3500/OpenSciGraph` 才从 404 变为可访问。
> 在此之前，HuggingFace 数据集页面上指向该仓库的链接是死链。

---

## 第 2 步 · 推送（PowerShell）

```powershell
cd E:\OpenSciGraph
git push -u origin main
```

首次推送会弹窗要求 GitHub 登录（Git Credential Manager），登录一次后自动记住。

**预期输出**：

```
Enumerating objects: 52, done.
Counting objects: 100% (52/52), done.
Writing objects: 100% (52/52), 42.31 KiB | 1.20 MiB/s, done.
To https://github.com/rguo3500/OpenSciGraph.git
 * [new branch]      main -> main
branch 'main' set up to track 'origin/main'.
```

---

## 备选 · 用 SSH 推送

若已配置 SSH key（[配置文档](https://docs.github.com/zh/authentication/connecting-to-github-with-ssh)）：

```powershell
cd E:\OpenSciGraph
git remote set-url origin git@github.com:rguo3500/OpenSciGraph.git
git push -u origin main
```

---

## 附 · 以后想装 `gh` CLI（可选）

装上之后就能一条命令建仓 + 绑定 + 推送：

```powershell
winget install --id GitHub.cli
gh auth login
gh repo create rguo3500/OpenSciGraph --public --source=. --remote=origin --push
```

> ⚠️ 本机 `winget` 是否可用未验证。若不可用，从 <https://cli.github.com> 下载安装包。

---

## 推送前自检清单

> 下面 4 条已于 2026-10-14 在本机**实测通过**，预期值直接写在注释里。

```powershell
cd E:\OpenSciGraph

# 1) 工作区干净（期望：无任何输出）
git status --short

# 2) 全历史不含令牌（期望：0）
#    注意：不要写 "hf_xxxx…" 这类占位符，长占位符会被本检查误判为令牌。
(git grep -n -E "hf_[A-Za-z0-9]{30,}" (git rev-list --all) 2>$null | Measure-Object).Count

# 3) 未误纳管虚拟环境 / 模型权重 / HF 缓存（期望：0）
@(git ls-files | Select-String -Pattern "\.venv|\.gguf|\.hf_smoke_cache|\.ollama").Count

# 4) 发布产物锁定 LF（期望：eol: lf）
git check-attr eol -- release/v0.1_mvp/eval_items.jsonl
```

四条全部符合预期后再 `git push`。以下为**实测记录**：

| 检查 | 实测结果 |
|---|---|
| `git status --short` | 空 ✓ |
| 全历史令牌扫描 | **0** 命中 ✓ |
| 误纳管文件 | **0** ✓ |
| `eval_items.jsonl` 换行属性 | `eol: lf` ✓ |
| 49 个文件的索引内容 vs 磁盘 | 逐字节一致 ✓（`reports/` 下 5 个 md 为 CRLF 落盘、索引已归一化为 LF，属预期） |

---

## 已知遗留项

| # | 事项 | 处理方式 |
|---|---|---|
| 1 | `data/interim/*`、`data/processed/*` 被 `.gitignore` 排除 | 全量 100 条概念图谱与 50 题评测集**不会进仓库**（仅 `release/v0.1_mvp/` 的 16 组黄金包会进）。若希望开源全量数据，需调整 `.gitignore` 并提交 —— **这是产品决策，需要 Owner 拍板** |
| 2 | `data/raw/README_DO_NOT_OVERWRITE.txt` 会进仓库 | 该文件在 `.gitignore` 里有白名单（`!data/raw/...`），刻意保留用于声明「原始目录只读」，属预期 |
| 3 | `logs/*.log` 被排除 | 运行日志不入库，属预期 |
| 4 | `reports/repair_p042_audit.jsonl` 会进仓库 | 是审计留档（扩展名为 `.jsonl`，未命中 `reports/*.json` 规则），刻意保留 |
