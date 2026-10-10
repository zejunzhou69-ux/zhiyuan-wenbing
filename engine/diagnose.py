"""知源问病 · 四诊采集与辨证引擎

设计原则
1. 无模型也能跑：全部逻辑基于规则与结构化数据，配 LLM 只是增强表达，不是前提。
2. 证据不足不下结论：只采到部分信息时，输出候选证型 + 还缺什么，不硬给一个证。
3. 双通道输出：治疗方案里经穴与董氏奇穴是两个独立字段，永不合并成一张配穴表。
"""
from __future__ import annotations

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from .kb import get_kb
from .safety import get_safety, extract_herb_names

# 采集问卷：顺序按「十问歌 + 望闻切」。q 是给用户看的口语化问法，不许用专业术语问用户。
QUESTIONS: list[dict] = [
    {"key": "chief", "stage": "问", "q": "最不舒服的地方是哪里？什么时候开始的？",
     "why": "定病种与病位"},
    {"key": "cold_heat", "stage": "问", "q": "怕冷还是怕热？手脚是凉还是热？",
     "why": "八纲定寒热"},
    {"key": "sweat", "stage": "问", "q": "出汗吗？是自汗（不动也出）、盗汗（睡着才出）、还是刚才发热出的汗？",
     "why": "定表虚、阴虚、气虚"},
    {"key": "head_body", "stage": "问", "q": "头和身上哪里疼？（后脑、太阳穴、头重、关节、腰…）是一阵一阵还是一直疼？",
     "why": "经络辨证"},
    {"key": "stool", "stage": "问", "q": "大便怎么样？一天几次、成形还是稀、什么颜色、有没有带血？",
     "why": "脾与大肠"},
    {"key": "urine", "stage": "问", "q": "小便怎么样？次数多不多、颜色黄不黄、有没有泡沫？夜里起来几次？",
     "why": "肾与膀胱、津液"},
    {"key": "diet", "stage": "问", "q": "胃口怎么样？吃冷的是舒服还是难受？有没有反酸、嗳气、恶心？",
     "why": "脾胃寒热"},
    {"key": "chest_abdomen", "stage": "问", "q": "胸口和肚子有没有胀痛、堵闷？按着疼还是不按也疼？",
     "why": "气机与心"},
    {"key": "sleep", "stage": "问", "q": "睡觉怎么样？入睡难还是容易醒、多梦还是整夜不睡？",
     "why": "心神与阴血"},
    {"key": "emotion", "stage": "问", "q": "心情怎么样？有没有烦、闷、爱叹气、压力大？情绪会影响症状吗？",
     "why": "肝郁"},
    {"key": "voice", "stage": "闻", "q": "说话声音有力还是懒洋洋？咳嗽吗、痰多不多、什么颜色？",
     "why": "闻诊与肺"},
    {"key": "tongue", "stage": "望", "q": "请对着镜子看舌头：舌色（淡白/正常/红/深红）、舌苔（薄白/白厚/黄/黄厚/没苔）、有没有裂纹和齿痕。拍照发我也行。",
     "why": "望诊核心"},
    {"key": "pulse", "stage": "切", "q": "脉象我这里摸不到，只能请你描述：手腕脉搏跳得快还是慢？轻按摸得到（浮）还是要用力按才摸到（沉）？有力还是无力？",
     "why": "切诊（远程不可得，只能间接描述）"},
    {"key": "history", "stage": "问", "q": "以前得过什么病？现在在吃什么药（中西药都算）？有没有手术或外伤？",
     "why": "兼证与用药安全"},
    {"key": "female", "stage": "问", "q": "月经怎么样？周期准不准、经量多少、有无痛经和血块？带下正常吗？",
     "why": "妇女经带胎产", "only": "female"},
]

CORE_KEYS = ["chief", "cold_heat", "stool", "urine", "diet", "sleep", "tongue"]

