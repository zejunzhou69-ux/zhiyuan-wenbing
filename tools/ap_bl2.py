r"""足太阳膀胱经 · 背腰部俞穴与腰骶穴 10 穴

BL14 厥阴俞、BL16 督脉俞、BL19 胆俞、BL22 三焦俞、BL25 大肠俞、
BL26 关元俞、BL27 小肠俞、BL28 膀胱俞、BL29 中膂俞、BL30 白环俞

⚠️ 背部俞穴统一安全提示：胸背段深方为胸腔，禁深刺；
孕妇腰腹段禁刺。全部 verified=false。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from add_acupoints import apply  # noqa: E402

M = "足太阳膀胱经"
THORAX = "⚠️胸背部，深方为胸腔与肺，禁深刺直刺，勿提插；孕妇禁针。"

ITEMS = [
    {"name": "厥阴俞", "code": "BL14", "meridian": M,
     "location": "在背部，第4胸椎棘突下，后正中线旁开1.5寸。",
     "anatomy_note": "浅层：第4胸神经后支的皮支；深层：斜方肌、菱形肌，有第4胸神经后支与肋间神经后支。⚠️深方近肺与胸膜。",
     "depth_limit": "直刺或斜刺0.5～0.8寸",
     "indications": ["心痛", "心悸", "咳嗽", "气喘", "胸闷", "疟疾"],
     "needling": "向内斜刺或平刺；可灸。",
     "contraindication": THORAX},

    {"name": "督脉俞", "code": "BL16", "meridian": M,
     "location": "在背部，第4胸椎棘突下，后正中线旁开1.5寸。",
     "anatomy_note": "浅层：第4胸神经后支的皮支；深层：斜方肌、菱形肌。⚠️深方近肺与胸膜。",
     "depth_limit": "直刺或斜刺0.5～0.8寸",
     "indications": ["心痛", "胸闷", "咳嗽", "气喘", "疟疾", "感冒", "癫狂"],
     "needling": "向内斜刺或平刺；可灸。",
     "contraindication": THORAX},

    {"name": "胆俞", "code": "BL19", "meridian": M,
     "location": "在背部，第10胸椎棘突下，后正中线旁开1.5寸。",
     "anatomy_note": "浅层：第10胸神经后支的皮支；深层：斜方肌、菱形肌。",
     "depth_limit": "直刺或斜刺0.5～0.8寸",
     "indications": ["黄疸", "口苦", "胁痛", "肺痨", "潮热", "盗汗"],
     "needling": "向内斜刺或平刺；可灸。",
     "contraindication": THORAX},

    {"name": "三焦俞", "code": "BL22", "meridian": M,
     "location": "在背部，第11胸椎棘突下，旁开1.5寸。",
     "anatomy_note": "浅层：第11胸神经后支的皮支；深层：斜方肌、菱形肌、腰背筋膜。",
     "depth_limit": "直刺0.5～0.8寸",
     "indications": ["肠鸣", "腹胀", "呕吐", "泄泻", "水肿", "腰背强痛"],
     "needling": "向内斜刺或平刺；可灸。",
     "contraindication": "⚠️腰背部深方为腹腔，禁深刺；孕妇禁针。", "self_moxa_safe": True},

    {"name": "大肠俞", "code": "BL25", "meridian": M,
     "location": "在腰部，第4腰椎棘突下，旁开1.5寸。",
     "anatomy_note": "浅层：第4腰神经后支的皮支；深层：腰背筋膜、腰大肌。",
     "depth_limit": "直刺0.8～1.2寸",
     "indications": ["腹胀", "泄泻", "便秘", "腰腿痛", "坐骨神经痛", "痔疾"],
     "needling": "直刺，针尖略向内；可灸。",
     "contraindication": "⚠️孕妇禁针；腰部深方为腹腔，禁深刺。", "self_moxa_safe": True},

    {"name": "关元俞", "code": "BL26", "meridian": M,
     "location": "在腰部，第5腰椎棘突下，旁开1.5寸。",
     "anatomy_note": "浅层：第5腰神经后支的皮支；深层：腰背筋膜、腰大肌。",
     "depth_limit": "直刺0.8～1.2寸",
     "indications": ["腰骶痛", "腹胀", "泄泻", "小便频数", "遗尿", "痔疮"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️孕妇禁针；禁深刺。", "self_moxa_safe": True},

    {"name": "小肠俞", "code": "BL27", "meridian": M,
     "location": "在骶区，横平第1骶后孔，骶正中嵴旁开1.5寸。",
     "anatomy_note": "浅层：第1骶神经后支的皮支；深层：骶棘肌。",
     "depth_limit": "直刺0.8～1.2寸",
     "indications": ["遗精", "遗尿", "尿血", "带下", "泄泻", "痢疾", "腰骶痛"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️孕妇禁针。", "self_moxa_safe": True},

    {"name": "膀胱俞", "code": "BL28", "meridian": M,
     "location": "在骶区，横平第2骶后孔，骶正中嵴旁开1.5寸。",
     "anatomy_note": "浅层：第2骶神经后支的皮支；深层：骶棘肌。",
     "depth_limit": "直刺0.8～1.2寸",
     "indications": ["小便不利", "遗尿", "泄泻", "便秘", "腰脊强痛", "下肢痿痹"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️孕妇禁针。", "self_moxa_safe": True},

    {"name": "中膂俞", "code": "BL29", "meridian": M,
     "location": "在骶区，横平第3骶后孔，骶正中嵴旁开1.5寸。",
     "anatomy_note": "浅层：臀中皮神经；深层：骶棘肌。",
     "depth_limit": "直刺0.8～1.2寸",
     "indications": ["泄泻", "痢疾", "腰脊强痛", "下肢痿痹", "痔疮"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️孕妇禁针。", "self_moxa_safe": True},

    {"name": "白环俞", "code": "BL30", "meridian": M,
     "location": "在骶区，横平第4骶后孔，骶正中嵴旁开1.5寸。",
     "anatomy_note": "浅层：臀中皮神经；深层：臀大肌。",
     "depth_limit": "直刺0.8～1.2寸",
     "indications": ["遗精", "带下", "月经不调", "疝气", "便秘", "腰骶痛", "下肢痿痹"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️孕妇禁针。", "self_moxa_safe": True},
]

if __name__ == "__main__":
    raise SystemExit(apply(ITEMS, "膀胱经·背腰骶10穴"))
