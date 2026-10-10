"""知源问病 · 逆向检索引擎（病→证→症→方→穴→其他疗法）

与 diagnose.py 是**同一套数据的两个遍历方向**：

  正向（问诊模式）：症 → 四诊采集 → 证 → 方/穴/推拿     站在患者一侧
  逆向（查阅模式）：病 → 证 → 症 → 方 → 穴 → 其他疗法   站在学习者/临床一侧

数据一个字节都没多，区别只是入口和遍历顺序。
逆向模式不做红旗拦截（不是在给具体患者下诊断），但仍保留「必须排除的器质性病变」，
因为查「咳嗽」时必须看到「咯血、消瘦、体重下降要排除肺癌肺结核」。
"""
from __future__ import annotations

import sys
from collections import defaultdict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from .kb import get_kb            # noqa: E402
from .safety import get_safety     # noqa: E402

# ---------------------------------------------------------------- 其他疗法
# 只收录有把握的内容，每条标 verified。缺口在 render 里显式说明，不硬填。
OTHER_THERAPY: list[dict] = [
    {"name": "艾灸法", "category": "温通类",
     "principle": "以艾绒燃烧产生的温热刺激作用于腧穴，温通经络、行气活血、扶阳固本。",
     "indications": ["虚寒证（畏寒肢冷、脘腹冷痛）", "阳虚证（阳痿、宫寒、五更泻）",
                     "慢性虚损性疾病（久咳、久泻、疲劳）", "寒痹（关节冷痛、遇寒加重）",
                     "气血不足（面色少华、易感冒、贫血辅助）"],
     "methods": ["温和灸：艾条距皮肤2–3cm，局部温热不烫，每穴15–20分钟",
                 "悬灸：艾条悬于穴上，灸感以温热为度",
                 "隔姜灸：生姜切片扎孔置穴，上置艾炷，温中散寒力强",
                 "隔盐灸（神阙）：食盐填脐，上置艾炷，温阳固脱，用于虚寒性腹痛腹泻",
                 "隔附子饼灸：附子研末制饼，温阳力强，用于阳虚证，须医师指导"],
     "cautions": ["⚠️实热证、阴虚火旺者禁灸（虚火上炎者灸之更甚，如口疮、咽痛、失眠宜灸涌泉引火归元）",
                  "⚠️面部、大血管处、孕妇腰腹部禁灸",
                  "⚠️施灸中防烫伤：艾条距皮肤不可过近，糖尿病周围神经病变者感觉迟钝，须格外小心",
                  "灸后不立即洗澡、不吹冷风，饮温水",
                  "施灸宜避开空腹、过饱、疲劳、醉酒时"],
     "verified": True},
    {"name": "拔罐法", "category": "泻实类",
     "principle": "以罐吸附于体表，造成局部负压与皮下瘀血，疏通经络、行气活血、消肿止痛。",
     "indications": ["风寒湿痹（关节痛、腰肌劳损）", "肌肉紧张酸痛", "痤疮（背部）",
                     "感冒受寒（背部拔罐）", "局部气血滞滞"],
     "methods": ["走罐：在痛处往返移动，适合大面积肌肉酸痛",
                 "闪罐：罐快速吸拔数次，适合受寒",
                 "留罐：吸附5–10分钟，适合点状痛处",
                 "刺络拔罐：先用三棱针点刺再拔罐，泻热活血（须专业者操作）"],
     "cautions": ["⚠️皮肤破损、炎症、皮肤病处禁拔",
                  "⚠️孕妇腰腹部禁拔",
                  "⚠️大血管处（颈动脉窦、腋动脉、股动脉处）、关节骨突处禁拔",
                  "⚠️发热、极度虚弱、严重贫血、血小板低、正在服抗凝药者禁拔",
                  "罐后皮肤有瘀青属正常，但应逐渐消退；若起大水泡需处理",
                  "空腹、饭后1小时内不宜"],
     "verified": True},
    {"name": "刮痧法", "category": "泻实类",
     "principle": "以刮板在皮肤表面反复刮拭，使局部皮下瘀血外排，疏通经络、祛邪外出。",
     "indications": ["风寒感冒（颈肩背部）", "暑湿（胸腹）", "经络阻滞之酸痛",
                     "头面胀痛（颈项侧）"],
     "methods": ["项背刮：从颈后正中向两侧肩部刮拭，力度以出痧为度",
                 "胸腹刮：沿肋间由内向外",
                 "刮痧板边缘垂直皮肤，短距离反复刮，忌大面积重刮"],
     "cautions": ["⚠️孕妇腰腹部禁刮", "⚠️经期、皮肤破损、急性传染病发热期禁刮",
                  "⚠️刮后不立即洗澡、不吹冷风，喝温水",
                  "⚠️「晕刮」（刮后头晕恶心）立即停止，平卧饮糖水",
                  "⚠️糖尿病、皮肤病、静脉曲张处慎用"],
     "verified": True},
    {"name": "刺络放血（点刺）", "category": "泻热类",
     "principle": "点刺浅表血络挤出少量血液，泻热解毒、活血消肿。",
     "indications": ["咽喉肿痛（少商、耳尖）", "高热（十宣、大椎）", "痤疮（耳尖、肺俞）",
                     "丹毒、疔疮（局部）", "麦粒肿（耳尖）", "急性扁桃体炎"],
     "methods": ["少商点刺：拇指外侧指甲角，点刺出血数滴",
                 "耳尖点刺：耳廓最高点，点刺出血",
                 "十宣点刺：十指尖端，用于高热、昏迷（急救为主）"],
     "cautions": ["⚠️血友病、凝血功能障碍、正在服抗凝药、血小板低者禁",
                  "⚠️孕妇、月经期、贫血者禁",
                  "⚠️仅限浅表部位，不可深刺",
                  "⚠️须由具备资质者操作"],
     "verified": True},
    {"name": "灯火灸", "category": "古法灸",
     "principle": "以灯芯草蘸麻油点燃，速点穴位，灯火灼热刺激，用于古法灸治。",
     "indications": ["小儿疳积", "腮腺炎（灯火灸耳尖/角孙）", "小儿惊风、脐风",
                     "扁桃体炎", "疮疡初起"],
     "methods": ["灯火灸：灯芯草蘸油点燃，对准穴位速点即止，局部发出啪声",
                 "常用穴：角孙、耳尖、印堂、神阙（脐风）、四缝（疳积）"],
     "cautions": ["⚠️必须在家长看护与专业指导下进行",
                  "⚠️面部与婴幼儿皮肤娇嫩，灼伤风险高，务必由专业者操作",
                  "⚠️已列入部分医院的婴幼儿辅助疗法，非家庭自用"],
     "verified": False},
    {"name": "药膳食疗", "category": "食治类",
     "principle": "药食同源。以常用食材的性味归经调养，温和持久，适合慢性调理与病后调养。",
     "indications": ["脾胃虚弱（山药、莲子、小米、南瓜）", "湿重（薏苡仁、赤小豆、冬瓜）",
                     "肺燥咳嗽（百合、银耳、梨、冰糖）", "气血不足（红枣、当归炖鸡、桂圆）",
                     "肝肾不足（枸杞、黑芝麻、桑葚）", "血瘀（山楂、黑木耳）",
                     "肝阳上亢（菊花、决明子代茶）", "失眠（酸枣仁粥、莲子心）"],
     "methods": ["代茶饮：菊花 3g 沸水泡饮（肝阳上亢、高血压辅助）",
                 "山药粥：鲜山药 50g + 小米同煮（脾胃虚弱、儿童厌食）",
                 "薏苡仁赤小豆粥：各 30g 煮粥（湿重、水肿）",
                 "百合银耳羹：百合 15g 银耳 10g 炖（肺燥干咳）",
                 "生姜红枣茶：生姜 3 片 + 红枣 4 枚（寒性腹痛、经期保暖）",
                 "陈皮山楂饮：陈皮 3g 山楂 6g 煮水（食积腹胀）"],
     "cautions": ["⚠️食疗是调理，不治病，不能替代药物与就医",
                  "⚠️药膳也有禁忌：孕妇慎用活血类（山楂大量活血）、阳虚者慎用寒凉（苦瓜、绿茶）",
                  "⚠️糖尿病、肾病、高尿酸者用代茶饮须咨询医师（含糖类）",
                  "⚠️服药期间忌口：服温补药忌生冷萝卜茶；服清热药忌辛辣"],
     "verified": False},
    {"name": "足浴引火下行", "category": "外治类",
     "principle": "温热水泡脚使下肢血流通畅，引火下行、暖足助眠。",
     "indications": ["失眠（尤虚火上炎者）", "手足不温", "头痛头晕（肝阳上亢辅助）",
                     "口疮、咽喉肿痛（虚火所致）"],
     "methods": ["温开水泡脚 15–20 分钟，水温 38–42℃，忌过烫",
                 "可加艾叶、生姜（寒证）或盐（简单版）",
                 "睡前1小时泡，配合揉涌泉"],
     "cautions": ["⚠️水温不宜过高，糖尿病、下肢动脉硬化、感觉障碍者须先测温",
                  "⚠️静脉曲张、皮肤破损、感染者不宜",
                  "⚠️饭后立即不宜泡脚",
                  "⚠️严重心衰、高血压未控者不宜久泡"],
     "verified": True},
    {"name": "功法导引（八段锦）", "category": "导引类",
     "principle": "以特定动作导引气血、通经络。动作柔和，适合慢性病与老人。",
     "indications": ["慢性疲劳", "颈肩腰背慢性痛", "失眠", "高血压辅助（八段锦有证据支持）",
                     "老年人平衡与柔韧"],
     "methods": ["预备式 → 双手托天理三焦 → 左右开弓似射雕 → 调理脾胃须单举",
                 "五劳七伤往后瞧 → 摇头摆尾去心火 → 两手攀足固肾腰 → 攒拳怒目增气力",
                 "背后七颠百病消 → 收功"],
     "cautions": ["⚠️量力而行，出现头晕胸闷立即停止",
                  "⚠️颈椎病急性期、严重骨质疏松者不做「摇头摆尾」与「两手攀足」",
                  "⚠️高血压未控者避免低头与憋气动作",
                  "每次 10–20 分钟，每日 1–2 次，坚持才有效"],
     "verified": False},
]