# 字段识别关键词。顺序即优先级：越靠前越具体。
# 例：「舌淡红苔薄白」要归到 tongue 而不是 head_body（都含「头」类字）。
FIELD_KEYWORDS: dict[str, list[str]] = {
    "tongue": ["舌", "苔"],
    "pulse": ["脉", "浮", "沉"],
    "sweat": ["汗"],
    "urine": ["小便", "尿"],
    "stool": ["大便", "拉", "便", "屎"],
    "sleep": ["睡", "失眠", "多梦"],
    "emotion": ["心情", "情绪", "烦", "闷", "压力", "焦虑", "抑郁"],
    "voice": ["声音", "说话", "咳", "痰"],
    "female": ["月经", "经期", "痛经", "带下", "例假"],
    "diet": ["胃口", "吃", "饭", "饮食", "不想吃"],
    "chest_abdomen": ["胸口", "心口", "胸闷", "腹胀", "肚子胀", "胀痛"],
    "history": ["以前", "病史", "吃药", "手术", "外伤", "过敏", "住院"],
    "cold_heat": ["怕冷", "怕热", "手脚", "冷", "热", "凉", "不渴", "口渴", "畏寒"],
    "head_body": ["头", "脑", "太阳穴", "疼", "痛", "腰", "关节", "身"],
}


def infer_field(text: str, profile: dict | None = None) -> str | None:
    """从用户的口语回答里判断它在回答哪个问题。

    没有命中任何字段时返回 None（当主诉处理）。
    """
    profile = profile or {}
    best, best_n = None, 0
    for key, kws in FIELD_KEYWORDS.items():
        if key == "female" and profile.get("sex") != "female":
            continue
        n = sum(1 for w in kws if w in text)
        if n > best_n:
            best, best_n = key, n
    return best


def applicable(qs: list[dict], profile: dict) -> list[dict]:
    return [q for q in qs if not (q.get("only") == "female" and profile.get("sex") != "female")]


class FourDiagSession:
    """四诊采集状态机。每轮只问 1–2 问，避免把用户问烦。"""

    def __init__(self, profile: dict | None = None) -> None:
        self.profile = profile or {}
        self.collected: dict[str, str] = {}

    def completeness(self) -> dict:
        qs = applicable(QUESTIONS, self.profile)
        total = len(qs)
        done = sum(1 for q in qs if q["key"] in self.collected)
        missing = [q for q in qs if q["key"] not in self.collected]
        return {
            "done": done, "total": total,
            "percent": round(done / total * 100) if total else 0,
            "missing": missing,
            "core_missing": [q["key"] for q in missing if q["key"] in CORE_KEYS],
            "ready": done >= int(total * 0.6),
        }

    def next_questions(self, n: int = 2) -> list[dict]:
        pending = [q for q in applicable(QUESTIONS, self.profile) if q["key"] not in self.collected]
        pending.sort(key=lambda q: 0 if q["key"] in CORE_KEYS else 1)
        return pending[:n]

    def record(self, key: str, value: str) -> None:
        self.collected[key] = value

    def text(self) -> str:
        return " ".join(f"{k} {v}" for k, v in self.collected.items())

    def stages_done(self) -> dict:
        got = {q["stage"] for q in applicable(QUESTIONS, self.profile) if q["key"] in self.collected}
        return {s: (s in got) for s in ("望", "闻", "问", "切")}


def infer_eight_principles(text: str) -> dict:
    """从采集文本推断八纲。定不出的写「待补」，不硬填。"""
    t = text
    r = {"表里": "待补", "寒热": "待补", "虚实": "待补", "阴阳": "待补"}

    if any(k in t for k in ["怕冷", "恶寒", "喜热", "不渴", "舌淡"]):
        r["寒热"] = "寒"
    if any(k in t for k in ["发热", "怕热", "口渴", "喜冷", "舌红", "便干", "便秘"]):
        r["寒热"] = "热" if r["寒热"] == "待补" else "寒热错杂"

    if any(k in t for k in ["乏力", "气短", "自汗", "盗汗", "舌淡", "脉弱", "脉细", "神疲"]):
        r["虚实"] = "虚"
    if any(k in t for k in ["腹胀", "胀痛", "拒按", "痰多", "苔厚腻", "便秘"]):
        r["虚实"] = "实" if r["虚实"] == "待补" else "虚实夹杂"

    if any(k in t for k in ["感冒", "着凉", "受凉"]):
        r["表里"] = "表"
    if any(k in t for k in ["久", "长期", "反复", "多年", "老毛病"]):
        r["表里"] = "里"

    if r["寒热"] == "寒" and r["虚实"] == "虚":
        r["阴阳"] = "阴证"
    elif r["寒热"] == "热" and r["虚实"] == "实":
        r["阴阳"] = "阳证"
    return r


