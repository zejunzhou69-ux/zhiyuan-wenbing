"""知源问病 · 对话编排

零依赖（标准库 http.server），不要求装 FastAPI/uvicorn。
没配模型 API 时自动降级为规则模式，仍可完整使用四诊采集与辨证。
"""
from __future__ import annotations

import json
import sys
import threading
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from engine.kb import get_kb                                    # noqa: E402
from engine.safety import get_safety, extract_herb_names       # noqa: E402
from engine import diagnose as dg                               # noqa: E402
from engine.textbook import get_textbook                       # noqa: E402
from engine import inverse as inv                              # noqa: E402
from llm.client import LLMClient, PROMPT                        # noqa: E402

CONFIG_PATH = ROOT / "config" / "config.json"
PORT = 8787
_KB = None


def load_config() -> dict:
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return {"llm": {"base_url": "", "api_key": "", "model": ""},
            "dongshi_lineage": "yangweijie"}


class Session:
    """一个用户的一次问诊会话。"""

    def __init__(self, profile: dict) -> None:
        self.profile = profile
        self.diag = dg.FourDiagSession(profile)
        self.history: list[dict] = []
        self.lock = threading.Lock()

    def to_dict(self) -> dict:
        return {"profile": self.profile,
                "collected": self.diag.collected,
                "completeness": self.diag.completeness(),
                "stages": self.diag.stages_done()}


SESSIONS: dict[str, Session] = {}


def kb():
    global _KB
    if _KB is None:
        _KB = get_kb()
    return _KB


def knowledge_block(disease: str | None, text: str) -> str:
    """检索教材片段注入上下文（带出处）。"""
    K = kb()
    parts: list[str] = []
    if disease:
        d = K.disease(disease)
        if d:
            parts.append(f"【病种】{d['name']}（{d['cat']}）｜必须排除：{'、'.join(d.get('ex', []))}")
            for sid in d.get("sx", []):
                s = K.syndrome(sid)
                if not s:
                    continue
                fnames = []
                for f in s.get("fx", []):
                    fx = K.formula(f)
                    fnames.append(fx["name"] if fx else f)
                parts.append(
                    f"【证型】{s['n']}｜主症：{'、'.join(s.get('sy', []))}｜"
                    f"舌：{s.get('tg','')}｜脉：{s.get('p','')}｜病机：{s.get('me','')}｜"
                    f"治法：{s.get('tx','')}｜方：{'、'.join(fnames)}")

    ms = K.search_acupoint(text, k=6)
    if ms:
        parts.append("【经穴（通道一，十四经穴）】" + "、".join(
            f"{p['name']}（{p.get('meridian','')}）定位{p.get('location','')}｜深度上限{p.get('depth_limit','')}"
            for p in ms))

    ds = K.search_dongshi(text, k=4)
    if ds:
        parts.append("【董氏奇穴（通道二，与经穴不是同一体系）】" + "、".join(
            f"{p['name']}（{p.get('direction','')}；定位待原书核对，系统不输出定位）" for p in ds))

    # 教材原文片段（带出处，用于引用溯源）
    tb = get_textbook()
    if len(tb):
        blk = tb.context_block(text + " " + (disease or ""), k=4)
        if blk:
            parts.append(blk)
    return "\n".join(parts)


def emergency_reply(blk: dict) -> str:
    lines = [f"🛑 **命中急症红旗：{blk['cat']}**", "", f"**{blk['action']}**", ""]
    if blk.get("note"):
        lines += [blk["note"], ""]
    lines += [
        "本次不进行辨证、不给方、不给穴。远程问诊无法排除这类急症，",
        "任何中医处置（含推拿、针灸、服中药）都会延误抢救。",
        "",
        "⚠️ 心理援助热线：12356（全国 24 小时）",
    ]
    return "\n".join(lines)


def current_disease(sess: Session, text: str) -> str | None:
    m = kb().match_disease(sess.diag.text() + " " + text,
                          sess.diag.collected.get("chief", ""))
    return m[0][0]["name"] if m else None


def structured_part(sess: Session, text: str) -> str:
    """规则引擎产出的结构化内容：采集不足则给问题，够了就给方案。"""
    c = sess.diag.completeness()
    if not c["ready"]:
        qs = sess.diag.next_questions(2)
        return "本次只问 2 个问题：\n" + "\n".join(
            f"{i}. {q['q']}" for i, q in enumerate(qs, 1))

    cands = dg.rank_syndromes(sess.diag, current_disease(sess, text))
    if cands and cands[0]["score"] > 0:
        return dg.render_plan(dg.build_plan(cands[0]["id"], sess.diag, sess.profile))
    return "尚无可用证据，不能定证。还缺：" + "、".join(q["q"] for q in c["missing"][:3])


def rule_reply(sess: Session, text: str) -> str:
    blk = get_safety().emergency_block(text, sess.profile)
    if blk:
        return emergency_reply(blk)

    disease = current_disease(sess, text)
    if disease and not sess.diag.collected.get("chief"):
        sess.diag.record("chief", text)

    c = sess.diag.completeness()
    if c["ready"]:
        return structured_part(sess, text)

    qs = sess.diag.next_questions(2)
    lines = [f"已采集 {c['done']}/{c['total']} 项（{c['percent']}%）。"]
    if disease:
        lines.append(f"初步看病种在「{disease}」这一类，先往下问。")
    lines += ["", "本次请你答两个："]
    for i, q in enumerate(qs, 1):
        lines.append(f"{i}. {q['q']}")
    lines += ["", "（不是考你，是用来区分证型的关键信息；说不出就答「不知道」，我不会替你编。）"]
    return "\n".join(lines)


