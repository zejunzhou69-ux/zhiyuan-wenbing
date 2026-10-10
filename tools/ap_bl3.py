r"""足太阳膀胱经 · 腰骶部与下肢 11 穴

BL31 上髎、BL33 下髎、BL35 会阳、BL36 承扶、BL37 殷门、BL38 浮郄、
BL39 委阳、BL41 附分、BL42 魄户、BL43 膏肓、BL55 合阳

⚠️ 承扶、殷门附近为坐骨神经，浮郄、委阳下有腘窝大血管，禁深刺猛刺。
全部 verified=false。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from add_acupoints import apply  # noqa: E402

M = "足太阳膀胱经"

ITEMS = [
    {"name": "上髎", "code": "BL31", "meridian": M,
     "location": "在骶区，正对第1骶后孔中。",
     "anatomy_note": "浅层：臀中皮神经；深层：骶棘肌。⚠️邻近骶管，禁深刺。",
     "depth_limit": "直刺0.5～0.8寸",
     "indications": ["月经不调", "带下", "遗精", "阳痿", "大小便不利", "腰骶痛"],
     "needling": "直刺0.5～0.8寸；可灸。",
     "contraindication": "⚠️骶管内有马尾神经，禁深刺、禁提插；孕妇禁针。", "self_moxa_safe": True},

    {"name": "下髎", "code": "BL33", "meridian": M,
     "location": "在骶区，正对第2骶后孔中。",
     "anatomy_note": "浅层：臀中皮神经；深层：骶棘肌。",
     "depth_limit": "直刺0.5～0.8寸",
     "indications": ["腹痛", "便秘", "小便不利", "带下", "腰骶痛"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️孕妇禁针；禁深刺。", "self_moxa_safe": True},

    {"name": "会阳", "code": "BL35", "meridian": M,
     "location": "在会区，尾骨端下，督脉旁开0.5寸。",
     "anatomy_note": "浅层：臀中皮神经；深层：臀大肌。",
     "depth_limit": "直刺0.5～0.8寸",
     "indications": ["痔疮", "便血", "泄泻", "阳痿", "遗精", "带下"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️会阴区，禁深刺；孕妇禁针。", "self_moxa_safe": True},

    {"name": "承扶", "code": "BL36", "meridian": M,
     "location": "在股后区，臀沟的中点。",
     "anatomy_note": "浅层：臀皮神经；深层：臀大肌、坐骨神经。⚠️坐骨神经体表投影附近，禁深刺。",
     "depth_limit": "直刺0.5～1寸",
     "indications": ["腰骶臀股部疼痛", "下肢痿痹", "痔疾", "便秘"],
     "needling": "直刺，针尖略向内；可灸。",
     "contraindication": "⚠️坐骨神经本干在下方，深刺可致下肢放射痛或损伤；孕妇禁针。", "self_moxa_safe": True},

    {"name": "殷门", "code": "BL37", "meridian": M,
     "location": "在股后区，臀沟下6寸，股二头肌与半腱肌之间。",
     "anatomy_note": "浅层：股后皮神经；深层：坐骨神经、股二头肌、半腱肌。⚠️坐骨神经本干在穴下，禁深刺。",
     "depth_limit": "直刺0.5～1寸",
     "indications": ["腰痛", "下肢痿痹", "半身不遂", "坐骨神经痛"],
     "needling": "直刺，针尖略向上；可灸。",
     "contraindication": "⚠️⚠️穴下即坐骨神经本干，禁深刺、禁强刺激，以免造成神经损伤；孕妇禁针。"},

    {"name": "浮郄", "code": "BL38", "meridian": M,
     "location": "在膝后区，腘横纹上1寸，股二头肌腱的内侧缘。",
     "anatomy_note": "浅层：股后皮神经；深层：股二头肌。",
     "depth_limit": "直刺0.5～1寸",
     "indications": ["股腘部麻木", "腘筋挛急", "下肢痿痹", "便秘"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️腘窝内腘静脉、腘动脉位置较深，禁深刺。", "self_moxa_safe": True},

    {"name": "委阳", "code": "BL39", "meridian": M,
     "location": "在膝部，腘横纹上，股二头肌腱的内侧缘。",
     "anatomy_note": "浅层：股后皮神经；深层：股二头肌。⚠️⚠️腘窝内为腘动脉、腘静脉与胫神经本干，位置固定、搏动明显，禁深刺。",
     "depth_limit": "直刺0.5～1寸",
     "indications": ["腹满", "小便不利", "遗尿", "腰脊强痛", "腿足挛痛", "痿痹"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️⚠️⚠️腘窝大血管与胫神经所在，禁深刺、禁提插，以免致大出血或神经损伤。", "self_moxa_safe": True},

    {"name": "附分", "code": "BL41", "meridian": M,
     "location": "在胸外侧区，第2胸椎棘突下，旁开3寸。",
     "anatomy_note": "浅层：第2胸神经后支的皮支；深层：斜方肌。⚠️深方近肺与胸膜。",
     "depth_limit": "斜刺0.5～0.8寸",
     "indications": ["颈项强痛", "肩背拘急", "肘臂麻木"],
     "needling": "沿肩胛骨内缘向下斜刺；可灸。",
     "contraindication": "⚠️⚠️胸背部，禁深刺直刺，勿提插，以防气胸。"},

    {"name": "魄户", "code": "BL42", "meridian": M,
     "location": "在胸外侧区，第3胸椎棘突下，旁开3寸。",
     "anatomy_note": "浅层：第3胸神经后支的皮支；深层：斜方肌。⚠️深方近肺与胸膜。",
     "depth_limit": "斜刺0.5～0.8寸",
     "indications": ["咳嗽", "气喘", "肺痨", "项强", "肩背痛"],
     "needling": "沿肩胛骨内缘向下斜刺；可灸。",
     "contraindication": "⚠️⚠️胸背部，禁深刺，防气胸。"},

    {"name": "膏肓", "code": "BL43", "meridian": M,
     "location": "在胸外侧区，第4胸椎棘突下，旁开3寸。",
     "anatomy_note": "浅层：第4胸神经后支的皮支；深层：斜方肌、菱形肌。⚠️深方近肺与胸膜。",
     "depth_limit": "斜刺0.5～0.8寸",
     "indications": ["咳嗽", "气喘", "肺痨", "健忘", "遗精", "虚劳羸瘦", "肩背痛"],
     "needling": "沿肩胛骨内缘向下斜刺；可灸（传统保健灸要穴）。",
     "contraindication": "⚠️⚠️胸背部，禁深刺，防气胸；孕妇禁针。", "self_moxa_safe": True},

    {"name": "合阳", "code": "BL55", "meridian": M,
     "location": "在小腿后区，腘横纹下2寸，腓肠肌内、外侧头之间。",
     "anatomy_note": "浅层：小腿后皮神经；深层：腓肠肌。",
     "depth_limit": "直刺0.8～1.2寸",
     "indications": ["腰脊强痛", "下肢痿痹", "疝气", "崩漏", "小腿转筋"],
     "needling": "直刺，针尖略向上；可灸。",
     "contraindication": "⚠️腓肠肌内可出现腓总神经分支，禁深刺猛刺。", "self_moxa_safe": True},
]

if __name__ == "__main__":
    raise SystemExit(apply(ITEMS, "膀胱经·腰骶下肢11穴"))