def rank_syndromes(session: FourDiagSession, disease_name: str | None = None) -> list[dict]:
    """按已采集信息给证型打分。分数低说明信息不足，不能当结论用。"""
    kb = get_kb()
    text = session.text()
    out = []
    for s in kb.syndromes:
        if disease_name and s.get("d") != disease_name:
            continue
        hits = [w for w in s.get("sy", []) if w and w in text]
        score = len(hits) * 2 + (1 if disease_name and s.get("d") == disease_name else 0)
        out.append({**s, "hit": hits, "score": score})
    out.sort(key=lambda x: -x["score"])
    return out


def confidence_of(sx: dict, session: FourDiagSession) -> tuple[str, str]:
    c = session.completeness()
    n = len(sx.get("hit", []))
    if n >= 4 and c["percent"] >= 75:
        return "高", ""
    if n >= 3 or c["percent"] >= 60:
        return "中", f"尚缺核心项：{'、'.join(c['core_missing'])}"
    if n >= 1:
        return "低", f"证据太少，只匹配到 {n} 项；还缺：{'、'.join(q['key'] for q in c['missing'][:5])}"
    return "低", "尚无可用证据，无法定证"


def build_plan(sx_id: str, session: FourDiagSession, profile: dict | None = None) -> dict:
    """生成完整治疗方案。

    acupoint_meridian 与 dongshi_channel 是两个独立字段，调用方必须分两段渲染。
    这是「经穴与董氏奇穴分开」的实现点。
    """
    kb, safe = get_kb(), get_safety()
    profile = profile or {}
    sx = kb.syndrome(sx_id)
    if not sx:
        return {"error": f"未找到证型 {sx_id}"}

    formulas = []
    for fid in sx.get("fx", []):
        f = kb.formula(fid)
        if not f:
            continue
        herb_names = extract_herb_names(str(f.get("herbs", "")))
        formulas.append({
            "name": f["name"], "source": f.get("source_text", ""),
            "functions": f.get("functions", ""), "indications": f.get("indications", ""),
            "herbs": f.get("herbs", ""), "meaning": f.get("formula_meaning", ""),
            "similar_diff": f.get("similar_diff", ""), "modifications": f.get("modifications", ""),
            "verified": f.get("verified", False),
            "warnings": safe.check_formula(f, profile),
            "toxicity": safe.herb_toxicity(herb_names, kb),
        })

    meridian = [{
        "name": p["name"], "meridian": p.get("meridian", ""),
        "location": p.get("location", ""), "depth": p.get("depth_limit", ""),
        "indications": p.get("indications", [])[:4],
        "needling": p.get("needling", ""), "contra": p.get("contraindication", ""),
        "self_moxa": p.get("self_moxa_safe", False),
        "anatomy": p.get("anatomy_note", ""), "channel": "meridian",
    } for p in kb.points_meridian(sx_id)]

    screen = safe.screen_profile(profile)
    return {
        "syndrome": {"id": sx_id, "name": sx.get("n", ""), "disease": sx.get("d", ""),
                     "system": sx.get("sys", ""), "mechanism": sx.get("me", ""),
                     "treatment": sx.get("tx", ""), "tongue": sx.get("tg", ""),
                     "pulse": sx.get("p", ""), "key_symptoms": sx.get("sy", []),
                     "home_ok": sx.get("home", False), "severity": sx.get("sev", "")},
        "confidence": confidence_of(sx, session),
        "eight": infer_eight_principles(session.text()),
        "formulas": formulas,
        "acupoint_meridian": meridian,
        "dongshi_channel": kb.points_dongshi(sx_id),
        "tuina": kb.search_tuina(sx.get("d", ""), k=2),
        "safety": {"bans": screen["bans"], "cautions": screen["cautions"],
                   "must_ask": screen["must_ask"],
                   "refer": safe.refer_flags(session.text()),
                   "needling_global": safe.needling_safety},
        "warnings": [w for w in (sx.get("wn", ""), sx.get("nt", "")) if w],
    }


