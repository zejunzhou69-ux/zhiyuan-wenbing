r"""T2 临床高频补录 · 收尾 15 穴（补齐最后缺口）

承浆 CV24、身柱 GV12、孔最 LU7、经渠 LU8、扶突 LI18、
气户 ST13、库房 ST14、屋翳 ST15、膺窗 ST16、渊腋 GB22、
辄筋 GB23、日月 GB24、小海 HT3、承泣 ST1、冲门 SP12

注：T2 清单里的「通谷」即「足通谷 BL65」，库中已存在，不重复录入。

⚠️ 本批多在胸壁、腋窝、颈部——都是禁深刺区域，逐穴写明。
全部 verified=false。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from add_acupoints import apply  # noqa: E402

CHEST = "⚠️⚠️胸壁穴位，深方为胸腔与肺，禁深刺直刺、勿提插，以防气胸；孕妇禁针。"

ITEMS = [
    {"name": "承浆", "code": "CV24", "meridian": "任脉",
     "location": "在面部，下唇下方，下颌骨正中。",
     "anatomy_note": "浅层：颏动脉；深层：颏肌。⚠️面部血管丰富。",
     "depth_limit": "直刺0.3～0.5寸",
     "indications": ["口眼歪斜", "齿龈肿痛", "流涎", "暴喑", "癫痫"],
     "needling": "直刺，针尖略向上；可灸。",
     "contraindication": "⚠️面部禁深刺，防出血。"},

    {"name": "身柱", "code": "GV12", "meridian": "督脉",
     "location": "在脊柱后正中线上，第3胸椎棘突下凹陷中。",
     "anatomy_note": "浅层：第3胸神经后支的皮支；深层：棘突间韧带。⚠️深方为脊髓与胸腔。",
     "depth_limit": "斜刺0.5～1寸",
     "indications": ["咳嗽", "气喘", "癫痫", "腰脊强痛", "疔疮", "小儿体弱", "疳积"],
     "needling": "斜刺，针尖略向上；可灸（小儿常用灸法）。",
     "contraindication": "⚠️⚠️胸背部，禁深刺直刺，防刺入脊髓与胸腔。", "self_moxa_safe": True},

    {"name": "孔最", "code": "LU6", "meridian": "手太阴肺经",
     "location": "在前臂前区，腕横纹上7寸，桡骨外侧桡动脉搏动处。",
     "anatomy_note": "浅层：桡动脉的分支；深层：桡侧腕伸肌、旋前圆肌（桡神经浅支与深支）。⚠️穴下即桡动脉。",
     "depth_limit": "直刺0.5～0.8寸",
     "indications": ["咳血", "咳嗽", "气喘", "咽喉肿痛", "肘臂麻木", "痔疮"],
     "needling": "直刺，避开桡动脉；可灸。",
     "contraindication": "⚠️穴下有桡动脉，禁深刺、禁提插，防出血。", "self_moxa_safe": True},

    {"name": "经渠", "code": "LU8", "meridian": "手太阴肺经",
     "location": "在前臂前区，腕横纹上1寸，桡动脉搏动处。",
     "anatomy_note": "浅层：桡动脉的分支；深层：桡侧腕屈肌、旋前圆肌（桡神经浅支）。⚠️穴下即桡动脉。",
     "depth_limit": "直刺0.3～0.5寸",
     "indications": ["咳嗽", "气喘", "胸痛", "咽喉肿痛", "手腕痛", "掌中热", "无脉症"],
     "needling": "直刺，避开桡动脉；可灸。",
     "contraindication": "⚠️⚠️穴下即桡动脉（可摸到搏动），禁深刺、禁提插，防出血。", "self_moxa_safe": True},

    {"name": "扶突", "code": "LI18", "meridian": "手阳明大肠经",
     "location": "在颈外侧区，喉结旁开3寸，颈大肌与胸锁乳突肌的交界处。",
     "anatomy_note": "浅层：颈外静脉；深层：颈阔肌、胸锁乳突肌、颈总动脉与迷走神经。⚠️⚠️⚠️"
                     "穴下即颈总动脉（可摸到搏动），旁有迷走神经。",
     "depth_limit": "直刺0.3～0.5寸",
     "indications": ["咳嗽", "气喘", "咽喉肿痛", "暴喑", "瘰疬", "瘿疬", "口眼歪斜"],
     "needling": "直刺0.3～0.5寸，避开动脉；可灸。",
     "contraindication": "⚠️⚠️⚠️⚠️⚠️穴下即颈总动脉，禁深刺、禁提插捻转，可致大出血；孕妇禁针。"},

    {"name": "气户", "code": "ST13", "meridian": "足阳明胃经",
     "location": "在胸部，锁骨上缘，胸锁关节上缘，前正中线旁开4寸。",
     "anatomy_note": "浅层：胸锁乳突肌；深层：锁骨上、下动脉的分支、胸膜与肺尖。⚠️⚠️⚠️深方近肺尖。",
     "depth_limit": "斜刺0.3～0.5寸",
     "indications": ["咳嗽", "气喘", "呃逆", "咽喉肿痛", "瘿疬", "缺盆中痛"],
     "needling": "沿胸壁向下斜刺或平刺；可灸。",
     "contraindication": CHEST, "self_moxa_safe": True},

    {"name": "库房", "code": "ST14", "meridian": "足阳明胃经",
     "location": "在胸部，锁骨下缘，前正中线旁开4寸。",
     "anatomy_note": "浅层：胸大肌；深层：胸膜与肺。⚠️⚠️⚠️深方为胸腔。",
     "depth_limit": "斜刺0.3～0.5寸",
     "indications": ["咳嗽", "气喘", "咳唾脓血", "胸胁胀痛"],
     "needling": "沿胸壁向下斜刺或平刺；可灸。",
     "contraindication": CHEST, "self_moxa_safe": True},

    {"name": "屋翳", "code": "ST15", "meridian": "足阳明胃经",
     "location": "在胸部，锁骨下缘，前正中线旁开4寸，库房下一寸。",
     "anatomy_note": "浅层：胸大肌；深层：第3肋间肌、胸膜与肺。⚠️⚠️⚠️深方为胸腔。",
     "depth_limit": "斜刺0.3～0.5寸",
     "indications": ["咳嗽", "气喘", "胸胁胀痛", "乳痈"],
     "needling": "沿胸壁向下斜刺或平刺；可灸。",
     "contraindication": CHEST, "self_moxa_safe": True},

    {"name": "膺窗", "code": "ST16", "meridian": "足阳明胃经",
     "location": "在胸部，锁骨下缘，前正中线旁开4寸，屋翳下一寸。",
     "anatomy_note": "浅层：胸大肌；深层：第4肋间肌、胸膜与肺。⚠️⚠️⚠️深方为胸腔。",
     "depth_limit": "斜刺0.3～0.5寸",
     "indications": ["咳嗽", "气喘", "胸胁胀痛", "乳痈"],
     "needling": "沿胸壁向下斜刺或平刺；可灸。",
     "contraindication": CHEST, "self_moxa_safe": True},

    {"name": "渊腋", "code": "GB22", "meridian": "足少阳胆经",
     "location": "在胸外侧区，腋中线上，第4肋间隙，腋前、后皱襞两端连线的中点。",
     "anatomy_note": "浅层：胸背壁神经与胸外侧动脉的分支；深层：前锯肌、肋间肌。⚠️⚠️⚠️"
                     "深方为胸腔；腋窝内有腋动脉、腋静脉与臂丛神经。",
     "depth_limit": "斜刺0.5～0.8寸",
     "indications": ["胸满", "胁痛", "腋下肿", "臂痛不举", "乳痈", "悬钟(GB39)所主之病"],
     "needling": "沿胸壁斜刺或平刺；可灸。",
     "contraindication": "⚠️⚠️⚠️⚠️⚠️腋窝血管神经密集且深方为胸腔，禁深刺、禁提插，"
                        "以免损伤腋动静脉或致气胸；孕妇禁针。"},

    {"name": "辄筋", "code": "GB18", "meridian": "足少阳胆经",
     "location": "在胸外侧区，腋中线上，第4肋间隙，腋前皱襞前端与乳头连线的中点。",
     "anatomy_note": "浅层：胸外侧动脉的分支；深层：前锯肌、肋间肌。⚠️⚠️⚠️深方为胸腔。",
     "depth_limit": "斜刺0.3～0.5寸",
     "indications": ["胸胁痛", "气喘", "呕吐", "吞酸", "乳痈"],
     "needling": "沿胸壁斜刺或平刺；可灸。",
     "contraindication": CHEST, "self_moxa_safe": True},

    {"name": "日月", "code": "GB24", "meridian": "足少阳胆经",
     "location": "在胸部，第7肋间隙，前正中线旁开4寸。",
     "anatomy_note": "浅层：第7肋间神经的外侧皮支；深层：第7肋间肌、胸膜与肺。⚠️⚠️⚠️深方为胸腔。",
     "depth_limit": "斜刺0.5～0.8寸",
     "indications": ["黄疸", "胁肋疼痛", "呕吐", "吞酸", "呃逆", "消渴"],
     "needling": "沿胸壁斜刺或平刺；可灸。",
     "contraindication": CHEST, "self_moxa_safe": True},

    {"name": "小海", "code": "SI8", "meridian": "手太阳小肠经",
     "location": "在肘后区，尺骨鹰嘴与肱骨内上髁之间凹陷中。",
     "anatomy_note": "浅层：尺神经；深层：尺神经与尺动脉。⚠️⚠️⚠️穴下即尺神经本干，位置极浅且紧贴骨面。",
     "depth_limit": "直刺0.3～0.5寸",
     "indications": ["肘臂疼痛", "麻木", "癫痫", "瘰疬", "头项痛", "腰痛", "齿痛"],
     "needling": "直刺，针感为麻电样向小指侧放射；可灸。",
     "contraindication": "⚠️⚠️⚠️⚠️穴下即尺神经本干且紧贴骨面，禁深刺、禁提插捻转，"
                        "以免造成尺神经损伤（致手内侧感觉与运动障碍）。"},

    {"name": "承泣", "code": "ST1", "meridian": "足阳明胃经",
     "location": "在面部，眼球与眶下缘之间，瞳孔直下。",
     "anatomy_note": "浅层：眶下动脉的分支；深层：下直肌、下斜肌。⚠️⚠️⚠️"
                     "深方为眼球与眶下神经，针刺稍深即可能刺入眼球。",
     "depth_limit": "直刺0.3～0.5寸，或斜刺（承泣泣、球后、瞳子髎等眼周穴禁提插）",
     "indications": ["目赤肿痛", "流泪", "夜盲", "眼睑𥉜动", "口眼歪斜", "目翳", "视力减退"],
     "needling": "直刺，针尖略向眶内；沿眼球外缘进针；禁提插。",
     "contraindication": "⚠️⚠️⚠️⚠️⚠️⚠️眼区穴位，深方即为眼球，"
                        "严禁深刺、严禁提插捻转，否则可致眼球穿伤、玻璃体出血；"
                        "眼周皮肤菲薄，灸时防烫伤眼睑。"},

    {"name": "冲门", "code": "SP12", "meridian": "足太阴脾经",
     "location": "在腹股沟区，髂前上棘与腹股沟韧带外侧端连线的中点，动脉搏动处。",
     "anatomy_note": "浅层：旋髂浅支；深层：腹股沟韧带、髂外动脉与股神经。⚠️⚠️⚠️"
                     "穴下即髂外动脉（可摸到搏动）与股神经。",
     "depth_limit": "直刺0.5～0.8寸",
     "indications": ["腹痛", "疝气", "崩漏", "带下", "胎气上冲", "小便不利", "阴肿痛"],
     "needling": "直刺，避开动脉；可灸。",
     "contraindication": "⚠️⚠️⚠️⚠️⚠️穴下即髂外动脉，禁深刺、禁提插捻转，可致大出血；孕妇禁针。"},
]

if __name__ == "__main__":
    raise SystemExit(apply(ITEMS, "T2·收尾15穴"))
