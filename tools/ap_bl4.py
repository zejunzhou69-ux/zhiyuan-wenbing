r"""足太阳膀胱经 · 小腿与足部 11 穴

BL56 承筋、BL58 飞扬、BL59 跗阳、BL61 仆参、BL63 束骨、
BL64 京骨、BL65 足通谷、BL66 至阴、BL33x 秩边（已有，跳过）、
BL57承山（已有，跳过）、BL60昆仑（已有，跳过）

本批 8 穴，另附 3 个易漏穴：BL55x 飞扬…
实际录入：承筋、飞扬、跗阳、仆参、束骨、京骨、足通谷、至阴 = 8 穴
全部 verified=false。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from add_acupoints import apply  # noqa: E402

M = "足太阳膀胱经"

ITEMS = [
    {"name": "承筋", "code": "BL56", "meridian": M,
     "location": "在小腿后区，腘横纹下5寸，腓肠肌两肌腹之间。",
     "anatomy_note": "浅层：小腿后皮神经；深层：腓肠肌、比目鱼肌。",
     "depth_limit": "直刺0.5～1寸",
     "indications": ["小腿痛", "转筋", "痔疾", "腰背拘急"],
     "needling": "直刺，针尖略向上；可灸。",
     "contraindication": "⚠️腓肠肌内可遇腓总神经分支，禁深刺猛刺。", "self_moxa_safe": True},

    {"name": "飞扬", "code": "BL58", "meridian": M,
     "location": "在小腿后区，昆仑直上7寸，腓肠肌两肌腹之间。",
     "anatomy_note": "浅层：小腿后皮神经；深层：腓肠肌、比目鱼肌。",
     "depth_limit": "直刺0.7～1寸",
     "indications": ["头痛", "项强", "腰骶疼痛", "下肢痿痹", "痔疾"],
     "needling": "直刺；可灸。",
     "contraindication": "禁深刺，以免损伤腓总神经分支。", "self_moxa_safe": True},

    {"name": "跗阳", "code": "BL59", "meridian": M,
     "location": "在小腿后区，昆仑直上3寸，腓骨与腓肠肌之间。",
     "anatomy_note": "浅层：小腿后皮神经；深层：腓骨短肌、腓总神经干。⚠️腓总神经本干在穴下。",
     "depth_limit": "直刺0.8～1.2寸",
     "indications": ["头重头痛", "腰骶疼痛", "下肢痿痹", "外踝肿痛"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️⚠️穴下为腓总神经本干，禁深刺、禁强刺激，以免神经损伤。", "self_moxa_safe": True},

    {"name": "仆参", "code": "BL61", "meridian": M,
     "location": "在踝区，昆仑直下，跟骨外侧，赤白肉际处。",
     "anatomy_note": "浅层：足背动脉的分支；深层：腓骨长肌腱与跟腱之间。⚠️腓总神经在外踝下方的腓骨肌下沟内，位置表浅。",
     "depth_limit": "直刺0.3～0.5寸",
     "indications": ["下肢痿痹", "足跟肿痛", "癫痫", "狂言"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️⚠️外踝处腓总神经位置极浅，禁深刺、禁提插，防神经损伤。", "self_moxa_safe": True},

    {"name": "束骨", "code": "BL63", "meridian": M,
     "location": "在踝区，第5跖骨粗隆前下方，赤白肉际处。",
     "anatomy_note": "浅层：足背动脉的分支；深层：腓骨短肌。",
     "depth_limit": "直刺0.3～0.5寸",
     "indications": ["腰脊强痛", "下肢痿痹", "外踝肿痛", "癫痫"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️足背有动脉，禁深刺。", "self_moxa_safe": True},

    {"name": "京骨", "code": "BL64", "meridian": M,
     "location": "在跖区，第5跖骨粗隆前下方，赤白肉际处。",
     "anatomy_note": "浅层：足背动脉的分支；深层：腓骨短肌。",
     "depth_limit": "直刺0.3～0.5寸",
     "indications": ["头痛", "项强", "目翳", "癫痫", "腰腿痛"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️足背动脉，禁深刺。", "self_moxa_safe": True},

    {"name": "足通谷", "code": "BL65", "meridian": M,
     "location": "在足区，第5跖趾关节的近端，赤白肉际处。",
     "anatomy_note": "浅层：足背动脉的分支；深层：跖趾关节。",
     "depth_limit": "直刺0.2～0.3寸",
     "indications": ["头项痛", "目眩", "鼻衄", "癫狂", "足跗肿痛"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️足趾部禁深刺，以免伤及趾骨与血管。", "self_moxa_safe": True},

    {"name": "至阴", "code": "BL66", "meridian": M,
     "location": "在足趾，小趾末节内侧，趾甲根角侧后方0.1寸（指寸）。",
     "anatomy_note": "浅层：足背动脉的趾背动脉；深层：小趾甲床。⚠️趾端末梢血管丰富。",
     "depth_limit": "浅刺0.1寸或点刺出血",
     "indications": ["胎位不正", "滞产", "头痛", "目痛", "鼻衄", "鼻渊", "目翳", "经量过多"],
     "needling": "浅刺或点刺出血；可灸。",
     "contraindication": "⚠️⚠️⚠️孕妇禁针（传统用于矫正胎位，但孕妇禁用）；禁深刺伤及甲床。", "self_moxa_safe": True},
]

if __name__ == "__main__":
    raise SystemExit(apply(ITEMS, "膀胱经·小腿足部8穴"))