def llm_reply(sess: Session, text: str, cfg: dict) -> str:
    """模型增强模式。安全层先行，安全层不过，模型没机会说话。"""
    blk = get_safety().emergency_block(text, sess.profile)
    if blk:
        return emergency_reply(blk)

    structured = structured_part(sess, text)
    sess.history.append({"role": "user", "content": text})
    prompt = (PROMPT.replace("{{stage_hint}}", structured)
              .replace("{{knowledge_block}}", knowledge_block(current_disease(sess, text), text)))
    out = LLMClient(cfg.get("llm", {})).chat(prompt, sess.history)
    sess.history.append({"role": "assistant", "content": out})
    return out + "\n\n" + structured


def lookup_reply(kind: str, text: str) -> str:
    """逆向模式（查阅）：病/症/方/穴/其他疗法。

    不做红旗拦截——这里不是给具体患者下诊断，是查知识。
    但证型里的「必须排除」与安全提示照常带出。
    """
    iv = inv.Inverse()
    kind = (kind or "disease").lower()
    if kind == "disease":
        return inv.render_disease(iv.by_disease(text))
    if kind == "symptom":
        return inv.render_symptom(iv.by_symptom(text))
    if kind == "formula":
        return inv.render_formula(iv.by_formula(text))
    if kind == "acupoint":
        return inv.render_acupoint(iv.by_acupoint(text))
    if kind == "therapy":
        return inv.render_therapy()
    return "未知的查阅类型。可用：disease / symptom / formula / acupoint / therapy"


class Handler(BaseHTTPRequestHandler):
    cfg = load_config()

    def log_message(self, fmt, *args):
        pass

    def _json(self, obj: dict, code: int = 200) -> None:
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._serve(ROOT / "web" / "index.html", "text/html; charset=utf-8")
        elif self.path == "/api/stats":
            self._json({"ok": True, "stats": kb().stats(),
                        "llm_enabled": bool(self.cfg.get("llm", {}).get("api_key"))})
        elif self.path.startswith("/api/session/"):
            s = SESSIONS.get(self.path.rsplit("/", 1)[-1])
            self._json({"ok": bool(s), "session": s.to_dict() if s else None})
        else:
            self._json({"ok": False, "error": "not found"}, 404)

    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(n).decode("utf-8") or "{}")
        except Exception:
            self._json({"ok": False, "error": "bad json"}, 400)
            return
        try:
            if self.path == "/api/new":
                sid = data.get("sid") or str(abs(hash(json.dumps(
                    data.get("profile", {}), ensure_ascii=False))) % (10 ** 12))
                SESSIONS[sid] = Session(data.get("profile", {}))
                self._json({"ok": True, "sid": sid,
                            "question": "说说你的症状，用大白话就行，专业的术语不用管。"})
                return

            if self.path == "/api/lookup":
                kind = data.get("kind", "disease")
                text = (data.get("text") or "").strip()
                self._json({"ok": True, "reply": lookup_reply(kind, text)})
                return

            if self.path == "/api/diseases":
                self._json({"ok": True, "diseases": [
                    {"name": d["name"], "cat": d["cat"], "count": len(d.get("sx", []))}
                    for d in kb().diseases]})
                return

            if self.path == "/api/chat":
                s = SESSIONS.get(data.get("sid", ""))
                if not s:
                    self._json({"ok": False, "error": "session not found"}, 404)
                    return
                text = (data.get("text") or "").strip()
                # 问诊第一问就是「最不舒服的地方」，第一条输入无条件当主诉。
                # 不能只靠 infer_field ——「后脑勺疼」会判成 head_body，chief 就空了，
                # 而病种匹配的权重恰恰依赖 chief。
                first_chief = not s.diag.collected.get("chief")
                if first_chief:
                    s.diag.record("chief", text)
                field = data.get("field") or dg.infer_field(text, s.profile)
                if field:
                    s.diag.record(field, text)
                elif not first_chief:
                    s.diag.record("chief", (s.diag.collected.get("chief", "") + " " + text).strip())

                use_llm = bool(self.cfg.get("llm", {}).get("api_key"))
                with s.lock:
                    reply = llm_reply(s, text, self.cfg) if use_llm else rule_reply(s, text)
                self._json({"ok": True, "reply": reply,
                            "completeness": s.diag.completeness(),
                            "mode": "llm" if use_llm else "rule"})
                return

            self._json({"ok": False, "error": "not found"}, 404)
        except Exception as exc:                        # noqa: BLE001
            traceback.print_exc()
            self._json({"ok": False, "error": str(exc)}, 500)

    def _serve(self, p: Path, mime: str) -> None:
        if not p.exists():
            self._json({"ok": False, "error": f"{p.name} 不存在"}, 404)
            return
        body = p.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    cfg = load_config()
    st = kb().stats()
    print("=" * 58)
    print("  知源问病 · 中医辨证问诊智能体")
    print("=" * 58)
    print(f"  知识库：{st['证型']} 证型 / {st['方剂']} 方 / {st['中药']} 药 / "
          f"经穴 {st['经穴(含经外奇穴)']} / 推拿 {st['推拿手法']} 手法")
    print(f"  董氏奇穴流派：{st['董氏流派']}（定位待原书 PDF 补录）")
    llm = cfg.get("llm", {})
    print(f"  模型：{'已配置 ' + llm.get('model', '') if llm.get('api_key') else '未配置 → 规则模式'}")
    print(f"\n  浏览器打开： http://127.0.0.1:{PORT}\n")
    Handler.cfg = cfg
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()