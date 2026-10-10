"""知源问病 · 知识库与检索

通道隔离原则（本文件的硬约束）
十四经穴与董氏奇穴是两条独立通道，物理上不混：
  经穴通道：acupoints.json  -> search_acupoint() / points_meridian()
  董氏通道：dongshi.json     -> search_dongshi() / points_dongshi()
任何检索函数都不得跨通道返回条目；治疗方案由 plan_points() 分别产出两个字段，
由调用方分两段输出。这是用户要求的「董氏奇穴和传统穴位要分开来」的技术落点。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


class KnowledgeBase:
    def __init__(self, data_dir: Path | None = None) -> None:
        self.dir = data_dir or DATA
        self.formulas: list[dict] = []
        self.herbs: list[dict] = []
        self.acupoints: list[dict] = []      # 经穴通道（不含董氏穴）
        self.tuina_hand: list[dict] = []
        self.tuina_proto: list[dict] = []
        self.diseases: list[dict] = []
        self.syndromes: list[dict] = []
        self.dongshi_points: list[dict] = []
        self.dongshi_names: list[dict] = []
        self.dongshi_theory: list[dict] = []
        self.dongshi_lineage = "yangweijie"
        self.dongshi_meta: dict = {}
        self.tuina_global_contra: dict = {}
        self.load()

    # ------------------------------------------------------------------ 加载
    def load(self) -> None:
        self.formulas = self._read("formulas.json").get("formulas", [])
        self.herbs = self._read("herbs.json").get("herbs", [])

        ap = self._read("acupoints.json").get("acupoints", [])
        # 通道隔离：经穴库里清掉任何混入的董氏来源条目
        self.acupoints = [a for a in ap if a.get("source_system", "经穴") != "董氏奇穴"]

        t = self._read("tuina.json")
        self.tuina_hand = t.get("handcrafts", [])
        self.tuina_proto = t.get("protocols", [])
        self.tuina_global_contra = t.get("global_contraindications", {})

        s = self._read("syndromes.json")
        self.diseases = s.get("diseases", [])
        self.syndromes = s.get("syndromes", [])

        d = self._read("dongshi.json")
        self.dongshi_points = d.get("points", [])
        names = d.get("names", {})
        self.dongshi_names = (names.get("hand", []) or []) + (names.get("foot_leg", []) or [])
        self.dongshi_theory = d.get("theory", [])
        self.dongshi_meta = d.get("_meta", {})
        cfg = self.dongshi_meta.get("lineage_config", {})
        self.dongshi_lineage = cfg.get("default", "yangweijie")

        self._build_index()

    def _read(self, name: str) -> dict:
        p = self.dir / name
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}

    def _build_index(self) -> None:
        self._f_by_id = {x["id"]: x for x in self.formulas}
        self._h_by_id = {x["id"]: x for x in self.herbs}
        self._a_by_id = {x["id"]: x for x in self.acupoints}
        self._s_by_id = {x["id"]: x for x in self.syndromes}
        self._dp_by_id = {x["id"]: x for x in self.tuina_proto}

    # ------------------------------------------------------------------ 检索
    @staticmethod
    def _score(item: dict, text: str, fields: tuple[str, ...]) -> float:
        t = text.lower()
        sc = 0.0
        for f in fields:
            v = item.get(f)
            if not v:
                continue
            if isinstance(v, list):
                v = " ".join(str(x) for x in v)
            v = str(v).lower()
            if v and v in t:
                sc += len(v) / max(len(t), 1) * 100 + min(len(v), 8)
        return sc

    def search_formula(self, text: str, k: int = 5) -> list[dict]:
        fields = ("name", "indications", "functions", "similar_diff")
        out = [f for f in self.formulas if self._score(f, text, fields) > 0]
        out.sort(key=lambda x: -self._score(x, text, fields))
        return out[:k]

    def search_herb(self, text: str, k: int = 8) -> list[dict]:
        fields = ("name", "indications", "effects")
        out = [h for h in self.herbs if self._score(h, text, fields) > 0]
        out.sort(key=lambda x: -self._score(x, text, fields))
        return out[:k]

    def search_syndrome(self, text: str, k: int = 8) -> list[dict]:
        fields = ("n", "d", "sy", "me", "tx")
        out = [s for s in self.syndromes if self._score(s, text, fields) > 0]
        out.sort(key=lambda x: -self._score(x, text, fields))
        return out[:k]

    def search_tuina(self, text: str, k: int = 5) -> list[dict]:
        fields = ("condition", "syndrome_pattern")
        out = [p for p in self.tuina_proto if self._score(p, text, fields) > 0]
        out.sort(key=lambda x: -self._score(x, text, fields))
        return out[:k]

    # ------------------------------------------------------------ 通道一：经穴
    def search_acupoint(self, text: str, k: int = 8) -> list[dict]:
        """仅返回十四经穴/经外奇穴。绝不返回董氏奇穴。"""
        fields = ("name", "indications", "meridian")
        out = [a for a in self.acupoints if self._score(a, text, fields) > 0]
        out.sort(key=lambda x: -self._score(x, text, fields))
        return out[:k]

    def points_meridian(self, syndrome_id: str) -> list[dict]:
        """取某证型的经穴方案，返回条目详情。"""
        sx = self._s_by_id.get(syndrome_id, {})
        return [self._a_by_id[i] for i in sx.get("ac", []) if i in self._a_by_id]

    # ------------------------------------------------------------ 通道二：董氏
    def search_dongshi(self, text: str, k: int = 8) -> list[dict]:
        """仅返回董氏奇穴。

        location_to_output 是唯一允许输出给用户的定位来源：
        points 中 verified=false 的条目该字段为空字符串，引擎据此拒绝输出定位。
        """
        out: list[dict] = []
        t = text.lower()
        for p in self.dongshi_points:
            if p.get("name") and p["name"][:2] in t:
                out.append({**p, "channel": "dongshi",
                            "location_to_output": p.get("location", "") if p.get("verified") else ""})
        for nm in self.dongshi_names:
            if nm["name"][:2] and nm["name"][:2] in t:
                out.append({
                    "name": nm["name"], "part": nm.get("part", ""),
                    "direction": nm.get("direction", ""),
                    "use_for": nm.get("use_for", []),
                    "lineage": self.dongshi_lineage, "channel": "dongshi",
                    "verified": False, "location_to_output": "",
                    "conflict_note": nm.get("conflict_note", ""),
                })
        return out[:k]

    def dongshi_by_use(self, keywords: list[str]) -> list[dict]:
        """按主治方向反查董氏穴（证型 -> 董穴配伍的补充手段）。

        匹配用「关键词前 2 字」，因为症状描述常带修饰字（「发热轻」「痰白清稀」）。

        **不把病名(d)纳入关键词**：病名截断后容易产生假匹配
        （例：病名「小儿积食」截成「小儿」，会撞上董氏定喘的主治「小儿喘促」）。
        只用证型名 + 主症，匹配质量才可靠。
        """
        keys: list[str] = []
        for kw in keywords:
            kw = (kw or "").strip()
            if len(kw) >= 2:
                keys.extend([kw, kw[:2]])
        hit, seen = [], set()
        for nm in self.dongshi_names:
            if nm["name"] in seen:
                continue
            hay = nm.get("direction", "") + " " + " ".join(nm.get("use_for", []))
            for kw in keys:
                if kw and kw in hay:
                    hit.append({**nm, "channel": "dongshi", "location_to_output": "",
                                "lineage": self.dongshi_lineage,
                                "match_on": kw})
                    seen.add(nm["name"])
                    break
        return hit

    def points_dongshi(self, syndrome_id: str) -> dict:
        """取某证型的董氏方案，返回结构固定，便于分两段输出。"""
        sx = self._s_by_id.get(syndrome_id, {})
        keys = [sx.get("n", "")] + sx.get("sy", [])[:4]
        matches = self.dongshi_by_use(keys)
        return {
            "hint": sx.get("ds", ""),
            "matches": matches[:5],
            "location_ready": [p["name"] for p in self.dongshi_points if p.get("verified")],
            "lineage": self.dongshi_lineage,
            "note": "董氏奇穴定位待按原书补录；补录前系统只给配穴思路，不给定位。",
        }

    # ------------------------------------------------------------------ 主诉 -> 病
    def match_disease(self, text: str, chief_text: str = "") -> list[tuple[dict, int]]:
        """主诉(chief_text)里的症状权重更高。

        用户说「后脑勺疼」是主症，「怕冷」是伴随症 —— 两者都命中时应判头痛，
        不能靠出现顺序决定。必须有 chief 加权，否则这个 bug 会一直在。
        """
        res = []
        for d in self.diseases:
            hit = chief_hit = 0
            for kw in d.get("kw", []):
                if kw in text:
                    hit += 1
                    if chief_text and kw in chief_text:
                        chief_hit += 1
            if hit:
                res.append((d, hit + chief_hit * 2))
        res.sort(key=lambda x: (-x[1], x[0]["name"]))   # 同分按名称，保证结果确定
        return res

    # ------------------------------------------------------------------ 详情
    def formula(self, fid: str) -> dict | None:
        return self._f_by_id.get(fid)

    def herb(self, hid: str) -> dict | None:
        return self._h_by_id.get(hid)

    def herb_by_name(self, name: str) -> dict | None:
        """按药名查中药（含炮制品名匹配，如「制首乌」→ 何首乌（制））。"""
        if not name:
            return None
        if name in self._h_by_id:
            return self._h_by_id[name]
        for h in self.herbs:
            if h.get("name", "") == name:
                return h
        for h in self.herbs:
            if name in h.get("name", "") or h.get("name", "") in name:
                return h
        return None

    def syndrome(self, sid: str) -> dict | None:
        return self._s_by_id.get(sid)

    def disease(self, name: str) -> dict | None:
        return next((d for d in self.diseases if d["name"] == name), None)

    # ------------------------------------------------------------------ 通道自检
    @staticmethod
    def assert_channel_separation(meridian: list[dict], dongshi: list[dict]) -> None:
        """确认两条通道没有串。发现问题直接抛错，不静默通过。"""
        for p in meridian:
            if p.get("source_system") == "董氏奇穴":
                raise AssertionError(f"经穴通道混入董氏条目：{p.get('name')}")
        for p in dongshi:
            if p.get("channel") != "dongshi":
                raise AssertionError(f"董氏通道混入非董氏条目：{p.get('name')}")

    # ------------------------------------------------------------------ 统计
    def stats(self) -> dict:
        return {
            "方剂": len(self.formulas), "中药": len(self.herbs),
            "经穴(含经外奇穴)": len(self.acupoints),
            "董氏奇穴(已录定位)": len([p for p in self.dongshi_points if p.get("verified")]),
            "董氏奇穴(穴名层待补录)": len(self.dongshi_names),
            "推拿手法": len(self.tuina_hand), "推拿方案": len(self.tuina_proto),
            "证型": len(self.syndromes), "病种": len(self.diseases),
            "董氏流派": self.dongshi_lineage,
        }


_KB: KnowledgeBase | None = None


def get_kb() -> KnowledgeBase:
    global _KB
    if _KB is None:
        _KB = KnowledgeBase()
    return _KB


if __name__ == "__main__":
    kb = get_kb()
    for k, v in kb.stats().items():
        print(f"{k:<24}{v}")
    print("\n通道自检：")
    ms = kb.points_meridian("S001")
    ds = kb.points_dongshi("S001")
    KnowledgeBase.assert_channel_separation(ms, ds["matches"])
    print(f"  经穴通道 S001 → {[p['name'] for p in ms]}")
    print(f"  董氏通道 S001 → {ds['hint'][:46]}…")
    print(f"  董氏反查命中 → {[m['name'] for m in ds['matches']]}")
    print(f"  董氏可输出定位 → {ds['location_ready'] or '（无，等待原书 PDF 补录）'}")