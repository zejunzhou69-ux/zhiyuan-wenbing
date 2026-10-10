r"""知源问病 · 病种扩充共享写入器

把 add_diseases.py 里已验证的写入逻辑抽出来，供各批扩充脚本复用。

强校验不可省：证型元组一旦错位，脚本不会报错，只会静默产出垃圾数据。
所以这里在写入前就把 sy/fx/ac 的类型、11 项结构、非空字符串全部卡死。

全部内容标 verified=false，内容为教材通行表述的整理，待人工核对。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

F = ROOT / "data" / "syndromes.json"

# 中医内科学标准病种（59），用于缺口计算
STANDARD_59 = {
    "呼吸系": ["感冒", "咳嗽", "哮病", "喘证", "肺痈", "肺痨", "肺胀", "肺痿"],
    "心脑系": ["心悸", "胸痹", "不寐", "癫狂", "痫病", "痴呆", "厥证", "头痛", "眩晕",
               "中风", "瘿病"],
    "脾胃系": ["胃痛", "痞满", "呕吐", "噎膈", "呃逆", "腹痛", "泄泻", "痢疾", "便秘",
               "便血", "痔疮", "积聚", "鼓胀", "黄疸"],
    "肝胆系": ["胁痛", "黄疸", "积聚", "鼓胀"],
    "肾系": ["水肿", "淋证", "癃闭", "关格", "阳痿", "遗精"],
    "气血津液": ["郁证", "血证", "痰饮", "消渴", "自汗盗汗", "内伤发热", "虚劳",
                 "肥胖", "癌病"],
    "肢体经络": ["痹证", "痉证", "颤证", "腰痛", "痿证", "颈痹"],
    "其他": ["发热", "汗证"],
}


def _check(name: str, s: tuple) -> tuple:
    if len(s) != 11:
        raise ValueError(f"{name} 的证型元组长度应为 11，实际 {len(s)}：{str(s)[:80]}…")
    sname, system, sy, tg, pl, me, tx, fx, ac, df, nt = s
    if not isinstance(sy, list) or not isinstance(fx, list) or not isinstance(ac, list):
        raise TypeError(
            f"{name}/{sname} 字段类型错：sy/fx/ac 必须是 list。"
            f"实际 sy={type(sy).__name__} fx={type(fx).__name__} ac={type(ac).__name__}。"
            f"——多半是元组少写了一项导致整体错位"
        )
    if not all(isinstance(x, str) and x for x in (system, tg, pl, me, tx)):
        raise TypeError(f"{name}/{sname} 的 system/tg/p/me/tx 必须是非空字符串")
    if not isinstance(df, str):
        raise TypeError(f"{name}/{sname} 的 df（鉴别）必须是字符串，无则写空串")
    return s


def apply(NEW: dict, batch: str) -> int:
    data = json.loads(F.read_text(encoding="utf-8"))
    have = {d["name"] for d in data["diseases"]}
    next_id = max(int(s["id"][1:]) for s in data["syndromes"]) + 1

    added_d = added_s = skipped = 0
    for name, (ov, cs, ex, syns) in NEW.items():
        if name in have:
            skipped += 1
            print(f"  跳过已存在：{name}")
            continue
        ids = []
        for s in syns:
            s = _check(name, s)
            sname, system, sy, tg, pl, me, tx, fx, ac, df, nt = s
            sid = f"S{next_id:03d}"
            next_id += 1
            data["syndromes"].append({
                "id": sid, "n": sname, "d": name, "sys": system,
                "sev": "中", "home": False,
                "sy": sy, "tg": tg, "p": pl, "me": me, "tx": tx,
                "fx": fx, "ac": ac,
                "ds": f"（{name}·{sname} 未预设董氏配穴思路）",
                "df": df,
                **({"wn": nt} if nt.startswith("⚠️") else ({"nt": nt} if nt else {})),
            })
            ids.append(sid)
            added_s += 1
        data["diseases"].append({
            "name": name, "cat": "内科", "kw": [name] + cs[:6],
            "sx": ids, "ex": ex, "ov": ov, "cs": cs, "verified": False,
        })
        added_d += 1
        print(f"  新增 {name}：{len(ids)} 个证型 [{ids[0]}~{ids[-1]}]")

    F.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")

    have = {d["name"] for d in data["diseases"]}
    print(f"\n[{batch}] 新增病种 {added_d} 个、证型 {added_s} 个（跳过 {skipped}）")
    print(f"当前覆盖：{len(have)} 个病 / {len(data['syndromes'])} 个证型")

    gap = {}
    for sysname, ds in STANDARD_59.items():
        miss = [d for d in ds if d not in have]
        if miss:
            gap[sysname] = miss
    total = sum(len(v) for v in gap.values())
    print(f"\n剩余缺口（中医内科学 59 病）：{total} 个")
    for sysname, miss in gap.items():
        print(f"  {sysname}：{'、'.join(miss)}")
    (ROOT / "data" / "gap.json").write_text(
        json.dumps({"covered": sorted(have), "gap": gap}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    print("\n缺口已更新到 data/gap.json")
    return 0