# 症状 → 同义词（用于「按症反查」，让口语也能命中）
SYNONYMS = {
    "口苦": ["嘴里发苦", "口苦", "嘴苦"],
    "咽干": ["嗓子干", "咽干", "喉咙干", "口干"],
    "不思饮食": ["没胃口", "不想吃", "吃不下", "食欲不振", "厌食"],
    "五更泻": ["黎明泻", "鸡鸣泻", "早上腹泻"],
    "头重如裹": ["头重", "像裹了布", "头沉"],
    "自汗": ["爱出汗", "动不动出汗", "自汗"],
    "盗汗": ["晚上出汗", "睡觉出汗", "盗汗"],
}


class Inverse:
    """逆向检索：按病/症/方/穴反查。"""

    def __init__(self) -> None:
        self.kb = get_kb()
        self.safe = get_safety()
        self._sym_index: dict[str, list[tuple[str, str]]] | None = None

    # ------------------------------------------------------------ 索引
    @property
    def sym_index(self) -> dict[str, list[tuple[str, str]]]:
        """症状 → [(证型id, 证型名)]，含同义词展开。"""
        if self._sym_index is not None:
            return self._sym_index
        idx: dict[str, list[tuple[str, str]]] = defaultdict(list)
        for sx in self.kb.syndromes:
            for w in sx.get("sy", []):
                idx[w].append((sx["id"], sx.get("n", "")))
        for canon, alts in SYNONYMS.items():
            for a in alts:
                if a not in idx:
                    idx[a] = idx.get(canon, [])
        self._sym_index = idx
        return idx

    def _expand(self, text: str) -> list[str]:
        return [text] + SYNONYMS.get(text, [])

    # ------------------------------------------------------------ 入口1：按病查
    def by_disease(self, name: str) -> dict | None:
        kb = self.kb
        matched = [(d, len([k for k in d.get("kw", []) if k in name]))
                   for d in kb.diseases]
        matched = [(d, h) for d, h in matched if h]
        if not matched:
            d = kb.disease(name)
            matched = [(d, 1)] if d else []
        if not matched:
            return None
        d = matched[0][0]
        syns = []
        for sid in d.get("sx", []):
            sx = kb.syndrome(sid)
            if not sx:
                continue
            formulas = []
            for fid in sx.get("fx", []):
                f = kb.formula(fid)
                if not f:
                    continue
                formulas.append({
                    "name": f["name"], "functions": f.get("functions", ""),
                    "herbs": f.get("herbs", ""), "source": f.get("source_text", ""),
                    "cautions": f.get("cautions", []),
                })
            meridian = [{"name": p["name"], "meridian": p.get("meridian", ""),
                         "location": p.get("location", "")}
                        for p in kb.points_meridian(sid)]
            syns.append({
                "id": sid, "name": sx.get("n", ""), "system": sx.get("sys", ""),
                "severity": sx.get("sev", ""), "home_ok": sx.get("home", False),
                "key_symptoms": sx.get("sy", []), "tongue": sx.get("tg", ""),
                "pulse": sx.get("p", ""), "mechanism": sx.get("me", ""),
                "treatment": sx.get("tx", ""),
                "differential": sx.get("df", ""), "warn": sx.get("wn", ""),
                "note": sx.get("nt", ""),
                "formulas": formulas, "acupoints_meridian": meridian,
                "dongshi": kb.points_dongshi(sid),
                "tuina": [{"condition": t["condition"], "level": t["level"],
                           "home": t.get("home_self_help", "")}
                          for t in kb.search_tuina(sx.get("d", ""), k=1)],
            })
        return {
            "disease": d, "syndromes": syns,
            "must_exclude": d.get("ex", []),
            "overview": d.get("ov", ""),
            "common_symptoms": d.get("cs", []),
        }

    # ------------------------------------------------------------ 入口2：按症查
    def by_symptom(self, text: str, k: int = 12) -> dict:
        idx = self.sym_index
        hits: dict[str, dict] = {}
        seen: set[str] = set()
        for w in self._expand(text):
            if w in seen:          # 同义词展开会把原词再带一次，去重否则命中数虚高
                continue
            seen.add(w)
            for sid, name in idx.get(w, []):
                e = hits.setdefault(sid, {"id": sid, "name": name, "match": []})
                e["match"].append(w)
        out = []
        for e in hits.values():
            sx = self.kb.syndrome(e["id"])
            if not sx:
                continue
            e["disease"] = sx.get("d", "")
            e["tongue"] = sx.get("tg", "")
            e["pulse"] = sx.get("p", "")
            e["mechanism"] = sx.get("me", "")
            e["treatment"] = sx.get("tx", "")
            e["hit"] = len(e["match"])
            e["formula"] = ""
            for fid in sx.get("fx", []):
                f = self.kb.formula(fid)
                if f:
                    e["formula"] = f["name"]
                    break
            e["acupoints"] = [p["name"] for p in self.kb.points_meridian(e["id"])[:4]]
            out.append(e)
        out.sort(key=lambda x: (-x["hit"], x["disease"]))
        return {"q": text, "hits": out[:k]}

    # ------------------------------------------------------------ 入口3：按方查
    def by_formula(self, text: str, k: int = 8) -> dict:
        hits = self.kb.search_formula(text, k=k)
        out = []
        for f in hits:
            uses = [sx for sx in self.kb.syndromes if f["id"] in sx.get("fx", [])]
            out.append({
                "formula": f, "used_by": uses,
                "acupoints": sorted({a for sx in uses
                                     for a in [p["name"] for p in self.kb.points_meridian(sx["id"])]}),
            })
        return {"hits": out}

    # ------------------------------------------------------------ 入口4：按穴查
    def by_acupoint(self, text: str, k: int = 10) -> dict:
        """经穴通道与董氏通道分开返回——与正向模式保持同样的隔离。"""
        m = self.kb.search_acupoint(text, k=k)
        d = self.kb.search_dongshi(text, k=k)
        mer = []
        for p in m:
            used = [sx for sx in self.kb.syndromes if p["id"] in sx.get("ac", [])]
            mer.append({"point": p, "used_by": used})
        return {"meridian": mer, "dongshi": d, "lineage": self.kb.dongshi_lineage}


