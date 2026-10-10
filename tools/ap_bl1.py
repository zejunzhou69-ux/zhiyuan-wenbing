r"""足太阳膀胱经 · 头部 8 穴（BL3–BL10）

定位依据 GB/T 12346-2006 与规划教材《经络腧穴学》通行表述。
全部 verified=false，须对照教材原文核对。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from add_acupoints import apply  # noqa: E402

M = "足太阳膀胱经"
ITEMS = [
    {"name": "眉冲", "code": "BL3", "meridian": M,
     "location": "在头部，攒竹直上，入发际0.5寸。",
     "anatomy_note": "浅层：额动静脉的分支；深层：额神经的分支。",
     "depth_limit": "平刺0.3～0.5寸",
     "indications": ["头痛", "眩晕", "目赤肿痛", "鼻塞", "鼻衄", "癫痫"],
     "needling": "平刺，针尖向上；可灸（艾炷3壮或温针灸）。",
     "contraindication": "头皮部针刺宜浅，防刺入颅内；灸后注意避免烫伤头皮。"},

    {"name": "曲差", "code": "BL4", "meridian": M,
     "location": "在头部，前发际正中直上0.5寸，旁开1.5寸。",
     "anatomy_note": "浅层：额动静脉的分支；深层：额神经的分支。",
     "depth_limit": "平刺0.3～0.5寸",
     "indications": ["头痛", "目眩", "目痛", "视物不清", "鼻塞", "鼻衄"],
     "needling": "平刺，针尖向上或向内；可灸。",
     "contraindication": "不宜深刺，以防刺入颅内。"},

    {"name": "五处", "code": "BL5", "meridian": M,
     "location": "在头部，前发际正中直上1寸，旁开1.5寸。",
     "anatomy_note": "浅层：额动静脉的分支；深层：额神经的分支。",
     "depth_limit": "平刺0.3～0.5寸",
     "indications": ["头痛", "目眩", "癫痫", "发热恶寒"],
     "needling": "平刺，针尖向上；可灸。",
     "contraindication": "不宜深刺。"},

    {"name": "承光", "code": "BL6", "meridian": M,
     "location": "在头部，前发际正中直上2.5寸，旁开1.5寸。",
     "anatomy_note": "浅层：额动静脉的分支；深层：额神经的分支。",
     "depth_limit": "平刺0.3～0.5寸",
     "indications": ["头痛", "目眩", "鼻塞", "流涕", "热病无汗"],
     "needling": "平刺，针尖向上；可灸。",
     "contraindication": "不宜深刺。"},

    {"name": "通天", "code": "BL7", "meridian": M,
     "location": "在头部，前发际正中直上4寸，旁开1.5寸。",
     "anatomy_note": "浅层：额动静脉的分支；深层：额神经的分支。",
     "depth_limit": "平刺0.3～0.5寸",
     "indications": ["头痛", "眩晕", "鼻塞", "鼻衄", "鼻渊", "鼻渊", "中风"],
     "needling": "平刺，针尖向上；可灸。",
     "contraindication": "不宜深刺。"},

    {"name": "络却", "code": "BL8", "meridian": M,
     "location": "在头部，前发际正中直上5.5寸，旁开1.5寸。",
     "anatomy_note": "浅层：额动静脉的分支；深层：额神经的分支。",
     "depth_limit": "平刺0.3～0.5寸",
     "indications": ["头晕", "目视不明", "耳鸣", "癫狂", "鼻衄"],
     "needling": "平刺，针尖向上；可灸。",
     "contraindication": "不宜深刺。"},

    {"name": "玉枕", "code": "BL9", "meridian": M,
     "location": "在头部，横平枕外隆凸上缘，后发际正中旁开1.3寸。",
     "anatomy_note": "浅层：枕动静脉的分支；深层：枕大神经的分支。",
     "depth_limit": "平刺0.3～0.5寸",
     "indications": ["头项痛", "目眩", "鼻塞", "鼻衄", "头痛"],
     "needling": "平刺，针尖向下或向内；可灸。",
     "contraindication": "枕骨处骨质较厚，不宜深刺或重手法按压。"},

    {"name": "天柱", "code": "BL10", "meridian": M,
     "location": "在颈后区，横平第2颈椎棘突上际，斜方肌外缘凹陷中。",
     "anatomy_note": "浅层：斜方肌上端的静脉；深层：枕神经的分支、副神经、枕大神经。⚠️邻近枕骨大孔与椎动脉，禁止向深部大幅提插。",
     "depth_limit": "直刺0.5～1寸",
     "indications": ["感冒", "头痛", "项强", "落枕", "鼻塞", "目赤肿痛", "咽喉肿痛", "疟疾"],
     "needling": "直刺，针尖略朝向鼻尖；不宜久留针、不宜大幅提插；可灸。",
     "contraindication": "⚠️严禁深刺进入枕骨大孔（可伤及延髓）；禁大幅提插捻转（椎动脉在旁侧）；颈动脉粥样硬化者禁针。", "self_moxa_safe": True},
]

if __name__ == "__main__":
    raise SystemExit(apply(ITEMS, "膀胱经·头部8穴"))
