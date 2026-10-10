"""知源问病 · 数据体检

用途：
1. 校验 data/*.json 语法
2. 逐条定位坏条目（给出 id 与原文片段），而不是只报一个行号
3. 统计各库条目数与 verified 分布

用法：
    python tools/check_json.py            # 全量体检
    python tools/check_json.py --file data/acupoints.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def _iter_array_items(text: str, key: str):
    """逐条 yield 数组元素的 (start_index, obj_or_None, raw_text)。"""
    dec = json.JSONDecoder()
    idx = text.index(f'"{key}"')
    idx = text.index("[", idx) + 1
    while True:
        while idx < len(text) and text[idx] in " \r\n\t,":
            idx += 1
        if idx >= len(text) or text[idx] == "]":
            return
        start = idx
        try:
            obj, idx = dec.raw_decode(text, idx)
            yield start, obj, None
        except json.JSONDecodeError as exc:
            yield start, None, text[start:start + 260]
            return


def check_file(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    name = path.name
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        print(f"[FAIL] {name}: 整体解析失败 -> {exc}")
        # 逐条定位
        for key in ("acupoints", "formulas", "herbs", "handcrafts", "protocols", "points", "syndromes"):
            if f'"{key}"' not in text:
                continue
            bad = None
            for start, obj, raw in _iter_array_items(text, key):
                if raw is not None:
                    bad = (start, raw)
                    break
            if bad:
                line = text.count("\n", 0, bad[0]) + 1
                print(f"       └─ 坏条目在 {key}[] 第 {line} 行附近：")
                print(f"          {bad[1]}")
            break
        return 1

    counts = []
    for key, val in data.items():
        if isinstance(val, list):
            counts.append(f"{key}={len(val)}")
    print(f"[ OK ] {name}: {'  '.join(counts) if counts else '(无数组字段)'}")
    return 0


def check_unverified(path: Path) -> None:
    """统计 verified 分布，提醒有多少条目尚未核对原文。"""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return
    total = unverified = 0
    for key, val in data.items():
        if not isinstance(val, list):
            continue
        for item in val:
            if isinstance(item, dict) and "verified" in item:
                total += 1
                if not item["verified"]:
                    unverified += 1
    if total:
        print(f"       verified: {total - unverified} 已核对 / {unverified} 待核对")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=None)
    ap.add_argument("--quiet", action="store_true", help="只看失败项")
    args = ap.parse_args()

    files = [Path(args.file)] if args.file else sorted(DATA.glob("*.json"))
    failures = 0
    for f in files:
        rc = check_file(f)
        failures += rc
        if not args.quiet and rc == 0:
            check_unverified(f)
    print("-" * 50)
    print(f"结果：{len(files)} 个文件，{failures} 个失败")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())