# ---------------------------------------------------------------- 渲染
def render_disease(data: dict) -> str:
    if not data:
        return "库中没有这个病。试试：感冒、咳嗽、头痛、眩晕、不寐、胃痛、泄泻、便秘、腹痛、胁痛、痹证、腰痛、郁证、水肿、消渴、月经不调、咽喉肿痛、口疮、鼻渊、小儿积食、小儿腹泻、小儿夜啼、遗尿"
    d = data["disease"]
    L = [f"# {d['name']}（{d['cat']}）"]
    if data.get("overview"):
        L.append(data["overview"])
    if data.get("common_symptoms"):
        L.append("\n**常见症状**：\n" + "、".join(data["common_symptoms"]))
    L.append(f"\n**本病收录 {len(data['syndromes'])} 个证型**")

    for i, sx in enumerate(data["syndromes"], 1):
        L.append("\n" + "─" * 50)
        L.append(f"## {i}. {sx['name']}（{sx['system']}｜{sx['severity']}）")
        L.append(f"**主症**：{'、'.join(sx['key_symptoms'])}")
        L.append(f"**舌**：{sx['tongue']}　**脉**：{sx['pulse']}")
        L.append(f"**病机**：{sx['mechanism']}")
        L.append(f"**治法**：{sx['treatment']}")
        if sx.get("differential"):
            L.append(f"**鉴别**：{sx['differential']}")
        L.append("\n**方药**")
        for f in sx["formulas"]:
            L.append(f"- **{f['name']}**（{f['source']}）{f['functions']}")
            L.append(f"  - 组成：{f['herbs']}")
            if f["cautions"]:
                L.append(f"  - 注意：{'；'.join(f['cautions'][:3])}")
        L.append("\n**针灸 · 通道一 十四经穴**")
        L.append("、".join(f"{p['name']}（{p['meridian']}）" for p in sx["acupoints_meridian"]))
        dsg = sx["dongshi"]
        L.append(f"\n**针灸 · 通道二 董氏奇穴（{dsg['lineage']} 派）**")
        L.append(f"- 配穴思路：{dsg['hint'] or '（本证型未预设董氏配穴思路）'}")
        if dsg["matches"]:
            L.append(f"- 可考虑：{'、'.join(x['name'] for x in dsg['matches'])}（定位待原书核对）")
        L.append("- ⛔ 定位未录入原书，系统不给定位")
        if sx["tuina"]:
            t = sx["tuina"][0]
            L.append(f"\n**推拿**（{t['level']}）：{t['condition']}")
            if t["home"]:
                L.append(f"- 🏠 家庭可做：{t['home']}")
        if sx.get("warn"):
            L.append(f"\n⚠️ **安全提示**：{sx['warn']}")
        if sx.get("note"):
            L.append(f"ℹ️ {sx['note']}")
        if sx["home_ok"]:
            L.append("✅ 本证型可先做家庭调理")

    if data.get("must_exclude"):
        L.append("\n" + "═" * 50)
        L.append("## ⚠️ 出现以下情况必须先就医，不可只按本病处理")
        for m in data["must_exclude"]:
            L.append(f"- {m}")
    L.append("\n" + "─" * 50)
    L.append("ℹ️ 本页为中医病证知识查阅，不构成处方。处方须经执业中医师复核签字。")
    return "\n".join(L)


