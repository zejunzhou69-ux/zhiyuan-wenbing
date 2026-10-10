r"""知源问病 · 静态站数据打包

把 7 个 JSON 合并成 1 个 bundle.json：
- 7 个请求 → 1 个请求，首屏快很多
- 去掉每个文件的 _meta 里冗长的政策说明（改为在 JS 里保留最小必要项）

不打包的内容（版权/隐私）：
- knowledge/textbook.jsonl  教材原文切片，**绝不上传**
- config/config.json       含 API key

用法：
    python tools/build_bundle.py
    python tools/build_bundle.py --out static/js/bundle.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SRC = ROOT / "data"
DEFAULT_OUT = ROOT / "static" / "js" / "bundle.js"
INDEX = ROOT / "static" / "index.html"


def load(name: str) -> dict:
    p = SRC / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def build() -> dict:
    f = load("formulas.json")
    h = load("herbs.json")
    a = load("acupoints.json")
    d = load("dongshi.json")
    t = load("tuina.json")
    s = load("syndromes.json")
    r = load("redflags.json")

    # 通道隔离的硬保证：经穴库里清掉任何董氏来源条目
    meridian = [x for x in a.get("acupoints", []) if x.get("source_system", "经穴") != "董氏奇穴"]

    meta_d = d.get("_meta", {})
    lineage = meta_d.get("lineage_config", {}).get("default", "yangweijie")
    names = d.get("names", {})

    return {
        "_meta": {
            "app": "知源问病",
            "version": "1.0",
            "license": "知识内容为教材通行表述的整理，代码开源",
            "dongshi_lineage": lineage,
            "disclaimer": "本应用输出为中医辨证思路与健康建议，不构成处方，不能替代执业医师面诊。用药前须经执业中医师复核签字。",
        },
        "formulas": f.get("formulas", []),
        "herbs": h.get("herbs", []),
        "acupoints": meridian,
        "dongshi": {
            "theory": d.get("theory", []),
            "points": d.get("points", []),
            "names_hand": names.get("hand", []),
            "names_foot": names.get("foot_leg", []),
            "usage_patterns": names.get("usage_patterns", []),
            "lineage": lineage,
            "locator_note": d.get("_meta", {}).get("usage_rule", ""),
        },
        "tuina": {
            "handcrafts": t.get("handcrafts", []),
            "protocols": t.get("protocols", []),
            "level_def": t.get("level_def", {}),
            "global_contraindications": t.get("global_contraindications", {}),
        },
        "diseases": s.get("diseases", []),
        "syndromes": s.get("syndromes", []),
        "redflags": {
            "emergency": r.get("emergency", []),
            "must_refer": r.get("must_refer", []),
            "special_populations": r.get("special_populations", {}),
            "drug_safety_rules": r.get("drug_safety_rules", []),
            "needling_safety": r.get("needling_safety", []),
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--minify", action="store_true", help="去掉空格换行，体积再小 ~30%")
    args = ap.parse_args()

    data = build()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    # 输出成 js 而不是 json：这样 file:// 直接双击也能用（fetch 会被 CORS 拦），
    # 部署到 Cloudflare Pages 同样没问题，少一个请求。
    if args.minify:
        body = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    else:
        body = json.dumps(data, ensure_ascii=False)
    text = "/* 自动生成，请勿手改。源数据见仓库 data/*.json，重新生成：python tools/build_bundle.py */\n" \
           "window.ZYW_BUNDLE = " + body + ";\n"
    out.write_text(text, encoding="utf-8")
    size_kb = len(text.encode("utf-8")) / 1024

    print(f"已打包 → {out}")
    print(f"体积：{size_kb:.0f} KB")
    print(f"  方剂 {len(data['formulas'])}｜中药 {len(data['herbs'])}｜经穴 {len(data['acupoints'])}")
    print(f"  董氏奇穴 理论 {len(data['dongshi']['theory'])}｜定位已录 {len(data['dongshi']['points'])}"
          f"｜穴名层 {len(data['dongshi']['names_hand']) + len(data['dongshi']['names_foot'])}")
    print(f"  推拿 手法 {len(data['tuina']['handcrafts'])}｜方案 {len(data['tuina']['protocols'])}")
    print(f"  病种 {len(data['diseases'])}｜证型 {len(data['syndromes'])}")
    print(f"  红旗 急症 {len(data['redflags']['emergency'])}｜必转诊 {len(data['redflags']['must_refer'])}")

    # 确认没把不该传的东西打进去了
    low = text.lower()
    assert "apikey" not in low and "api_key" not in low, "包里混入了 API key！"
    print("\n✅ 未混入 API key")

    fingerprint(out)
    return 0


def fingerprint(out: Path) -> None:
    """给 bundle 加内容指纹，并改写 index.html 的引用。

    为什么必须做：static/_headers 里 bundle.js 设了24 小时缓存
    （max-age=86400，这是为了省流量）。但知识库更新后 URL 不变，
    浏览器就会继续用旧版 —— 实测发现补录穴位后线上仍显示旧的穴数。
    内容指纹让「数据变了 -> 文件名变了 -> 浏览器必然拉新的」，
    同时未变的内容仍能长期缓存，不必重复下载 500KB。
    """
    h = hashlib.sha256(out.read_bytes()).hexdigest()[:10]
    hashed = out.with_name(f"bundle.{h}.js")
    if not hashed.exists():
        hashed.write_bytes(out.read_bytes())

    if INDEX.exists():
        html = INDEX.read_text(encoding="utf-8")
        new_html = re.sub(r'js/bundle(\.[0-9a-f]+)?\.js',
                          f'js/bundle.{h}.js', html)
        if new_html != html:
            INDEX.write_text(new_html, encoding="utf-8")
            print(f"   index.html 已引用 bundle.{h}.js")

    # 清掉上一轮遗留的指纹文件，避免 static/js 里堆一堆旧 bundle
    for old in out.parent.glob("bundle.*.js"):
        if old.name != hashed.name:
            old.unlink()
            print(f"   清理旧版 {old.name}")


if __name__ == "__main__":
    raise SystemExit(main())
