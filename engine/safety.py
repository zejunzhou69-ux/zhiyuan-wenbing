"""知源问病 · 安全层

独立于模型。模型说什么都拦不住这里。
命中急症红旗 → 中止辨证，只给急诊指引；命中必转诊 → 正常辨证但强制附上转诊项。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DATA = Path(__file__).resolve().parent.parent / "data"

# 西药关键词 -> 风险提示
WESTERN_DRUG_RISK = {
    "华法林": ["活血化瘀类中药（丹参、当归、川芎、红花、桃仁）会显著增加出血风险，须查 INR 调整"],
    "利伐沙班": ["与抗血小板药同用时活血药出血风险显著升高"],
    "阿司匹林": ["与活血化瘀药同用增加出血风险"],
    "氯吡格雷": ["与活血化瘀药同用增加出血风险"],
    "二甲双胍": ["须监测血糖，中药不可替代降糖药"],
    "胰岛素": ["须监测血糖，不可自行加减量"],
    "降压药": ["含麻黄制剂（麻黄、桂枝类）可能升高血压与心率，反向抵消降压效果"],
    "地高辛": ["⚠️甘草大量长期用可致低钾，地高辛与低钾并用易致洋地黄中毒（心律失常）"],
    "利尿剂": ["⚠️甘草与利尿剂并用致低钾、水肿、血压异常"],
    "胺碘酮": ["存在相互作用，须咨询心内科与药师"],
    "激素": ["长期使用致骨质疏松，推拿禁暴力手法"],
    "抗抑郁药": ["酸枣仁、柏子仁、远志等安神药可能叠加镇静，须防嗜睡"],
    "镇静催眠药": ["与安神药叠加可致过度镇静"],
    "他汀": ["何首乌、女贞子等有肝损伤报告，须监测肝功能"],
    "化疗药": ["与化疗相互作用复杂，须咨询肿瘤科，禁止自行服用"],
}


def re_split(s: str) -> list[str]:
    for ch in "（）()、/，,":
        s = s.replace(ch, " ")
    return [x for x in s.split() if x]


# ---------------------------------------------------------------- 十八反 / 十九畏
# 写成显式配对表，不再从 redflags.json 的自然语言描述里 split。
# 原实现用 "甘草反海藻" 这种串去 split，实际切不开（整串是一个词），
# 导致十八反检测**完全失效**——既漏报也不会误报，看起来"没问题"是假象。
# 别名组处理炮制品：制川乌/附子与川乌同物，炙甘草与甘草同物。
_ANTI_ALIAS: dict[str, list[str]] = {
    "甘草": ["甘草", "炙甘草", "生甘草", "粉甘草", "甘草梢"],
    "海藻": ["海藻"],
    "甘遂": ["甘遂", "醋甘遂"],
    "大戟": ["大戟", "京大戟", "红大戟", "醋大戟"],
    "芫花": ["芫花", "醋芫花"],
    "乌头": ["乌头", "川乌", "制川乌", "生川乌", "草乌", "制草乌", "附子", "黑顺片",
             "白附片", "淡附片", "炮附片", "附片"],
    "半夏": ["半夏", "法半夏", "姜半夏", "清半夏", "生半夏"],
    "瓜蒌": ["瓜蒌", "全瓜蒌", "瓜蒌皮", "瓜蒌仁", "天花粉"],
    "贝母": ["川贝母", "浙贝母", "平贝母", "贝母", "土贝母"],
    "白蔹": ["白蔹"],
    "白及": ["白及", "白及粉"],
    "藜芦": ["藜芦"],
    "人参": ["人参", "生晒参", "红参", "白参", "人参须"],
    "沙参": ["南沙参", "北沙参", "沙参"],
    "丹参": ["丹参"],
    "玄参": ["玄参"],
    "苦参": ["苦参"],
    "细辛": ["细辛"],
    "芍药": ["白芍", "赤芍", "炒白芍", "酒白芍", "白芍炭", "赤芍炭"],
    # 十九畏
    "硫黄": ["硫黄"],
    "朴硝": ["朴硝", "芒硝", "玄明粉", "牙硝"],
    "水银": ["水银"],
    "砒霜": ["砒霜", "砒石"],
    "狼毒": ["狼毒"],
    "密陀僧": ["密陀僧"],
    "巴豆": ["巴豆", "巴豆霜"],
    "牵牛": ["牵牛子", "黑丑", "白丑", "牵牛"],
    "丁香": ["丁香", "公丁香", "母丁香"],
    "郁金": ["郁金"],
    "犀角": ["犀角", "水牛角"],
    "三棱": ["三棱", "醋三棱", "荆三棱"],
    "官桂": ["肉桂", "桂皮", "官桂"],
    "赤石脂": ["赤石脂", "煅赤石脂"],
    "五灵脂": ["五灵脂", "醋五灵脂"],
}

ANTI_18 = [("甘草", "海藻"), ("甘草", "甘遂"), ("甘草", "大戟"), ("甘草", "芫花"),
           ("乌头", "半夏"), ("乌头", "瓜蒌"), ("乌头", "贝母"), ("乌头", "白蔹"), ("乌头", "白及"),
           ("藜芦", "人参"), ("藜芦", "沙参"), ("藜芦", "丹参"), ("藜芦", "玄参"),
           ("藜芦", "苦参"), ("藜芦", "细辛"), ("藜芦", "芍药")]

ANTI_19 = [("硫黄", "朴硝"), ("水银", "砒霜"), ("狼毒", "密陀僧"), ("巴豆", "牵牛"),
           ("丁香", "郁金"), ("乌头", "犀角"), ("朴硝", "三棱"), ("官桂", "赤石脂"),
           ("人参", "五灵脂")]

# 煎服法与炮制说明词，不能当成药名
_NOT_HERB = {"先煎", "后下", "包煎", "另煎", "烊化", "冲服", "研末", "吞服", "水煎",
             "各", "等分", "分", "酒", "醋", "姜", "蜜", "米", "朱砂为衣", "为衣"}


def extract_herb_names(herbs_str: str) -> list[str]:
    """从「麻黄9g 桂枝9g 杏仁9g 炙甘草3g」这类组成串里提取药名。

    去掉剂量数字、括注、煎法词。返回的是**原文出现过的药名**，
    后续与别名组比对时能正确识别炮制品。
    """
    import re as _re
    s = herbs_str.replace("（", " ").replace("）", " ").replace("，", " ").replace("、", " ")
    out: list[str] = []
    for tok in s.split():
        tok = tok.strip()
        if not tok:
            continue
        name = _re.sub(r"[×xX].*$", "", tok)
        name = _re.sub(r"[\d.]+\s*[gGgMm克]*$", "", name)
        name = name.strip()
        if not name or name in _NOT_HERB:
            continue
        if any(ch.isdigit() for ch in name):
            continue
        out.append(name)
    return out


def _matched_groups(herb_names: list[str]) -> set[str]:
    """判断方中有哪些别名组（含炮制品匹配）。"""
    hit = set()
    for group, names in _ANTI_ALIAS.items():
        if any(n in herb_names for n in names):
            hit.add(group)
    return hit


def check_anticonflict(herb_names: list[str]) -> list[str]:
    """检查十八反与十九畏，返回告警。"""
    hit = _matched_groups(herb_names)
    out: list[str] = []

    def real(a: str) -> str:
        for n in _ANTI_ALIAS[a]:
            if n in herb_names:
                return n
        return a

    for a, b in ANTI_18:
        if a in hit and b in hit:
            out.append(f"⚠️⚠️【十八反】本方含「{real(a)}」与「{real(b)}」，属十八反配伍禁忌，须医师复核后方可使用")
    for a, b in ANTI_19:
        if a in hit and b in hit:
            out.append(f"⚠️【十九畏】本方含「{real(a)}」与「{real(b)}」，属十九畏，须医师复核")
    return out


class Safety:
    def __init__(self, data_dir: Path | None = None) -> None:
        p = (data_dir or DATA) / "redflags.json"
        d = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
        self.meta = d.get("_meta", {})
        self.emergency = d.get("emergency", [])
        self.must_refer = d.get("must_refer", [])
        self.special = d.get("special_populations", {})
        self.drug_rules = d.get("drug_safety_rules", [])
        self.needling_safety = d.get("needling_safety", [])

    # ------------------------------------------------------------ 急症扫描
    def scan(self, text: str) -> list[dict]:
        if not text:
            return []
        hits = []
        for e in self.emergency:
            hit = [k for k in e.get("kw", []) if k in text]
            if hit:
                hits.append({**e, "hit": hit})
        return hits

    def emergency_block(self, text: str, profile: dict | None = None) -> dict | None:
        """返回最高危的一组红旗；无命中返回 None。

        优先级：E06 疑似中风（最易被误当面瘫而延误）→ E15 自伤 → 其余按致命性排。
        另有一条硬规则：**孕期的任何腹痛都直接按孕产急症处理**，不做关键词匹配，
        因为异位妊娠破裂是以腹痛为主诉的，漏掉的代价是致命的。
        """
        profile = profile or {}

        # 硬规则：孕腹 = 孕产急症
        # 匹配腹部疼痛，不含泛用词"疼"——否则孕妇牙疼/头疼/咽疼全被拉去产科急诊
        if profile.get("pregnant") and any(k in text for k in
                                        ["腹痛", "肚子痛", "肚子疼", "小腹痛", "下腹痛",
                                         "小肚子疼", "坠痛", "腹部痛", "上腹痛", "胃脘痛"]):
            return {**next(e for e in self.emergency if e["id"] == "E12"),
                    "hit": ["孕期腹痛（硬规则拦截）"]}

        # 硬规则：婴幼儿精神状态改变
        age = profile.get("age")
        if isinstance(age, (int, float)) and age < 1 and any(
                k in text for k in ["嗜睡", "叫不醒", "拒奶", "哭声尖", "囟门"]):
            return {**next(e for e in self.emergency if e["id"] == "E11"),
                    "hit": ["婴儿精神状态改变（硬规则拦截）"]}

        hits = self.scan(text)
        if not hits:
            return None
        for must in ("E06", "E15", "E01", "E12", "E08", "E07", "E11",
                     "E05", "E04", "E02", "E03", "E14", "E13", "E10", "E09"):
            for h in hits:
                if h["id"] == must:
                    return h
        return hits[0]

    # ------------------------------------------------------------ 必转诊扫描
    def refer_flags(self, text: str) -> list[dict]:
        hits = []
        for r in self.must_refer:
            hit = [i for i in r.get("items", []) if i in text]
            if hit:
                hits.append({**r, "hit": hit})
        return hits

    # ------------------------------------------------------------ 人群筛查
    def screen_profile(self, profile: dict) -> dict:
        out: dict = {"bans": [], "cautions": [], "must_ask": []}
        age = profile.get("age")
        if profile.get("pregnant"):
            pg = self.special.get("pregnancy", {})
            out["bans"] += pg.get("drug_absolutely_ban", [])
            out["bans"] += pg.get("acupoint_ban_needle", [])
            out["bans"] += ["腹部与腰骶部推拿按摩"]
            out["cautions"] += pg.get("drug_caution", [])
        if profile.get("breastfeeding"):
            out["bans"] += ["回乳药（麦芽、大量山楂）"]
        if isinstance(age, (int, float)):
            if age < 1:
                out["bans"] += self.special.get("infant", {}).get("massage_ban", [])
                out["must_ask"].append("是否高热、拒奶、精神状态、尿量")
            elif age < 6:
                out["must_ask"].append("⚠️6个月以下婴儿发热属急诊指征")
            elif age >= 70:
                out["bans"] += self.special.get("elderly", {}).get("avoid", [])
                out["must_ask"].append("是否有骨质疏松、近期跌倒、新发疼痛")
        if profile.get("liver_kidney"):
            lk = self.special.get("liver_kidney_impairment", {})
            out["cautions"] += [lk.get("note", "")]
            out["must_ask"] += lk.get("must_ask", [])
        for med in profile.get("medications", []) or []:
            for key, risks in WESTERN_DRUG_RISK.items():
                if key in str(med):
                    out["cautions"] += risks
                    out["must_ask"].append(f"正在服用{key}，是否已告知开方医师")
        out["bans"] = sorted(set(out["bans"]))
        out["cautions"] = sorted(set(x for x in out["cautions"] if x))
        return out

    # ------------------------------------------------------------ 方剂安全核对
    def check_formula(self, formula: dict, profile: dict | None = None) -> list[str]:
        warns: list[str] = []
        profile = profile or {}
        herbs_str = str(formula.get("herbs", ""))
        cautions = str(formula.get("cautions", ""))

        if profile.get("pregnant"):
            pg = self.special.get("pregnancy", {})
            hit_b = [h for h in pg.get("drug_absolutely_ban", []) if h in herbs_str]
            hit_c = [h for h in pg.get("drug_caution", []) if h in herbs_str]
            hit_p = [h for h in pg.get("acupoint_ban_needle", []) if h in herbs_str]
            if hit_b:
                warns.append(f"⚠️⚠️【妊娠禁用】本方含绝对禁用药 {'、'.join(hit_b)} —— 孕妇禁用，须换方")
            if hit_c:
                warns.append(f"⚠️【妊娠慎用】本方含慎用药 {'、'.join(hit_c)} —— 须医师评估")
            if hit_p:
                warns.append(f"⚠️【配伍与取穴禁忌】涉及 {'、'.join(hit_p)}")

        # 十八反 / 十九畏：用显式配对表 + 炮制品别名，见 check_anticonflict
        herb_names = extract_herb_names(herbs_str)
        warns.extend(check_anticonflict(herb_names))

        if cautions:
            warns.append(f"【原方注意】{cautions}")
        warns.append("【剂量核定】上方剂量为教材参考值，须经执业医师按体质、病情、剂量习惯核定后方可使用。")
        deco = self.decoction_notes(herbs_str)
        if deco:
            warns.append("【煎服法】" + "；".join(deco))
        return warns

    def herb_toxicity(self, herb_names: list[str], kb) -> list[str]:
        out = []
        for hn in herb_names:
            h = kb.herb_by_name(hn)
            if h and h.get("toxicity") and "无毒" not in h["toxicity"]:
                ci = "；".join(h.get("contraindications", []))[:90]
                out.append(f"⚠️【{hn}】{h['toxicity']}｜常用量 {h.get('dosage','')}｜禁忌：{ci}")
        return out

    def decoction_notes(self, herbs_str: str) -> list[str]:
        notes = []
        for kw, how in [("石膏", "生石膏先煎"), ("牡蛎", "牡蛎先煎"), ("龙骨", "龙骨先煎"),
                        ("附子", "附子先煎久煎30–60分钟以上"), ("川乌", "川乌先煎久煎1–2小时"),
                        ("草乌", "草乌先煎久煎1–2小时"), ("薄荷", "薄荷后下"),
                        ("钩藤", "钩藤后下（超20分钟失效）"),
                        ("砂仁", "砂仁后下"), ("豆蔻", "豆蔻后下"), ("沉香", "沉香后下"),
                        ("车前子", "车前子包煎"), ("旋覆花", "旋覆花包煎"), ("人参", "人参另煎兑服")]:
            if kw in herbs_str:
                notes.append(how)
        return notes


_S: Safety | None = None


def get_safety() -> Safety:
    global _S
    if _S is None:
        _S = Safety()
    return _S


if __name__ == "__main__":
    s = get_safety()
    for t in ["我胸口压着疼还出汗", "嘴歪了说话不清，右手没劲", "孩子发烧到39度还抽搐",
              "我这两天拉肚子", "怀孕5周有点肚子疼"]:
        blk = s.emergency_block(t)
        print(f"\n【{t}】")
        print("  急诊拦截：" + (f"{blk['id']} {blk['cat']}" if blk else "无"))
        rf = s.refer_flags(t)
        print("  必转诊：" + ("；".join(f"{x['cat']}{x['hit']}" for x in rf) if rf else "无"))
    print("\n人群筛查（孕妇 + 服华法林）：")
    for c in s.screen_profile({"pregnant": True, "medications": ["华法林 2.5mg"]})["cautions"][:8]:
        print("  -", c)