def render_symptom(data: dict) -> str:
    hits = data.get("hits", [])
    if not hits:
        return "没有匹配到含该症状的证型。可以换个说法试试，或直接查病名。"
    L = [f"# 症状「{data.get('q', '')}」反查（命中 {len(hits)} 个证型）", ""]
    L.append("⚠️ 同一症状可见于多个病多种证，此处仅为知识对照，**不能据此自诊**。")
    L.append("")
    for e in hits:
        L.append(f"**{e['disease']} · {e['name']}**（匹配 {e['hit']} 项：{'、'.join(e['match'])}）")
        L.append(f"  - 舌脉：{e['tongue']}｜{e['pulse']}")
        L.append(f"  - 病机：{e['mechanism']}")
        L.append(f"  - 治法：{e['treatment']}　方：{e['formula'] or '—'}")
        L.append(f"  - 穴：{'、'.join(e['acupoints'])}\n")
    return "\n".join(L)


def render_formula(data: dict) -> str:
    hits = data.get("hits", [])
    if not hits:
        return "没有匹配到这个方剂。"
    L = ["# 方剂反查（方 → 证 → 症）", ""]
    for h in hits:
        f = h["formula"]
        L.append("═" * 50)
        L.append(f"## {f['name']}（{f.get('source_text','')}）　{f.get('functions','')}")
        L.append(f"**主治**：{f.get('indications','')}")
        L.append(f"**组成**：{f.get('herbs','')}")
        L.append(f"**方义**：{f.get('formula_meaning','')}")
        if f.get("similar_diff"):
            L.append(f"**类方鉴别**：{f['similar_diff']}")
        if f.get("modifications"):
            L.append(f"**加减**：{f['modifications']}")
        if f.get("cautions"):
            L.append(f"**禁忌**：{'；'.join(f['cautions'])}")
        L.append(f"**剂量**：⚠️为教材参考值，须执业医师核定")
        if h["used_by"]:
            L.append(f"\n**本库中用于这些证型**（共 {len(h['used_by'])} 个）：")
            for sx in h["used_by"]:
                L.append(f"- {sx['d']} · {sx['n']}｜主症：{'、'.join(sx.get('sy', [])[:5])}")
        if h["acupoints"]:
            L.append(f"\n**常配穴**：{'、'.join(h['acupoints'][:10])}")
    L.append("\n" + "─" * 50)
    L.append("ℹ️ 知识查阅用，不构成处方。")
    return "\n".join(L)


