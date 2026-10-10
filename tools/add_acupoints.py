r"""知源问病 · 经穴补录（按考试标准补全十四经穴）

为什么要补：中医执业医师《针灸学》要求掌握十四经穴 361 个的定位，
而本库原先只录了 120 个常用穴，覆盖率约 33%，偏离「考试标准」的要求。

定位依据：GB/T 12346-2006《经络腧穴学》与规划教材《经络腧穴学》通行表述。
与董氏奇穴的区别——经穴有国家标准与统一教材表述，各流派无分歧，
所以可以录入；董氏奇穴各派定位不一致，必须按原书，故留空。

所有条目 verified=false，须逐条对照教材原文核对后方可视为可靠。

用法：
    python tools/add_acupoints.py          # 看统计
    python tools/add_acupoints.py --apply  # 真正写入
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

F = ROOT / "data" / "acupoints.json"

# 考试要求的十四经穴数（GB/T 12346-2006）
STANDARD = {
    "手太阴肺经": 11, "手阳明大肠经": 20, "足阳明胃经": 45, "足太阴脾经": 21,
    "手少阴心经": 9, "手太阳小肠经": 19, "足太阳膀胱经": 67, "足少阴肾经": 27,
    "手厥阴心包经": 9, "手少阳三焦经": 23, "足少阳胆经": 44, "足厥阴肝经": 23,
    "任脉": 24, "督脉": 28,
}

# 必填字段：缺任何一项都拒绝写入，避免造出半成品数据
REQUIRED = ("name", "code", "meridian", "location",
            "anatomy_note", "depth_limit", "indications",
            "needling", "contraindication")


def check(items: list[dict]) -> list[str]:
    """写入前把问题一次列全，而不是边写边报错。"""
    errs = []
    for i, a in enumerate(items):
        tag = a.get("name", f"#{i}")
        for k in REQUIRED:
            v = a.get(k)
            if v is None or (isinstance(v, str) and not v.strip()) or (isinstance(v, list) and not v):
                errs.append(f"{tag}: 缺 {k}")
        if not isinstance(a.get("indications"), list):
            errs.append(f"{tag}: indications 必须是 list")
    return errs


def next_id(data: dict) -> str:
    return f"A{max(int(a['id'][1:]) for a in data['acupoints']) + 1:03d}"


def report(data: dict) -> None:
    from collections import Counter
    have = Counter(a.get("meridian", "?") for a in data["acupoints"])
    print(f"{'经络':<12}{'现有':>6}{'要求':>6}{'缺口':>7}")
    print("-" * 34)
    total_gap = 0
    for m, need in STANDARD.items():
        gap = need - have.get(m, 0)
        total_gap += max(0, gap)
        flag = "" if gap == 0 else f"  ← 缺 {gap}"
        print(f"{m:<12}{have.get(m,0):>6}{need:>6}{gap:>7}{flag}")
    other = sum(v for k, v in have.items() if k not in STANDARD)
    print(f"\n经外奇穴等：{other}")
    print(f"十四经穴合计：{sum(have.get(m,0) for m in STANDARD)} / 361")
    print(f"总缺口：{total_gap} 穴")


def apply(items: list[dict], batch: str) -> int:
    """把一批穴位写入库。幂等：同 code 已存在则跳过。"""
    data = json.loads(F.read_text(encoding="utf-8"))

    errs = check(items)
    if errs:
        print("✗ 字段校验未通过，未写入任何数据：")
        for e in errs[:20]:
            print("   -", e)
        print(f"   共 {len(errs)} 个问题")
        return 1

    have_code = {a.get("code"): a["name"]
                 for a in data["acupoints"] if a.get("code")}
    have_name = {a.get("name") for a in data["acupoints"]}
    nid = next_id(data)
    seq = int(nid[1:])
    added, skipped = 0, []
    # 同 code 但穴名不同 = 编码冲突，必须报出来。
    # 原实现只判「code 是否存在」就静默跳过，导致过 EX-LE5 被说明条目占用、
    # 真正的膝眼被丢弃且无人察觉——静默掩盖问题比报错危险得多。
    conflicts = []

    for a in items:
        owner = have_code.get(a["code"])
        if owner is not None and owner != a["name"]:
            conflicts.append(
                f"编码冲突：{a['code']} 已被「{owner}」占用，"
                f"但本批要录「{a['name']}」——请先修占用者的编码")
        if a["code"] in have_code or a["name"] in have_name:
            skipped.append(a["name"])
            continue
        rec = {
            "id": f"A{seq:03d}", "name": a["name"], "code": a["code"],
            "source_system": "经穴", "meridian": a["meridian"],
            "location": a["location"], "anatomy_note": a["anatomy_note"],
            "depth_limit": a["depth_limit"], "indications": a["indications"],
            "needling": a["needling"], "contraindication": a["contraindication"],
            "self_moxa_safe": a.get("self_moxa_safe", False),
            "verified": False,
        }
        data["acupoints"].append(rec)
        have_code[a["code"]] = a["name"]
        have_name.add(a["name"])
        seq += 1
        added += 1

    if conflicts:
        print("✗ 发现编码冲突，未写入任何数据：")
        for c in conflicts:
            print("   -", c)
        print("   冲突往往说明库里有条目占错了编码，需先人工修正。")
        return 1

    F.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[{batch}] 新增 {added} 穴"
          + (f"，跳过已存在 {len(skipped)} 个：{'、'.join(skipped)}" if skipped else ""))
    report(data)
    return 0