def render_plan(plan: dict) -> str:
    """渲染成文本。经穴与董氏分段输出，不混排。"""
    if plan.get("error"):
        return plan["error"]
    s = plan["syndrome"]
    L: list[str] = []
    lvl, why = plan["confidence"]
    L.append(f"【证型】{s['disease']} · {s['name']}（{s['system']}）｜置信度：{lvl}")
    if why:
        L.append(f"  └─ {why}")
    L.append(f"【八纲】{plan['eight']}")
    L.append(f"【病机】{s['mechanism']}")
    L.append(f"【治法】{s['treatment']}")
    L.append(f"【舌脉】{s['tongue']}｜{s['pulse']}")

    if plan["formulas"]:
        L.append("\n【方药】")
        for f in plan["formulas"]:
            tag = "" if f["verified"] else "（组成待核对教材）"
            L.append(f"· {f['name']}{tag}　{f['functions']}")
            L.append(f"  出处：{f['source']}")
            L.append(f"  主治：{f['indications']}")
            L.append(f"  组成：{f['herbs']}")
            L.append(f"  方义：{f['meaning']}")
            if f["similar_diff"]:
                L.append(f"  类方鉴别：{f['similar_diff']}")
            for w in f["warnings"]:
                L.append(f"  {w}")
            for w in f["toxicity"]:
                L.append(f"  {w}")

    L.append("\n【针灸 · 通道一：十四经穴】")
    for p in plan["acupoint_meridian"]:
        L.append(f"· {p['name']}（{p['meridian']}）")
        L.append(f"  定位：{p['location']}")
        L.append(f"  主治：{'、'.join(p['indications'])}")
        L.append(f"  针刺：{p['needling']}｜深度上限：{p['depth']}")
        if p["anatomy"]:
            L.append(f"  解剖：{p['anatomy']}")
        if p["contra"]:
            L.append(f"  ⚠️禁忌：{p['contra']}")
        if p["self_moxa"]:
            L.append("  🟢 此穴适合家庭艾灸/按揉（针刺仍须专业者）")

    d = plan["dongshi_channel"]
    L.append(f"\n【针灸 · 通道二：董氏奇穴（{d['lineage']} 派）】")
    L.append("  ⚠️以上十四经穴与下方董氏奇穴不是同一套体系，请分开理解，不可混为一表。")
    if d["hint"]:
        L.append(f"  配穴思路：{d['hint']}")
    if d["matches"]:
        L.append("  可考虑穴（按主治方向匹配）：" +
                 "、".join(f"{m['name']}（{m['direction']}）" for m in d["matches"]))
    L.append(f"  已有定位可输出：{'、'.join(d['location_ready']) or '（无）'}")
    L.append(f"  🔒 {d['note']}")
    L.append("  ⛔ 定位未经原书核对，系统不输出董氏奇穴的定位与针刺深度。")

    if plan["tuina"]:
        L.append("\n【推拿】")
        for t in plan["tuina"]:
            L.append(f"· {t['condition']}（{t['syndrome_pattern']}）等级 {t['level']}")
            L.append(f"  首步：{t['steps'][0]}")
            if t.get("home_self_help"):
                L.append(f"  🏠 家庭可做：{t['home_self_help']}")
            L.append(f"  疗程：{t['course']}")
            if t.get("cautions"):
                L.append(f"  注意：{'；'.join(t['cautions'])}")

    if plan["warnings"]:
        L.append("\n【本证型安全提示】")
        for w in plan["warnings"]:
            L.append(f"  {w}")

    sa = plan["safety"]
    if sa["bans"]:
        L.append("\n【禁用（针对你的情况）】")
        for b in sa["bans"]:
            L.append(f"  ⛔ {b}")
    if sa["cautions"]:
        L.append("\n【注意】")
        for c in sa["cautions"]:
            L.append(f"  ⚠️ {c}")
    if sa["refer"]:
        L.append("\n【必须先排查的器质性病变】")
        for r in sa["refer"]:
            L.append(f"  ⚠️ {r['cat']}：命中「{'、'.join(r['hit'])}」—— {r['why']}；{r['action']}")

    L.append("\n【免责】以上为中医辨证思路与健康建议，不构成处方，不能替代执业医师面诊。"
             "用药前须经执业中医师复核签字。")
    return "\n".join(L)


if __name__ == "__main__":
    prof = {"sex": "female", "age": 32}
    sess = FourDiagSession(prof)
    sess.record("chief", "头痛三天")
    sess.record("cold_heat", "后脑疼，怕风，无汗")
    sess.record("tongue", "舌苔薄白")
    sess.record("pulse", "浮紧")
    cands = rank_syndromes(sess, "头痛")
    print(f"候选证型：{[(c['n'], c['score']) for c in cands[:3]]}\n")
    print(render_plan(build_plan(cands[0]["id"], sess, prof)))