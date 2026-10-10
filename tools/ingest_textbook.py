r"""知源问病 · 教材入库（通用管道）

与 ingest_dongshi.py 的区别：
  ingest_dongshi  切「一个穴位一条」的条目（董氏奇穴体例）
  ingest_textbook 切「教材正文片段」，供检索与引用溯源

产出 knowledge/textbook.jsonl，每条片段带 source_book / source_page / source_chapter。
检索命中后可以把出处原样带进回答，实现「引教材原文，不把教材话当成自己的结论」。

用法：
    pip install pypdf

    :: 单个 PDF
    python tools\ingest_textbook.py "D:\书\方剂学.pdf" --book "方剂学" --type textbook

    :: 整目录批量（按文件名归类科目）
    python tools\ingest_textbook.py "D:\中医教材" --batch --type textbook

    :: TXT / MD
    python tools\ingest_textbook.py "D:\笔记\伤寒论笔记.md" --book "伤寒论笔记" --type note

    :: 看切分结果不写文件
    python tools\ingest_textbook.py "D:\书\方剂学.pdf" --book "方剂学" --dry-run

支持 --chunk-size / --overlap 控制切片粒度。重叠是为了不让一句话被切断。
按章节边界优先切分，章节标签才不会丢。
扫描版 PDF（无文本层）不做 OCR，明确退出。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
OUT_DIR = ROOT / "knowledge"
OUT_FILE = OUT_DIR / "textbook.jsonl"

# 教材章节标题常见形态，用于给切片打 chapter 标签
_CHAPTER_RE = re.compile(
    r"^\s*(第[一二三四五六七八九十百零〇\d]+[章讲篇部分]|"
    r"[一二三四五六七八九十]+[、.．]\s*|"
    r"[（(][一二三四五六七八九十\d]+[)）]\s*|"
    r"\d+[\.、．]\s*)"
)


def split_pdf_pages(text: str, chunk_size: int, overlap: int) -> list[str]:
    """先按段落聚合，再按字数切；重叠部分不带重复标题。"""
    paras = [p.strip() for p in text.split("\n") if p.strip()]
    chunks: list[str] = []
    buf: list[str] = []
    n = 0
    for p in paras:
        buf.append(p)
        n += len(p)
        if n >= chunk_size:
            chunks.append("\n".join(buf))
            # 重叠：回带最后 overlap 字
            tail, n2 = [], 0
            for prev in reversed(buf):
                if n2 >= overlap:
                    break
                tail.insert(0, prev)
                n2 += len(prev)
            buf, n = list(tail), n2
    if buf:
        chunks.append("\n".join(buf))
    return chunks


def guess_chapter(page_text: str, carry: str) -> str:
    """在片段里找章节标题；找不到就沿用上一个（跨页时标题常在页首）。"""
    for line in page_text.split("\n")[:6]:
        line = line.strip()
        if 3 <= len(line) <= 40 and _CHAPTER_RE.match(line):
            return re.sub(r"^\s*", "", line)
    return carry


def _strip_bom(s: str) -> str:
    return s.lstrip("﻿")


def split_by_chapter(pages: list[str]) -> list[tuple[str, str, int]]:
    """先按章节标题切成 (章节名, 正文, 起始页) 的大段。

    为什么先按章节切：教材的章节边界正是知识边界（第二章解表剂 vs 第九章补益剂），
    按页/按字数硬切会把两章内容混在一片里，章节标签也会丢。
    """
    blocks: list[tuple[str, list[str], int]] = []
    cur_ch, cur_lines, cur_pg = "", [], pages[0] and 1 or 1
    for pno, page in enumerate(pages, 1):
        for line in _strip_bom(page).split("\n"):
            s = line.strip()
            if 3 <= len(s) <= 40 and _CHAPTER_RE.match(s):
                if cur_lines:
                    blocks.append((cur_ch, cur_lines, cur_pg))
                cur_ch, cur_lines, cur_pg = s, [], pno
            else:
                if s:
                    if not cur_lines:
                        cur_pg = pno
                    cur_lines.append(s)
    if cur_lines:
        blocks.append((cur_ch, cur_lines, cur_pg))
    return [(ch, "\n".join(ls), pg) for ch, ls, pg in blocks if ls]


def make_records(pages: list[str], book: str, btype: str,
                 chunk_size: int, overlap: int) -> list[dict]:
    recs: list[dict] = []
    idx = 0
    for chapter, body, start_pg in split_by_chapter(pages):
        for chunk in split_pdf_pages(body, chunk_size, overlap):
            chunk = _strip_bom(chunk.strip())
            if len(chunk) < 20:          # 太短的碎片不入库，避免噪声
                continue
            idx += 1
            recs.append({
                "id": f"T{idx:06d}",
                "source_book": book,
                "source_type": btype,
                "source_page": start_pg,
                "source_chapter": chapter or "（未识别章节）",
                "text": chunk,
                "verified": False,          # 未人工核对
            })
    return recs


def load_pdf_pages(path: Path, start: int, end: int | None) -> list[str]:
    try:
        from pypdf import PdfReader
    except ImportError:
        print("缺少依赖：pip install pypdf")
        sys.exit(2)
    reader = PdfReader(str(path))
    total = len(reader.pages)
    e = min(end or total, total)
    print(f"{path.name}: 共 {total} 页，处理 {start}-{e}")
    pages, empty = [], []
    for p in range(start, e + 1):
        try:
            txt = reader.pages[p - 1].extract_text() or ""
        except Exception:
            txt = ""
        if not txt.strip():
            empty.append(p)
        pages.append(txt)
    if empty:
        print(f"  ⚠️ {len(empty)} 页无文本层（插图页/扫描页），这些页不入库：{empty[:15]}")
        if len(empty) > e - start:
            print("  → 疑似扫描版 PDF，本工具不做 OCR。请先 OCR 再入库。")
            sys.exit(1)
    return pages


def load_text_pages(path: Path) -> list[str]:
    """TXT/MD：每 2000 字当一页，方便统一处理。utf-8-sig 自动剥掉 BOM。"""
    t = path.read_text(encoding="utf-8-sig", errors="ignore")
    step = 2000
    return [t[i:i + step] for i in range(0, len(t), step)] or [""]


def main() -> int:
    ap = argparse.ArgumentParser(description="教材入库（切片 + 索引 + 溯源）")
    ap.add_argument("target", help="PDF 文件或目录")
    ap.add_argument("--book", default="", help="书名（目录批量时取文件名）")
    ap.add_argument("--type", default="textbook",
                    choices=["textbook", "classic", "regulation", "note"])
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--end", type=int, default=None)
    ap.add_argument("--chunk-size", type=int, default=800)
    ap.add_argument("--overlap", type=int, default=100)
    ap.add_argument("--batch", action="store_true", help="target 是目录")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    t = Path(args.target)
    if not t.exists():
        print(f"路径不存在：{t}")
        return 2

    files: list[Path] = []
    if args.batch:
        if not t.is_dir():
            print("--batch 需要传目录")
            return 2
        for ext in ("*.pdf", "*.txt", "*.md"):
            files.extend(sorted(t.glob(ext)))
        if not files:
            print("目录下没有 pdf/txt/md")
            return 1
    else:
        files = [t]

    all_recs: list[dict] = []
    for f in files:
        book = args.book or f.stem
        pages = (load_pdf_pages(f, args.start, args.end)
                 if f.suffix.lower() == ".pdf" else load_text_pages(f))
        recs = make_records(pages, book, args.type, args.chunk_size, args.overlap)
        all_recs.extend(recs)
        print(f"  → {len(recs)} 片段（书名：{book}）")

    print(f"\n合计 {len(all_recs)} 片段")
    for r in all_recs[:5]:
        print(f"  [{r['id']}] p{r['source_page']} 《{r['source_book']}》"
              f"{r['source_chapter'][:16]}  {r['text'][:40]}...")

    if args.dry_run:
        print("\n[dry-run] 未写入。")
        return 0

    OUT_DIR.mkdir(exist_ok=True)
    with OUT_FILE.open("a", encoding="utf-8") as f:
        for r in all_recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"\n已追加写入 {OUT_FILE}")
    print("检索是懒加载的，不需要单独建索引。直接启动服务即可，或用：")
    print("  python -m engine.textbook")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
