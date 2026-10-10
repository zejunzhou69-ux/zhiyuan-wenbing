r"""知源问病 · 提交前安全核验

公开仓库提交前必跑。三件事：
  1. 不该提交的文件有没有混进去（教材原文、PDF、API key 配置）
  2. 代码里有没有硬编码的密钥
  3. 体积是否异常（教材切片会让仓库突然变成几十 MB）

用法：
    python tools/precommit_check.py            # 检查暂存区
    python tools/precommit_check.py --all      # 检查工作区全部文件
    python tools/precommit_check.py --bypass   # 强制通过（不推荐）
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# 绝不能进仓库的路径片段
FORBIDDEN_PATHS = [
    "config/config.json", "config/", ".env", "textbook.jsonl",
    "textbook_raw", "/.venv/", "/venv/", "node_modules/",
]
FORBIDDEN_EXT = [".pdf", ".docx", ".epub"]

# 常见密钥格式
SECRET_PATTERNS = [
    (re.compile(r"sk-[A-Za-z0-9]{16,}"), "OpenAI 风格 key"),
    (re.compile(r"gsk_[A-Za-z0-9]{16,}"), "Groq key"),
    (re.compile(r"AIza[0-9A-Za-z_\-]{30,}"), "Google API key"),
    (re.compile(r"ghp_[A-Za-z0-9]{20,}"), "GitHub token"),
    (re.compile(r"AKIA[0-9A-Z]{12,}"), "AWS Access Key"),
    (re.compile(r"eyJhbGciOi[A-Za-z0-9_\-]{20,}"), "JWT"),
    # api_key 后跟非空字符串字面量
    (re.compile(r"""["']?api[_-]?key["']?\s*[:=]\s*["'][^"'\s]{8,}["']""", re.I), "硬编码 api_key"),
]

TEXT_EXT = [".js", ".py", ".json", ".md", ".jsonc", ".html", ".css", ".txt", ".bat", ".yml", ".yaml"]
MAX_FILE_KB = 3000     # 单文件超过 3MB 基本就是误提交了大文件


def staged_files() -> list[str]:
    try:
        out = subprocess.run(["git", "diff", "--cached", "--name-only"],
                             cwd=ROOT, capture_output=True, text=True, check=True)
        return [x for x in out.stdout.split("\n") if x.strip()]
    except Exception:
        return []


def all_files() -> list[str]:
    import fnmatch
    files: list[str] = []
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(ROOT).as_posix()
        if any(seg in rel for seg in (".git/", "node_modules/", "__pycache__/",
                                       ".venv", "venv/")):
            continue
        files.append(rel)
    return files


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="检查工作区全部文件")
    ap.add_argument("--bypass", action="store_true")
    args = ap.parse_args()

    files = all_files() if args.all else staged_files()
    if not files:
        print("没有待检查的文件（暂存区为空？先 git add）")
        return 0

    print(f"检查 {len(files)} 个文件…\n")
    problems: list[str] = []

    # 1) 禁止路径
    bad_paths = [f for f in files if any(p in f for p in FORBIDDEN_PATHS)]
    bad_ext = [f for f in files if Path(f).suffix.lower() in FORBIDDEN_EXT]
    if bad_paths:
        problems += [f"❌ 禁止提交的路径：{p}" for p in bad_paths]
    if bad_ext:
        problems += [f"❌ 疑似教材/书籍原件：{p}" for p in bad_ext]
    if not bad_paths and not bad_ext:
        print("✅ 1. 无禁止路径（教材切片 / PDF / config / .env 都没混进来）")

    # 2) 密钥扫描
    hits: list[str] = []
    for rel in files:
        p = ROOT / rel
        if p.suffix.lower() not in TEXT_EXT:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for pat, desc in SECRET_PATTERNS:
            for m in pat.finditer(text):
                # 排除明显的占位符与示例
                s = m.group(0)
                if any(x in s.lower() for x in ("your", "你的", "xxx", "填", "example",
                                                 "<key", "placeholder", "sk-xxx")):
                    continue
                hits.append(f"{desc} @ {rel}: {s[:40]}")
    if hits:
        problems += [f"❌ 发现疑似密钥：{h}" for h in hits[:10]]
    else:
        print("✅ 2. 未发现硬编码密钥")

    # 3) 体积
    big = []
    total = 0
    for rel in files:
        p = ROOT / rel
        if p.exists():
            kb = p.stat().st_size / 1024
            total += kb
            if kb > MAX_FILE_KB:
                big.append(f"{rel} ({kb:.0f} KB)")
    if big:
        problems += [f"❌ 单文件过大（疑似误提交）：{b}" for b in big]
    print(f"✅ 3. 总体积 {total:.0f} KB"
          + (f"，但有 {len(big)} 个大文件" if big else "，无异常大文件"))

    if problems:
        print("\n" + "=" * 50)
        print("核验未通过：")
        for p in problems:
            print("  " + p)
        print("\n处理办法：确认 .gitignore 已覆盖；若已暂存，执行 git rm --cached <文件>")
        return 1

    print("\n" + "=" * 50)
    print("核验通过，可以提交。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
