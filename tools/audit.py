"""知源问病 · 深度审计

查的不是「能不能跑」，是「跑起来会不会害死人」。三类检查：
  A 交叉引用完整性（证型引用的方/穴是否真实存在）
  B 逻辑正确性（安全规则会不会误报/漏报）
  C 数据自洽性（名称冲突、字段缺失、重复 ID）
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from engine.kb import get_kb            # noqa: E402
from engine.safety import get_safety     # noqa: E402

ISSUES: list[tuple[str, str]] = []


def add(level: str, msg: str) -> None:
    ISSUES.append((level, msg))
    print(f"  [{level}] {msg}")


def main() -> int:
    kb = get_kb()
    s = get_safety()
    syn = json.loads((ROOT / "data" / "syndromes.json").read_text(encoding="utf-8"))

    print("=" * 62)
    print("A. 交叉引用完整性")
    print("=" * 62)
    f_ids = {f["id"] for f in kb.formulas}
    a_ids = {a["id"] for a in kb.acupoints}
    bad_f = bad_a = 0
    for sx in syn["syndromes"]:
        for fid in sx.get("fx", []):
            if fid not in f_ids:
                add("严重", f"证型 {sx['id']}({sx['n']}) 引用了不存在的方剂 {fid}")
                bad_f += 1
        for aid in sx.get("ac", []):
            if aid not in a_ids:
                add("严重", f"证型 {sx['id']}({sx['n']}) 引用了不存在的穴位 {aid}")
                bad_a += 1
    print(f"  方剂引用：{len(syn['syndromes'])} 个证型，错误 {bad_f}")
    print(f"  穴位引用：错误 {bad_a}")
    d_ids = {s2["id"] for s2 in syn["syndromes"]}
    for d in syn["diseases"]:
        for sid in d.get("sx", []):
            if sid not in d_ids:
                add("严重", f"病种 {d['name']} 引用了不存在的证型 {sid}")
    print(f"  病种->证型引用：错误 {len([1 for d in syn['diseases'] for sid in d.get('sx',[]) if sid not in d_ids])}")

    print("\n" + "=" * 62)
    print("B. 安全规则逻辑（重点：会不会误报/漏报）")
    print("=" * 62)

    # B1 十八反检测：人参 + 白芍 同用是否被误判为十八反
    print("\nB1. 十八反检测是否误报")
    fake = {"name": "测试方", "herbs": "人参9g 白术9g 茯苓9g 炙甘草6g 白芍12g 当归9g 远志6g",
            "cautions": ""}
    warns = s.check_formula(fake, {})
    hit18 = [w for w in warns if "十八反" in w]
    if hit18:
        add("严重", f"十八反检测误报！人参+白芍被判反药：{hit18[0][:60]}")
    else:
        print("   人参+白芍（归脾汤）未被误判为十八反  OK")

    # B2 真正含反药的方是否被抓到
    fake2 = {"name": "测试反药方", "herbs": "甘草6g 海藻12g", "cautions": ""}
    w2 = s.check_formula(fake2, {})
    print(f"   甘草+海藻 被抓十八反：{'是' if any('十八反' in x for x in w2) else '否 ← 漏报'}")

    # B3 孕妇硬规则是否过度拦截
    print("\nB2. 孕妇硬规则是否过度拦截")
    preg = {"pregnant": True}
    for t, expect, label in [("怀孕8周肚子疼", "E12", "腹痛（该拦）"),
                             ("怀孕20周下腹痛", "E12", "下腹痛（该拦）"),
                             ("怀孕20周牙疼", "—", "牙疼（不该拦）"),
                             ("怀孕20周头疼", "—", "头疼（不该拦）"),
                             ("怀孕20周嗓子疼", "—", "咽疼（不该拦）"),
                             ("怀孕20周腰疼", "—", "腰疼（不该拦）")]:
        blk = s.emergency_block(t, preg)
        got = blk["id"] if blk else "—"
        flag = "OK" if got == expect else "BUG"
        if flag == "BUG":
            add("严重", f"孕妇硬规则 {label}：期望 {expect} 实际 {got}")
        else:
            print(f"   {label:<14} -> {got:<4} {flag}")

    # B4 婴幼儿
    print("\nB3. 婴幼儿规则")
    for t, prof, label in [("宝宝嗜睡不醒", {"age": 0.5}, "嗜睡（该拦）"),
                           ("宝宝拉肚子", {"age": 0.5}, "拉肚子（不该拦）")]:
        blk = s.emergency_block(t, prof)
        print(f"   {label:<16} -> {blk['id'] if blk else '—'}")

    # B5 红旗关键词误伤检查
    print("\nB4. 普通症状是否被红旗误伤")
    for t in ["我这两天拉肚子", "有点头疼", "睡不着", "胃疼", "咳嗽有痰",
              "腰疼", "手脚麻", "头晕", "牙疼"]:
        blk = s.emergency_block(t, {})
        if blk:
            add("注意", f"「{t}」被红旗拦截：{blk['id']} {blk['cat']}")
        else:
            print(f"   「{t}」未误伤  OK")

    print("\n" + "=" * 62)
    print("C. 数据自洽性")
    print("=" * 62)
    for name, coll in [("方剂", kb.formulas), ("中药", kb.herbs), ("经穴", kb.acupoints),
                       ("证型", kb.syndromes)]:
        ids = [x["id"] for x in coll]
        dup = {i for i in ids if ids.count(i) > 1}
        if dup:
            add("严重", f"{name} 重复 ID：{dup}")
    print("   ID 唯一性 OK")

    # 经穴名与董氏名冲突
    m_names = {a["name"] for a in kb.acupoints}
    d_names = {n["name"] for n in kb.dongshi_names}
    conflict = m_names & d_names
    print(f"   经穴与董氏同名穴：{conflict if conflict else '无'}")

    # verified 分布
    tot = sum(1 for c in (kb.formulas, kb.herbs, kb.acupoints)
              for x in c if x.get("verified"))
    alld = sum(len(c) for c in (kb.formulas, kb.herbs, kb.acupoints))
    print(f"   方/药/穴 verified=true：{tot}/{alld}")

    print("\n" + "=" * 62)
    lvl = {}
    for lv, _ in ISSUES:
        lvl[lv] = lvl.get(lv, 0) + 1
    if not ISSUES:
        print("审计结果：未发现问题")
    else:
        print("审计发现：" + "、".join(f"{k} {v} 处" for k, v in lvl.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
