r"""知源问病 · 发布打包工具

产出两样东西：
  1) release/知源问病-v<版本>.zip   —— 解压后双击 index.html 即用，无需装任何东西
  2) release/SHA256SUMS.txt         —— 校验和，方便用户确认包没被改过

设计要点：
- zip 内的根目录就是可运行的静态站（不是让你再找目录），避免「下载完还要翻文件夹」
- 「使用说明.md」放在包内第一屏，任意编辑器双击就能看
- 源码单独放在 _源码/ 子目录，想研究或二次开发的人才需要
- 排除 node_modules、__pycache__、.git 等，避免包体积暴涨

用法：
  python tools/make_release.py                  # 只打可运行版
  python tools/make_release.py --with-source    # 连源码一起打
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "release"
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

VERSION = "1.0"
# ⚠️ zip 文件名必须用纯 ASCII。
# 实测：中文名经 GitHub Release 分发后会被剥成「-v1.0.zip」，
# 用户下载到的文件名是残缺的。包内文件名仍用中文，只有包名走 ASCII。
ZIP_STEM = "zhiyuan-wenbing"

# 不进包的目录：构建缓存与体积炸弹
EXCLUDE_DIRS = {
    "node_modules", "__pycache__", ".git", ".github", "release",
    ".wrangler", ".venv", "venv", "test-results", "playwright-report",
}
# 不进包的文件：本地配置与测试产物，不应外传
EXCLUDE_FILES = {
    ".DS_Store", "Thumbs.db", "package-lock.json",
    "config.json", ".env", "credentials.json",
}
EXCLUDE_EXT = {".pyc", ".pyo", ".log", ".tmp", ".zip"}


def version() -> str:
    """从 README 里取版本号，取不到就用默认。"""
    readme = ROOT / "README.md"
    if readme.exists():
        m = re.search(r"v(\d+\.\d+)", readme.read_text(encoding="utf-8"))
        if m:
            return m.group(1)
    return VERSION


def human(n: int) -> str:
    return f"{n / 1024 / 1024:.1f} MB" if n > 1024 * 1024 else f"{n / 1024:.0f} KB"


def add(zf: zipfile.ZipFile, src: Path, arc: str) -> int:
    if src.suffix.lower() in EXCLUDE_EXT:
        return 0
    if src.name in EXCLUDE_FILES:
        return 0
    zf.write(src, arc)
    return src.stat().st_size


def collect(zf: zipfile.ZipFile, base: Path, prefix: str, total: list[int]) -> None:
    for p in sorted(base.rglob("*")):
        if p.is_dir():
            continue
        rel = p.relative_to(base)
        if any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        total[0] += add(zf, p, f"{prefix}/{rel.as_posix()}")


README_TEXT = """# 知源问病 · 使用说明

## 一、怎么打开

**双击 `index.html` 就能用。** 不需要装 Python，不需要联网，不需要注册。

推荐 Chrome / Edge / Firefox / Safari。

- 双击 `index.html` → 在默认浏览器打开
- 也可以把整个文件夹拖进浏览器窗口
- 手机上怎么用，见「三」

## 二、能做什么

**问诊模式**：填 4 项基本信息 → 逐轮回答四诊（望闻问切）→ 给出辨证结论、
治法、方剂、经穴与推拿方案，并单列「必须排除的危险情况」。

**查阅模式**：按病 / 按症 / 按方 / 按穴 / 其他疗法反查。

知识库规模：65 个病种、259 个证型、55 首方剂、170 味中药、120 个经穴、
28 个董氏奇穴穴名、30 种推拿手法、20 个推拿方案。

**董氏奇穴说明**：默认按杨维杰派。穴名层已录入，但**定位数据尚未补录**，
所以输出只给「取穴思路」，不给定位描述——这是刻意的安全设计，避免误导误针。
按原书补录定位后会自动放开。

## 三、手机上怎么用

**方式 A：手机浏览器（推荐，需要联网）**
把 static 目录传到任意静态托管（GitHub Pages / Cloudflare Pages / Vercel），
手机浏览器打开那个网址即可。界面已做移动端适配。

**方式 B：局域网内共用（无需外网）**
在这台电脑上起个本地服务，手机连同一个 Wi-Fi 访问：

    npx serve .

然后手机浏览器打开终端显示的 `http://192.168.x.x:3000`（IP 换成电脑的）。

## 四、能不能外接大模型

默认是**纯规则引擎**，功能完整，不需要任何 API Key。

若要接大模型（仅用于把口语转成规范中医术语，**不参与辨证决策**），
见 `_源码/worker/` 与 `_源码/docs/AI接入配置.md`。

## 五、重要提醒

- 本工具输出的是**中医辨证思路与健康建议，不是处方**，不能替代执业医师面诊。
- 用药前必须经执业中医师复核签字。
- 遇到急症（胸痛、嘴歪伴无力、抽搐、大出血、意识改变等），系统会直接拦下
  并让你去医院——请听它的，不要自行处理。
- 知识内容为教材通行表述的整理，**尚未经执业药师逐条核对**（标注 verified=false）。
  正式使用前请自行核对关键内容。
- 本软件不收集、不上传任何数据，全部计算都在你自己的设备上完成。
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--with-source", action="store_true",
                    help="把完整项目源码一并打进包（体积更大，供二次开发）")
    args = ap.parse_args()

    ver = version()
    OUT.mkdir(exist_ok=True)
    readme_path = OUT / "使用说明.md"
    readme_path.write_text(README_TEXT, encoding="utf-8")

    zip_path = OUT / f"{ZIP_STEM}-v{ver}.zip"
    total = [0]
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        # 1) 使用说明放最前，解压第一眼就能看到
        total[0] += add(zf, readme_path, "使用说明.md")
        # 2) 静态站放根目录，解压即可双击
        collect(zf, ROOT / "static", "", total)
        # 3) 文档
        for d in ("docs", "knowledge"):
            if (ROOT / d).exists():
                collect(zf, ROOT / d, d, total)
        # 4) 可选：完整源码
        if args.with_source:
            for d in ("engine", "tools", "worker", "prompts", "config", "data"):
                if (ROOT / d).exists():
                    collect(zf, ROOT / d, f"_源码/{d}", total)
            for f in ("README.md", "package.json", "wrangler.jsonc",
                      "wrangler-worker.jsonc", "启动知源问病.bat"):
                if (ROOT / f).exists():
                    total[0] += add(zf, ROOT / f, f"_源码/{f}")

    size = zip_path.stat().st_size
    sha = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    (OUT / "SHA256SUMS.txt").write_text(f"{sha}  {zip_path.name}\n", encoding="utf-8")

    with zipfile.ZipFile(zip_path) as zf:
        n = len(zf.namelist())
    print(f"✅ {zip_path.relative_to(ROOT)}")
    print(f"   {n} 个文件 / 压缩后 {human(size)}（原始 {human(total[0])}）")
    print(f"   SHA256 {sha[:16]}…")
    print(f"   含源码：{'是' if args.with_source else '否（纯可运行版）'}")
    print(f"   SHA256SUMS.txt 已写出")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
