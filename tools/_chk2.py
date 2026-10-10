r"""国标编码校验：揪出历史录入的编码错配

起因：补录「巨髎 ST8」时冲突检测报出「ST8 已被头维占用」。
查证后确认头维的国标编码是 ST4，ST8 属于巨髎——
说明库里存在编码错配（与之前 EX-LE5 被说明条目占用同类）。

本脚本用国标编码对照表校验全库，列出所有错配，便于一次性修正。
对照表只收录我确信的穴（国标与教材长期一致），不凭印象扩充。
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent

# 穴名 -> 国标编码（GB/T 12346-2006）
CODE = {
    "睛明": "BL1", "攒竹": "BL2", "眉冲": "BL3", "曲差": "BL4", "五处": "BL5",
    "承光": "BL6", "通天": "BL7", "络却": "BL8", "玉枕": "BL9", "天柱": "BL10",
    "风门": "BL12", "肺俞": "BL13", "厥阴俞": "BL14", "心俞": "BL15",
    "督脉俞": "BL16", "膈俞": "BL17", "肝俞": "BL18", "胆俞": "BL19",
    "脾俞": "BL20", "胃俞": "BL21", "三焦俞": "BL22", "肾俞": "BL23",
    "气海俞": "BL24", "大肠俞": "BL25", "关元俞": "BL26", "小肠俞": "BL27",
    "膀胱俞": "BL28", "中膂俞": "BL29", "白环俞": "BL30", "上髎": "BL31",
    "次髎": "BL32", "下髎": "BL33", "会阳": "BL35", "承扶": "BL36",
    "殷门": "BL37", "浮郄": "BL38", "委阳": "BL39", "委中": "BL40",
    "附分": "BL41", "魄户": "BL42", "膏肓": "BL43", "阳纲": "BL49",
    "志室": "BL50", "肓门": "BL51", "胞肓": "BL52", "秩边": "BL54",
    "合阳": "BL55", "承筋": "BL56", "承山": "BL57", "飞扬": "BL58",
    "跗阳": "BL59", "昆仑": "BL60", "仆参": "BL61", "申脉": "BL62",
    "束骨": "BL63", "京骨": "BL64", "足通谷": "BL65", "至阴": "BL66",

    "合谷": "LI4", "迎香": "LI20", "巨髎": "ST8", "头维": "ST4",
    "气舍": "ST11", "四白": "ST2", "下关": "ST7", "颊车": "ST6",
    "足三里": "ST36", "丰隆": "ST40", "内庭": "ST44", "天枢": "ST25",
    "髀关": "ST31", "伏兔": "ST32", "梁门": "ST21", "归来": "ST29",
    "气冲": "ST30", "厉兑": "ST45", "陷谷": "ST43",

    "涌泉": "KI1", "太溪": "KI3", "照海": "KI6", "复溜": "KI7",
    "然谷": "KI2", "大钟": "KI4", "水泉": "KI5", "交信": "KI8",
    "筑宾": "KI9", "阴谷": "KI10",

    "太冲": "LR3", "三阴交": "SP6", "血海": "SP10", "阴陵泉": "SP9",
    "太白": "SP3", "公孙": "SP4", "商丘": "SP5", "大都": "SP2",
    "漏谷": "SP7", "地机": "SP8", "箕门": "SP11", "冲门": "SP12",

    "神门": "HT7", "少海": "HT3", "通里": "HT5", "灵道": "HT4",
    "少冲": "HT9",

    "后溪": "SI3", "腕骨": "SI4", "肩贞": "SI9", "臑俞": "SI10",
    "天宗": "SI11", "秉风": "SI12", "曲垣": "SI13", "天髎": "SI15",
    "颧髎": "SI18", "听宫": "SI19", "养老": "SI6", "支正": "SI7",
    "阳谷": "SI5", "少泽": "SI1", "前谷": "SI2",

    "外关": "SJ5", "四渎": "SJ9", "支沟": "SJ6", "会宗": "SJ7",
    "天井": "SJ10", "清冷渊": "SJ11", "消泺": "SJ12", "臑会": "SJ13",
    "肩髎": "SJ14", "关冲": "SJ1", "液门": "SJ2", "中渚": "SJ3",
    "阳池": "SJ4",

    "瞳子髎": "GB1", "听会": "GB2", "头窍阴": "GB11", "完骨": "GB12",
    "风池": "GB20", "肩井": "GB21", "渊腋": "GB22", "辄筋": "GB18",
    "丝竹空": "GB23", "日月": "GB24", "环跳": "GB30", "风市": "GB31", "阳陵泉": "GB34",
    "光明": "GB38", "阳交": "GB36", "外丘": "GB37", "悬钟": "GB39",
    "阳辅": "GB44", "侠溪": "GB43", "足临泣": "GB41", "丘墟": "GB40",

    "大椎": "DU14", "腰阳关": "GV3", "至阳": "GV9", "灵台": "GV17",
    "身柱": "GV12", "筋缩": "GV19", "悬枢": "GV13", "中枢": "GV8",
    "哑门": "GV15", "风府": "GV16", "百会": "DU20", "素髎": "DU25",
    "水沟": "GV26", "龈交": "GV28",

    "廉泉": "CV23", "天突": "CV22", "承浆": "CV24", "鸠尾": "CV15",
    "巨阙": "CV14", "阴交": "CV7", "气海": "CV6", "关元": "CV4",
    "中脘": "CV12", "膻中": "CV17",

    "曲池": "LI11", "手三里": "LI10", "列缺": "LU7", "尺泽": "LU5",
    "鱼际": "LU10", "少商": "LU11", "太渊": "LU9", "二间": "LI2",
    "三间": "LI3", "阳溪": "LI5", "偏历": "LI6", "温溜": "LI7",
    "下廉": "LI8", "上廉": "LI9",

    "郄门": "PC4", "间使": "PC5", "内关": "PC6", "大陵": "PC7",
    "劳宫": "PC8", "中冲": "PC9",

    "四神聪": "EX-HN1", "定喘": "EX-B1", "夹脊": "EX-B2",
    "阑尾": "EX-LE7", "胆囊": "EX-LE6", "膝眼": "EX-LE5", "八正": "EX-LE8",
}

# 等价编码体系：两套写法都对，不算错配
# SJ =三焦经WHO 码，TE = 国标现行码
# DU = 督脉旧码，GV = 国标现行码
# EX-B = EX-BL 的旧写法
EQUIV_CODE = {
    "SJ": "TE", "TE": "SJ",   # 三焦经
    "DU": "GV", "GV": "DU",   # 督脉
}


def same_family(a: str, b: str) -> bool:
    """判断两个编码是否属于同一套等价体系。"""
    if not a or not b or len(a) != len(b):
        return False
    pre = a[:2] if a[2:3] == "-" else a[:2]
    pre_b = b[:2] if b[2:3] == "-" else b[:2]
    return EQUIV_CODE.get(pre) == pre_b or EQUIV_CODE.get(pre_b) == pre


def main() -> int:
    f = ROOT / "data" / "acupoints.json"
    data = json.loads(f.read_text(encoding="utf-8"))
    aps = data["acupoints"]

    bad = []
    equiv = []
    for a in aps:
        name, code = a["name"], a.get("code")
        if not code:
            continue
        want = CODE.get(name) or CODE.get(name.replace("（附", "").rstrip("）"))
        if want and code != want:
            # 等价体系（DU/GV、SJ/TE）不算错配
            if same_family(code, want):
                equiv.append((a["id"], name, code, want))
            else:
                bad.append((a["id"], name, code, want))

    print(f"对照表收录 {len(CODE)} 个穴，全库 {len(aps)} 条")
    if not bad:
        print("✅ 未发现编码错配")
    else:
        print(f"❌ 发现 {len(bad)} 处编码错配：")
        for aid, name, got, want in bad:
            print(f"   {aid} {name:12} 现为 {got:10} 应为 {want}")

    if equiv:
        print(f"\nℹ️ {len(equiv)} 处为等价编码体系（DU/GV、SJ/TE），不算错：")
        print("   " + "、".join(f"{n}({g})" for _, n, g, _ in equiv[:10])
              + ("…" if len(equiv) > 10 else ""))

    # 反向：同一 code 被多个不同穴名占用
    seen = {}
    for a in aps:
        c = a.get("code")
        if c:
            seen.setdefault(c, []).append(a["name"])
    dup = {c: v for c, v in seen.items() if len(set(v)) > 1}
    if dup:
        print(f"\n⚠️ 同code 多个穴名：{dup}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
