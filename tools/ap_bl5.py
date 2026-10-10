r"""足太阳膀胱经 · 腰部最后 4 穴（BL49–BL52），收尾

阳纲、志室、肓门、胞肓。全部 verified=false。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from add_acupoints import apply  # noqa: E402

M = "足太阳膀胱经"
LUMB = "⚠️腰部深方为腹腔与肾脏，禁深刺；孕妇禁针。"

ITEMS = [
    {"name": "阳纲", "code": "BL49", "meridian": M,
     "location": "在背部，第10胸椎棘突下，旁开3寸。",
     "anatomy_note": "浅层：第10胸神经后支的皮支；深层：斜方肌、菱形肌。⚠️深方近肺与胸膜。",
     "depth_limit": "斜刺0.5～0.8寸",
     "indications": ["黄疸", "腹痛", "肠鸣", "泄泻", "小便不利"],
     "needling": "沿肩胛骨内缘向下斜刺；可灸。",
     "contraindication": "⚠️⚠️胸背部，禁深刺，防气胸。"},

    {"name": "志室", "code": "BL50", "meridian": M,
     "location": "在腰部，第2腰椎棘突下，旁开3寸。",
     "anatomy_note": "浅层：第2腰神经后支的皮支；深层：腰背筋膜、腰大肌。",
     "depth_limit": "直刺0.8～1寸",
     "indications": ["遗精", "阳痿", "小便不利", "水肿", "腰脊强痛", "泄泻"],
     "needling": "直刺；可灸。",
     "contraindication": LUMB, "self_moxa_safe": True},

    {"name": "肓门", "code": "BL51", "meridian": M,
     "location": "在腰部，第1腰椎棘突下，旁开3寸。",
     "anatomy_note": "浅层：第1腰神经后支的皮支；深层：腰背筋膜、腰大肌。",
     "depth_limit": "直刺0.8～1寸",
     "indications": ["腹痛", "便秘", "痞块", "乳疾", "腰脊强痛"],
     "needling": "直刺；可灸。",
     "contraindication": LUMB, "self_moxa_safe": True},

    {"name": "胞肓", "code": "BL52", "meridian": M,
     "location": "在骶区，横平第2骶后孔，骶正中嵴旁开3寸。",
     "anatomy_note": "浅层：臀中皮神经；深层：臀大肌。",
     "depth_limit": "直刺0.8～1.2寸",
     "indications": ["肠鸣", "腹胀", "便秘", "癃闭", "腰脊强痛", "下肢痿痹"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️孕妇禁针。", "self_moxa_safe": True},
]

if __name__ == "__main__":
    raise SystemExit(apply(ITEMS, "膀胱经·收尾4穴"))