def render_acupoint(data: dict) -> str:
    L = ["# 穴位反查（穴 → 主治 → 证 → 方）", ""]
    L.append("## 通道一：十四经穴")
    if not data["meridian"]:
        L.append("（无匹配）")
    for m in data["meridian"]:
        p = m["point"]
        L.append("─" * 40)
        L.append(f"### {p['name']}（{p.get('meridian','')}｜{p.get('code','')}）")
        L.append(f"- 定位：{p.get('location','')}")
        L.append(f"- 主治：{'、'.join(p.get('indications', [])[:8])}")
        L.append(f"- 针刺：{p.get('needling','')}｜深度上限：{p.get('depth_limit','')}")
        if p.get("anatomy_note"):
            L.append(f"- 解剖：{p['anatomy_note']}")
        if p.get("contraindication"):
            L.append(f"- ⚠️ 禁忌：{p['contraindication']}")
        if p.get("self_moxa_safe"):
            L.append("- 🟢 适合家庭艾灸/按揉")
        if m["used_by"]:
            L.append(f"- **本库用于这些证型**（{len(m['used_by'])}）：")
            for sx in m["used_by"]:
                fn = ""
                for fid in sx.get("fx", []):
                    f = get_kb().formula(fid)
                    if f:
                        fn = f["name"]
                        break
                L.append(f"  - {sx['d']} · {sx['n']}　方：{fn or '—'}")

    L.append(f"\n## 通道二：董氏奇穴（{data['lineage']} 派）")
    L.append("⚠️ 与上方十四经穴不是同一套体系。")
    if not data["dongshi"]:
        L.append("（无匹配）")
    for p in data["dongshi"]:
        L.append("─" * 40)
        L.append(f"### {p['name']}"
                 + (f"（{p.get('part','')}）" if p.get("part") else ""))
        L.append(f"- 主治方向：{p.get('direction','')}")
        if p.get("use_for"):
            L.append(f"- 适用：{'、'.join(p['use_for'])}")
        L.append(f"- 定位：🔒 未按原书录入，系统不提供（{p.get('lineage','')} 派）")
        if p.get("conflict_note"):
            L.append(f"- ⚠️ 与经穴冲突：{p['conflict_note']}")
    L.append("\n" + "─" * 50)
    L.append("ℹ️ 针刺仅限具备执业资格者。知识查阅用，不构成处方。")
    return "\n".join(L)


