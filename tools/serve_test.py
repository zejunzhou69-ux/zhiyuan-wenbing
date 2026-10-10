"""知源问病 · 服务端到端测试：建会话 -> 问诊 -> 红旗拦截 -> 出方案"""
from __future__ import annotations

import json
import sys
import threading
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from web.app import Handler, ThreadingHTTPServer, PORT   # noqa: E402

BASE = f"http://127.0.0.1:{PORT + 1}"


def post(path: str, body: dict) -> dict:
    req = urllib.request.Request(
        BASE + path, data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def get(path: str) -> dict:
    with urllib.request.urlopen(BASE + path, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def main() -> int:
    Handler.cfg = {"llm": {"api_key": ""}}
    srv = ThreadingHTTPServer(("127.0.0.1", PORT + 1), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    time.sleep(0.6)
    ok = True
    try:
        print("=" * 60)
        print("1. GET /api/stats")
        s = get("/api/stats")
        st = s["stats"]
        print(f"   ok={s['ok']} 证型={st['证型']} 方={st['方剂']} 药={st['中药']} "
              f"经穴={st['经穴(含经外奇穴)']} 董氏流派={st['董氏流派']}")

        print("\n2. 建会话（孕妇 + 服华法林）")
        r = post("/api/new", {"profile": {"sex": "female", "age": 28,
                                        "pregnant": True,
                                        "medications": ["华法林 2.5mg"]}})
        sid = r["sid"]
        print(f"   sid={sid}")

        print("\n3. 急症红旗：孕妇腹痛（硬规则）")
        r = post("/api/chat", {"sid": sid, "text": "怀孕8周，今天突然肚子疼"})
        rep = r["reply"]
        print("   " + rep[:160].replace("\n", "\n   "))
        hit = ("孕产急症" in rep) and ("不给方" in rep)
        print(f"   急症拦截：{'通过' if hit else '失败'}")
        ok = ok and hit

        print("\n4. 正常问诊：头痛")
        post("/api/chat", {"sid": sid, "text": "后脑勺疼三天了"})
        for ans in ["怕冷风，手脚凉，不渴", "不出汗", "后脑连着脖子一起疼",
                    "大便一天一次成形", "小便正常", "吃凉的胃里不舒服",
                    "睡眠正常", "没心情不好"]:
            r = post("/api/chat", {"sid": sid, "text": ans})
        c = r["completeness"]
        print(f"   采集完成度 {c['done']}/{c['total']}（{c['percent']}%）")

        print("\n5. 继续问到出方案")
        for ans in ["舌淡红苔薄白", "脉浮紧", "声音有点懒", "以前没什么大病，没吃药"]:
            r = post("/api/chat", {"sid": sid, "text": ans})
        rep = r["reply"]
        print(f"   回复长度 {len(rep)} 字")
        checks = {
            "经穴通道出现": "通道一：十四经穴" in rep,
            "董氏通道出现": "通道二：董氏奇穴" in rep,
            "标明两套体系不同": "不是同一套体系" in rep,
            "董氏定位锁定": "不输出董氏奇穴的定位" in rep,
            "孕期禁忌注入": ("妊娠" in rep or "禁用" in rep or "禁针" in rep),
        }
        for k, v in checks.items():
            print(f"   {k}：{'通过' if v else '失败'}")
        ok = ok and all(checks.values())

        idx = rep.find("通道一")
        if idx > 0:
            print("\n" + "-" * 60)
            print(rep[max(0, idx - 100):idx + 760])
            print("-" * 60)

        print("\n6. GET /  前端页面")
        with urllib.request.urlopen(BASE + "/", timeout=10) as resp:
            html = resp.read().decode("utf-8")
        has = "知源问病" in html
        print(f"   HTML {len(html)} 字节，含标题：{has}")
        ok = ok and has
    finally:
        srv.shutdown()

    print("\n" + "=" * 60)
    print("结果：" + ("全部通过" if ok else "有失败项"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())