"""知源问病 · 教材原文检索

与 kb.py 的分工：
  kb.py          查**结构化条目**（方剂/穴位/证型），精确、可计算、已人工核对为佳
  textbook.py    查**教材原文片段**，用来补充细节与给出出处

为什么两套：结构化库能回答「麻黄汤是什么」，但答不了「教材第几页怎么说的」。
考试与临床都需要后者——引用必须能追到书和页，否则就是编。

检索打分（不引第三方库，纯 Python）：
  词频 + 标题命中加成 + 相邻词加成 + 章节主题匹配
"""
from __future__ import annotations

import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "knowledge" / "textbook.jsonl"

# 中文按字切，英文/数字按词切
_TOKEN_RE = re.compile(r"[一-龥]|[a-zA-Z]+|\d+")


def tokenize(s: str) -> list[str]:
    return _TOKEN_RE.findall(s.lower())


def tokenize_cn2(s: str) -> list[str]:
    """中文双字切分（单字切太碎，召回差噪音大）。"""
    toks = tokenize(s)
    out: list[str] = []
    buf: list[str] = []
    for t in toks:
        if "一" <= t <= "龥":
            buf.append(t)
            if len(buf) == 2:
                out.append("".join(buf))
                buf = buf[1:]
        else:
            if buf:
                out.append(buf[-1])
                buf = []
            out.append(t)
    return out


class TextbookIndex:
    def __init__(self, corpus: Path | None = None) -> None:
        self.path = corpus or CORPUS
        self.records: list[dict] = []
        self.df: Counter = Counter()
        self.avg_len = 1.0
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            return
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                r["_tokens"] = tokenize_cn2(r.get("text", ""))
                r["_tf"] = Counter(r["_tokens"])
                self.records.append(r)
                self.df.update(set(r["_tokens"]))
        if self.records:
            self.avg_len = sum(len(r["_tokens"]) for r in self.records) / len(self.records)

    def __len__(self) -> int:
        return len(self.records)

    # ------------------------------------------------------------------ 检索
    def search(self, query: str, k: int = 5, book: str | None = None,
               chapter: str | None = None) -> list[dict]:
        """BM25 式打分。返回片段列表，带 source_book / source_page / source_chapter。"""
        if not self.records or not query:
            return []
        q = tokenize_cn2(query)
        if not q:
            return []
        pool = [r for r in self.records
                if (not book or r.get("source_book") == book)
                and (not chapter or chapter in (r.get("source_chapter") or ""))]
        if not pool:
            pool = self.records

        N = len(pool)
        scores: list[tuple[float, dict]] = []
        for r in pool:
            s = 0.0
            tf = r["_tf"]
            dl = len(r["_tokens"]) or 1
            for term in q:
                f = tf.get(term, 0)
                if not f:
                    continue
                n = self.df.get(term, 0)
                idf = math.log(1 + (N - n + 0.5) / (n + 0.5))
                s += idf * (f * 2.2) / (f + 1.2 * (0.25 + 0.75 * dl / self.avg_len))
            # 章节标题命中加成：查「某证型的方」时，命中章节名更有价值
            ch = r.get("source_chapter") or ""
            for term in q:
                if len(term) >= 2 and term in ch:
                    s *= 1.25
            if s > 0:
                scores.append((s, r))
        scores.sort(key=lambda x: -x[0])
        out = []
        for s, r in scores[:k]:
            item = {kk: vv for kk, vv in r.items() if not kk.startswith("_")}
            item["score"] = round(s, 3)
            item["citation"] = self.cite(r)
            out.append(item)
        return out

    @staticmethod
    def cite(r: dict) -> str:
        """生成标准出处标注。"""
        bits = [f"《{r.get('source_book', '?')}》"]
        if r.get("source_chapter"):
            bits.append(r["source_chapter"])
        if r.get("source_page"):
            bits.append(f"p{r['source_page']}")
        return " ".join(bits)

    def context_block(self, query: str, k: int = 4) -> str:
        """给提示词用的上下文块，每条都带出处。"""
        hits = self.search(query, k=k)
        if not hits:
            return ""
        out = ["【教材原文片段（引用时必须带上出处）】"]
        for h in hits:
            text = h["text"]
            if len(text) > 300:
                text = text[:300] + "…"
            out.append(f"- {h['citation']}｜{text}")
        return "\n".join(out)

    def stats(self) -> dict:
        books = Counter(r.get("source_book", "?") for r in self.records)
        return {"片段数": len(self.records), "书": len(books), "已入库书目": dict(books)}


_INDEX: TextbookIndex | None = None


def get_textbook() -> TextbookIndex:
    global _INDEX
    if _INDEX is None:
        _INDEX = TextbookIndex()
    return _INDEX


if __name__ == "__main__":
    idx = get_textbook()
    st = idx.stats()
    print(f"教材片段库：{st['片段数']} 片段 / {st['书']} 本书")
    if not st["片段数"]:
        print("\n尚未入库。用法：")
        print('  python tools\\ingest_textbook.py "D:\\书\\方剂学.pdf" --book "方剂学"')
        print('  python tools\\ingest_textbook.py "D:\\中医教材" --batch')
    else:
        print(f"  已入库：{list(st['已入库书目'])}")
        print("\n检索测试（麻黄汤）：")
        for h in idx.search("麻黄汤 组成 功效", k=3):
            print(f"  {h['score']:>6}  {h['citation']}")
            print(f"         {h['text'][:70]}...")