def render_therapy() -> str:
    L = ["# 其他疗法（传统中医非药物与非方药方法）", "",
         "本库已有的方药、针灸、推拿之外，以下方法按「传统中医」收录。",
         "**这些是知识查阅，不构成处方。**", ""]
    for t in OTHER_THERAPY:
        L.append("═" * 50)
        L.append(f"## {t['name']}（{t['category']}）")
        L.append(f"**原理**：{t['principle']}")
        L.append(f"**适用**：{'、'.join(t['indications'])}")
        L.append("**操作**：")
        for m in t["methods"]:
            L.append(f"- {m}")
        L.append("**注意**：")
        for c in t["cautions"]:
            L.append(f"- {c}")
        if not t.get("verified"):
            L.append("- ℹ️ 本条待对照教材核对")
    return "\n".join(L)


if __name__ == "__main__":
    inv = Inverse()
    from engine.kb import get_kb as _kb
    print("=" * 58)
    print("逆向模式可用入口：")
    print("=" * 58)
    d = inv.by_disease("咳嗽")
    if d:
        print(f"\n【按病查】{d['disease']['name']} → {len(d['syndromes'])} 个证型")
        for sx in d["syndromes"]:
            fn = sx["formulas"][0]["name"] if sx["formulas"] else "—"
            print(f"  {sx['name']:<18} 主症：{'、'.join(sx['key_symptoms'][:4])}")
            print(f"  {'':<18} 方：{fn}｜穴：{'、'.join(p['name'] for p in sx['acupoints_meridian'][:4])}")
    print("\n【按症查】口苦 →")
    r = inv.by_symptom("口苦", k=4)
    for e in r["hits"]:
        print(f"  {e['disease']} · {e['name']}（{e['hit']}项）方：{e['formula']}")
    print("\n【按方查】逍遥散 →")
    f = inv.by_formula("逍遥散", k=1)
    if f["hits"]:
        h = f["hits"][0]
        print(f"  {h['formula']['name']}：本库用于 {len(h['used_by'])} 个证型")
        for sx in h["used_by"][:4]:
            print(f"    - {sx['d']} · {sx['n']}")
    print("\n【按穴查】太冲 →")
    a = inv.by_acupoint("太冲")
    print(f"  经穴通道 {len(a['meridian'])} 条｜董氏通道 {len(a['dongshi'])} 条（分开）")
    print(f"\n【其他疗法】{len(OTHER_THERAPY)} 种：{'、'.join(t['name'] for t in OTHER_THERAPY)}")
