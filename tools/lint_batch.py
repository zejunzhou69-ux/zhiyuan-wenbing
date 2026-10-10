r"""知源问病 · 扩充批次数据体检

在跑 apply() 之前，先把该批次所有结构问题一次性列出来，
避免「修一个跑一次、又报下一个」的低效循环。

检查项：
  1. 证型元组长度是否恰为 11
  2. sy/fx/ac 是否 list、df/nt 是否 str
  3. sys/tg/pl/me/tx 是否非空字符串
  4. 方ID(F###)、穴ID(A###) 格式
  5. 是否混入英文（中文语料里出现 ASCII 单词，通常是生成失控的信号）
  6. 是否混入异常重复（排除项里堆砌同一符号属于生成崩坏的信号）

用法：python tools/lint_batch.py tools/add_diseases4.py [more.py ...]
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

F_ID = re.compile(r"^F\d{3}$")
A_ID = re.compile(r"^A\d{3}$")
ASCII_WORD = re.compile(r"[A-Za-z]{2,}")
# 允许的英文：医学检查/指标缩写、编号残留字母。不是"混入英文"。
ALLOWED_TOKENS = {"F", "A", "CT", "AFP", "CO", "MRI", "B", "PH"}
# ⚠️ 重复是本项目的强调风格，只有堆到这么多才算生成失控
WARN_PILE_LIMIT = 8


def load(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[path.stem] = mod
    spec.loader.exec_module(mod)
    return mod


def scan_words(text: str) -> list[str]:
    """返回文本中夹杂的英文单词。"""
    return [w for w in ASCII_WORD.findall(text or "") if w not in ALLOWED_TOKENS]


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2

    total_err = 0
    for arg in argv:
        path = Path(arg)
        if not path.is_absolute():
            cand = ROOT / arg
            path = cand if cand.exists() else Path(arg)
        if not path.exists():
            print(f"[跳过] 找不到文件：{path}")
            continue

        mod = load(path)
        NEW = getattr(mod, "NEW", None)
        if not NEW:
            print(f"[失败] {path.name} 里没有 NEW 字典")
            total_err += 1
            continue

        errs: list[str] = []
        n_dis = n_syn = 0
        for dname, tup in NEW.items():
            n_dis += 1
            if not isinstance(tup, tuple) or len(tup) != 4:
                errs.append(f"{dname}: 病种元组长度应为 4，实际 {len(tup) if isinstance(tup, tuple) else type(tup).__name__}")
                continue
            ov, cs, ex, syns = tup
            if not isinstance(cs, list) or not isinstance(ex, list):
                errs.append(f"{dname}: cs/ex 必须是 list")
            for e in (ex if isinstance(ex, list) else []):
                if isinstance(e, str) and e.count("⚠️") >= WARN_PILE_LIMIT:
                    errs.append(f"{dname}: 排除项重复堆砌 ⚠️（生成失控信号）：{e[:40]}…")
                for w in scan_words(str(e)):
                    errs.append(f"{dname}: 排除项混入英文 {w!r}")

            for i, s in enumerate(syns if isinstance(syns, list) else []):
                n_syn += 1
                tag = f"{dname}[证型{i}]"
                if not isinstance(s, tuple) or len(s) != 11:
                    got = len(s) if isinstance(s, tuple) else type(s).__name__
                    errs.append(f"{tag}: 元组长度应为 11，实际 {got}")
                    continue
                sname, system, sy, tg, pl, me, tx, fx, ac, df, nt = s
                if not isinstance(sy, list):
                    errs.append(f"{tag}/{sname}: sy 必须是 list")
                if not isinstance(fx, list):
                    errs.append(f"{tag}/{sname}: fx 必须是 list")
                if not isinstance(ac, list):
                    errs.append(f"{tag}/{sname}: ac 必须是 list")
                for fname, val, pat in (("fx", fx, F_ID), ("ac", ac, A_ID)):
                    if isinstance(val, list):
                        for x in val:
                            if not pat.match(str(x)):
                                errs.append(f"{tag}/{sname}: {fname} 引用格式错 {x!r}")
                for fname, val in (("df", df), ("nt", nt)):
                    if not isinstance(val, str):
                        errs.append(f"{tag}/{sname}: {fname} 必须是 str（无则写空串）")
                for fname, val in (("sys", system), ("tg", tg), ("pl", pl), ("me", me), ("tx", tx)):
                    if not (isinstance(val, str) and val.strip()):
                        errs.append(f"{tag}/{sname}: {fname} 必须是非空字符串")
                blob = " ".join([str(sname), str(system), str(tg), str(pl), str(me),
                                 str(tx), str(df), str(nt)] +
                                [str(x) for x in (sy if isinstance(sy, list) else [])])
                for w in scan_words(blob):
                    errs.append(f"{tag}/{sname}: 混入英文 {w!r}")

        head = "OK  " if not errs else "FAIL"
        print(f"[{head}] {path.name}：病种 {n_dis} / 证型 {n_syn} / 问题 {len(errs)}")
        for e in errs:
            print(f"       - {e}")
        total_err += len(errs)

    print("-" * 60)
    print("合计问题：" + str(total_err) +
          ("　✅ 可以执行 apply()" if total_err == 0 else "　❌ 先修完再执行"))
    return 0 if total_err == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))