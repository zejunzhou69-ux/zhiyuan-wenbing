"""董氏奇穴 PDF 录入工具

用途：把你提供的董氏奇穴原书 PDF（或杨维杰派讲义）切分成结构化待核条目，
      写入 data/dongshi_raw.json，供你逐条核对后并入 data/dongshi.json。

设计原则（不可妥协）：
1. 不猜、不补、不改写原文 —— 只做切分，定位与主治一律保留原文表述。
2. 切出的条目 verified=false、needs_review=true，系统在核对前不会用于输出定位。
3. 扫描版 PDF（无文本层）不做 OCR，明确告知并退出，不产出垃圾数据。
4. 保留页码与原文偏移量，便于你回原书核对。

用法：
    pip install pypdf
    python tools/ingest_dongshi.py "D:/books/董氏奇穴.pdf"
    python tools/ingest_dongshi.py "D:/books/x.pdf" --lineage yangweijie --book "书名" --start 12 --end 60
    python tools/ingest_dongshi.py "D:/books/x.pdf" --dry-run     # 只看切分结果，不写文件
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "dongshi_raw.json"

# 穴位标题的常见写法：独立成行的短标题，或带编号的标题
_HEAD_PATTERNS = [
    re.compile(r"^[（(]?[一二三四五六七八九十百]+[)）、.．]\s*(\S.{0,14})$"),
    re.compile(r"^(\d+)[.、．]\s*(\S.{0,14})$"),
    re.compile(r"^([一-龥]{2,6}(?:穴|腧|针|部))\s*[:：]?\s*$"),
]
# 定位/主治/操作等字段的起始标志
_FIELD_PATTERNS = {
    "location": re.compile(r"(定位|部位|取穴|穴位)\s*[:：]"),
    "indication": re.compile(r"(主治|适应|主治症|功用|功效)\s*[:：]"),
    "needling": re.compile(r"(操作|刺法|针法|要诀|手法)\s*[:：]"),
    "depth": re.compile(r"(针刺深度|深度|进针)\s*[:：]"),
    "caution": re.compile(r"(禁忌|注意|忌)\s*[:：]"),
}


def looks_like_heading(line: str) -> str | None:
    s = line.strip()
    if not s or len(s) > 18:
        return None
    for pat in _HEAD_PATTERNS:
        m = pat.match(s)
        if m:
            title = (m.group(2) if m.lastindex == 2 else m.group(1)).strip()
            if title and not re.search(r"[。；，,]", title):
                return title
    return None


def split_entry(body_lines: list[str]) -> dict:
    """把一条穴位的正文按字段标志切成各字段，保留未识别的原文。"""
    entry: dict = {}
    leftover: list[str] = []
    cur_field = None
    for ln in body_lines:
        hit = None
        for field, pat in _FIELD_PATTERNS.items():
            if pat.search(ln):
                hit = field
                break
        if hit:
            cur_field = hit
            entry[hit] = ln.strip()
        elif cur_field:
            entry[cur_field] += ln.strip()
        else:
            leftover.append(ln.strip())
    if leftover:
        entry["raw_intro"] = "".join(leftover)
    return entry


def ingest(pdf_path: Path, start: int, end: int | None, dry: bool) -> int:
    try:
        from pypdf import PdfReader
    except ImportError:
        print("缺少依赖：pip install pypdf")
        return 2

    reader = PdfReader(str(pdf_path))
    total = len(reader.pages)
    if end is None:
        end = total
    print(f"PDF 共 {total} 页，本次处理 {start}-{min(end, total)} 页")

    entries: list[dict] = []
    empty_pages: list[int] = []

    for pno in range(start, min(end, total) + 1):
        try:
            text = reader.pages[pno - 1].extract_text() or ""
        except Exception as exc:  # noqa: BLE001
            print(f"  第 {pno} 页提取失败：{exc}")
            empty_pages.append(pno)
            continue
        if not text.strip():
            empty_pages.append(pno)
            continue

        lines = [ln.rstrip() for ln in text.splitlines()]
        cur: dict | None = None
        body: list[str] = []

        def flush() -> None:
            nonlocal cur, body
            if cur and body:
                cur.update(split_entry(body))
                cur["_body_preview"] = " ".join(body)[:200]
                entries.append(cur)
            cur, body = None, []

        for ln in lines:
            title = looks_like_heading(ln)
            if title:
                flush()
                cur = {
                    "name": title,
                    "source_page": pno,
                    "lineage": None,      # 由命令行参数统一填写
                    "verified": False,
                    "needs_review": True,
                }
            elif cur is not None:
                body.append(ln)
        flush()

    if not entries:
        print("\n未切分出任何条目。可能原因：")
        print("  1) 页面范围不对 —— 用 --start/--end 调整")
        print("  2) 原书标题格式特殊 —— 需在 _HEAD_PATTERNS 里补规则")
        if empty_pages:
            print(f"  3) 有 {len(empty_pages)} 页提不出文本：{empty_pages[:20]}"
                  f"{' ...' if len(empty_pages) > 20 else ''}")
            print("     → 若是扫描版 PDF（无文本层），本工具不做 OCR，请先 OCR 再录入")
        return 1

    if empty_pages:
        print(f"注意：{len(empty_pages)} 页无文本（可能是插图页/扫描页），这些内容不会被录入")

    print(f"切分出 {len(entries)} 条待核条目，前 10 条：")
    for e in entries[:10]:
        loc = e.get("location", "")[:40]
        print(f"  p{e['source_page']:>4}  {e['name']:<12}  定位:{loc or '（未识别，待手工补）'}")

    if dry:
        print("\n[dry-run] 未写入文件。去掉 --dry-run 即落盘。")
        return 0

    payload = {
        "_meta": {
            "generated_from": str(pdf_path),
            "total_pages": total,
            "processed": f"{start}-{min(end, total)}",
            "entry_count": len(entries),
            "status": "待人工核对。核对完成前系统不得输出这些条目的定位。",
            "how_to_promote": "逐条核对无误后，把该条 append 到 data/dongshi.json 的 points 数组，"
                              "填齐 source_book/source_page，并改 verified: true；"
                              "同时从本文件移除，避免两处不一致。",
        },
        "points": entries,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n已写入 {OUT}")
    print("下一步：打开 data/dongshi_raw.json 逐条核对 -> 补 lineage/source_book -> 并入 dongshi.json")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="董氏奇穴 PDF 录入")
    ap.add_argument("pdf", help="PDF 路径")
    ap.add_argument("--lineage", default="yangweijie", help="流派标记，默认杨维杰派")
    ap.add_argument("--book", default="", help="书名，会写入每条 source_book")
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--end", type=int, default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    pdf = Path(args.pdf)
    if not pdf.exists():
        print(f"文件不存在：{pdf}")
        return 2

    rc = ingest(pdf, args.start, args.end, args.dry_run)

    if rc == 0 and not args.dry_run:
        data = json.loads(OUT.read_text(encoding="utf-8"))
        for e in data["points"]:
            e["lineage"] = args.lineage
            e["source_book"] = args.book or pdf.stem
        OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"已为全部条目标记 lineage={args.lineage}、source_book={args.book or pdf.stem}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())