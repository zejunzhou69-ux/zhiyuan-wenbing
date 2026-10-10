r"""T2 临床高频补录 · 第1批（督脉背部 + 头颈面部 24 穴）

督脉：灵台 GV17、中枢 GV8、至阳 GV9、筋缩 GV19、悬枢 GV13、脊中 GV6
颈面：天突 CV22、廉泉 CV23、气舍 ST11、完骨 GB12、头窍阴 GB11、
      瞳子髎 GB1、听会 GB2、丝竹空 GB23、巨髎 ST8、水沟 GV26、龈交 GV28
肩背：天宗 SI11、秉风 SI12、曲垣 SI13、臑俞 SI10、天髎 SI15

⚠️ 天突、廉泉、巨髎、水沟均在颈部/面部，邻近重要血管与神经，
禁忌逐穴写明。全部 verified=false。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from add_acupoints import apply  # noqa: E402

ITEMS = [
    {"name": "灵台", "code": "GV17", "meridian": "督脉",
     "location": "在脊柱后正中线上，第6胸椎棘突下凹陷中。",
     "anatomy_note": "浅层：第6胸神经后支的皮支；深层：棘突间韧带、棘突肌。⚠️深方为胸腔。",
     "depth_limit": "斜刺0.5～1寸",
     "indications": ["咳嗽", "气喘", "疟疾", "腰脊强痛", "疮疡"],
     "needling": "沿棘突向上斜刺；可灸。",
     "contraindication": "⚠️胸背部，禁深刺直刺，防刺入胸腔与脊髓。"},

    {"name": "中枢", "code": "GV8", "meridian": "督脉",
     "location": "在脊柱后正中线上，第10胸椎棘突下凹陷中。",
     "anatomy_note": "浅层：第10胸神经后支的皮支；深层：棘突间韧带。",
     "depth_limit": "斜刺0.5～1寸",
     "indications": ["黄疸", "呕吐", "腹满", "腰背强痛"],
     "needling": "斜刺；可灸。",
     "contraindication": "⚠️胸背部，禁深刺，防刺入胸腔与脊髓。"},

    {"name": "至阳", "code": "GV9", "meridian": "督脉",
     "location": "在脊柱后正中线上，第7胸椎棘突下凹陷中。",
     "anatomy_note": "浅层：第7胸神经后支的皮支；深层：棘突间韧带。",
     "depth_limit": "斜刺0.5～1寸",
     "indications": ["黄疸", "胸胁胀满", "咳嗽", "气喘", "脊强", "背痛"],
     "needling": "斜刺；可灸。",
     "contraindication": "⚠️胸背部，禁深刺，防刺入胸腔与脊髓。"},

    {"name": "筋缩", "code": "GV19", "meridian": "督脉",
     "location": "在脊柱后正中线上，第9胸椎棘突下凹陷中。",
     "anatomy_note": "浅层：第9胸神经后支的皮支；深层：棘突间韧带。",
     "depth_limit": "斜刺0.5～1寸",
     "indications": ["癫痫", "抽搐", "脊强", "胃痛", "黄疸"],
     "needling": "斜刺；可灸。",
     "contraindication": "⚠️胸背部，禁深刺，防刺入胸腔与脊髓。"},

    {"name": "悬枢", "code": "GV13", "meridian": "督脉",
     "location": "在脊柱后正中线上，第1腰椎棘突下凹陷中。",
     "anatomy_note": "浅层：第1腰神经后支的皮支；深层：棘突间韧带；深方为腰椎管。",
     "depth_limit": "直刺0.5～1寸",
     "indications": ["腹痛", "泄泻", "完谷不化", "腰脊强痛"],
     "needling": "直刺，针尖略向上；可灸。",
     "contraindication": "⚠️深方为腰管，禁深刺提插；孕妇禁针。", "self_moxa_safe": True},

    {"name": "脊中", "code": "GV6", "meridian": "督脉",
     "location": "在脊柱后正中线上，第11胸椎棘突下凹陷中。",
     "anatomy_note": "浅层：第11胸神经后支的皮支；深层：棘突间韧带。",
     "depth_limit": "斜刺0.5～1寸",
     "indications": ["黄疸", "泄泻", "痔疮", "脱肛", "小儿疳积", "癫痫"],
     "needling": "斜刺；可灸。",
     "contraindication": "⚠️胸背部，禁深刺，防刺入胸腔与脊髓。"},

    {"name": "天突", "code": "CV22", "meridian": "任脉",
     "location": "在颈前区，胸骨上窝中央，前正中线上。",
     "anatomy_note": "浅层：颈静脉弓、头臂干与胸锁乳突肌下端；深层：胸腺（成人已退化）。⚠️⚠️⚠️"
                     "胸骨上窝下为胸腺与头臂干、颈总动脉起始部，紧邻气管。",
     "depth_limit": "直刺0.2～0.3寸，或向胸骨上窝缘沿胸骨柄后缘向下刺入0.5～1寸",
     "indications": ["咳嗽", "气喘", "咽喉肿痛", "暴喑", "噎膈", "瘿疬", "梅核气"],
     "needling": "⚠️先直刺0.2～0.3寸确认入皮，再沿胸骨柄后缘向下刺入0.5～1寸；"
                 "或令患者仰卧抬颈，从天突向下沿胸骨柄后缘刺入；可灸。",
     "contraindication": "⚠️⚠️⚠️⚠️⚠️深方为胸腺、头臂干与颈总动脉起始部，"
                        "严禁大幅提插捻转、严禁直刺超过1寸，"
                        "否则可致大出血、喉部血肿甚至窒息；孕妇禁针。"},

    {"name": "廉泉", "code": "CV23", "meridian": "任脉",
     "location": "在颈前区，喉结上方，舌骨上缘凹陷中，前正中线上。",
     "anatomy_note": "浅层：舌下神经的分支；深层：舌骨舌肌、二腹肌（面神经分支）。⚠️⚠️⚠️"
                     "深方为会厌与喉口，针尖过深可误入气道。",
     "depth_limit": "直刺或斜刺0.5～1寸",
     "indications": ["舌强不语", "暴喑", "吞咽困难", "口舌生疮", "流涎", "梅核气", "暴喑失语"],
     "needling": "向舌根方向斜刺0.5～1寸，或直刺0.3～0.5寸；可灸。",
     "contraindication": "⚠️⚠️⚠️⚠️深方为会厌软骨与喉口，严禁深刺、禁提插，"
                        "否则可误入气道致呛咳窒息；禁灸宜慎灸；孕妇禁针。"},

    {"name": "气舍", "code": "ST11", "meridian": "足阳明胃经",
     "location": "在颈前区，胸锁乳突肌前缘，喉结旁开1.5寸。",
     "anatomy_note": "浅层：颈阔肌；深层：颈动脉鞘（颈总动脉与迷走神经）。⚠️⚠️⚠️"
                     "穴下即颈总动脉，搏动明显。",
     "depth_limit": "直刺0.3～0.5寸",
     "indications": ["咽喉肿痛", "瘿疬", "瘰疬", "颈项强痛", "呃逆", "气喘"],
     "needling": "直刺0.3～0.5寸，避开动脉；可灸。",
     "contraindication": "⚠️⚠️⚠️⚠️⚠️穴下即颈总动脉，严禁深刺、严禁提插捻转，"
                        "刺中可致颈部血肿、压迫气道甚至窒息；孕妇禁针。"},

    {"name": "完骨", "code": "GB12", "meridian": "足少阳胆经",
     "location": "在头部，耳后乳突的后下方凹陷中。",
     "anatomy_note": "浅层：耳后肌；深层：枕小神经、耳大神经（面神经分支）。⚠️"
                     "乳突内有乳突窦与面神经垂直段，深刺有风险。",
     "depth_limit": "直刺0.3～0.5寸",
     "indications": ["耳鸣", "耳聋", "齿痛", "口眼歪斜", "颈项强痛", "头痛", "癫痫"],
     "needling": "直刺，针尖略向前；可灸。",
     "contraindication": "⚠️乳突部深方有面神经与颅内结构，禁深刺、禁提插。", "self_moxa_safe": True},

    {"name": "头窍阴", "code": "GB11", "meridian": "足少阳胆经",
     "location": "在头部，乳突的后上方，从天冲至完骨的弧形连线的上1/3与下2/3交点处。",
     "anatomy_note": "浅层：耳后肌；深层：耳大神经、耳后动静脉。",
     "depth_limit": "直刺0.3～0.5寸",
     "indications": ["耳鸣", "耳聋", "头颈强痛", "偏头痛", "目赤肿痛", "胸胁痛"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️禁深刺，禁提插。", "self_moxa_safe": True},

    {"name": "瞳子髎", "code": "GB1", "meridian": "足少阳胆经",
     "location": "在面部，目外眦外侧0.5寸。",
     "anatomy_note": "浅层：颞浅动脉分支；深层：眼轮匝肌、颧面神经。⚠️⚠️⚠️"
                     "外眦部为眼区，球结膜菲薄，深刺可致眼球损伤。",
     "depth_limit": "平刺0.3～0.5寸",
     "indications": ["头痛", "目赤肿痛", "羞明流泪", "目翳", "青盲", "口眼歪斜"],
     "needling": "向眼外角方向平刺，禁提插；可灸（眼周皮肤薄，灸时注意温度）。",
     "contraindication": "⚠️⚠️⚠️⚠️⚠️眼区穴位，严禁提插捻转、严禁深刺，"
                        "否则可致眼球损伤、结膜出血；眼周皮肤菲薄，灸时防烫伤。"},

    {"name": "听会", "code": "GB2", "meridian": "足少阳胆经",
     "location": "在面部，耳屏间切迹与下颌骨髁突之间的凹陷中。",
     "anatomy_note": "浅层：颞浅动脉；深层：腮腺（有耳颞神经、面神经分支）。⚠️"
                     "前方有颞浅动脉，深刺可致出血。",
     "depth_limit": "直刺0.3～0.5寸",
     "indications": ["耳鸣", "耳聋", "聤耳", "齿痛", "口眼歪斜", "颞颔关节疼痛"],
     "needling": "直刺，针尖略向前；可灸。",
     "contraindication": "⚠️禁深刺、禁提插，防颞浅动脉出血。", "self_moxa_safe": True},

    {"name": "丝竹空", "code": "GB23", "meridian": "足少阳胆经",
     "location": "在面部，眉梢凹陷中。",
     "anatomy_note": "浅层：颞浅动脉分支；深层：眼轮匝肌（面神经颧支）。⚠️眼区。",
     "depth_limit": "平刺0.3～0.5寸",
     "indications": ["头痛", "目赤肿痛", "眼睑跳动", "牙痛", "癫痫"],
     "needling": "向眼外角方向平刺，禁提插；可灸。",
     "contraindication": "⚠️⚠️眼区，禁深刺提插，防眼球损伤；孕妇禁针。", "self_moxa_safe": True},

    {"name": "巨髎", "code": "ST8", "meridian": "足阳明胃经",
     "location": "在面部，横平鼻翼外缘，瞳孔直下。",
     "anatomy_note": "浅层：面动静脉的分支；深层：咬肌（有面神经颊支）。⚠️⚠️⚠️"
                     "穴下有面动脉，眶下动脉与神经，禁深刺。",
     "depth_limit": "直刺0.3～0.6寸",
     "indications": ["口眼歪斜", "眼睑𥉜动", "齿痛", "鼻衄", "唇颊肿", "口噤不语", "三叉神经痛"],
     "needling": "直刺或斜刺，避开面动脉；可灸。",
     "contraindication": "⚠️⚠️⚠️穴下为面动脉与眶下动脉，禁深刺猛刺，禁提插，防出血与眶内损伤。"},

    {"name": "水沟", "code": "GV26", "meridian": "督脉",
     "location": "在面部，人中沟的上1/3与中1/3交点处。",
     "anatomy_note": "浅层：上唇动脉；深层：口轮匝肌（有面神经下颌缘支）。⚠️上唇部血管丰富。",
     "depth_limit": "直刺0.3～0.5寸，或向上斜刺0.5～1寸",
     "indications": ["昏迷", "晕厥", "中风", "中暑", "癫狂痫", "牙关紧闭", "急性腰扭伤", "面瘫"],
     "needling": "直刺或向鼻尖方向斜刺，针感明显；可灸（间接灸）。",
     "contraindication": "⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️"
                        "⚠️本穴为急救要穴，但严禁用于「掐人中救昏迷」——"
                        "现代急救规范要求立即拨打120并执行心肺复苏，"
                        "掐人中不能替代现代急救，且有延误风险。"
                        "孕妇禁针。"},

    {"name": "龈交", "code": "GV28", "meridian": "督脉",
     "location": "在上唇内侧面，上唇系带与上唇内侧面交点处。",
     "anatomy_note": "浅层：上唇动静脉；深层：上颌骨、上唇系带。⚠️口腔黏膜，"
                     "操作不当易出血。",
     "depth_limit": "点刺出血或斜刺0.3～0.5寸",
     "indications": ["齿龈肿痛", "齿衄", "口臭", "鼻渊", "癫狂", "小儿时撮口瘰疬"],
     "needling": "向上斜刺0.3～0.5寸，或点刺出血；不灸。",
     "contraindication": "⚠️口腔内操作易出血，禁大幅提插；孕妇禁针。"},

    {"name": "天宗", "code": "SI11", "meridian": "手太阳小肠经",
     "location": "在肩胛区，肩胛骨冈中线与肩胛骨下角连线上1/3与下2/3交点凹陷中。",
     "anatomy_note": "浅层：斜方肌；深层：冈下肌（肩胛下动脉、肩胛上神经）。⚠️"
                     "深方为肩胛骨与胸腔后壁。",
     "depth_limit": "直刺或斜刺0.5～1寸",
     "indications": ["肩胛疼痛", "气喘", "乳痈", "乳癖", "项背强痛"],
     "needling": "直刺或向肩胛骨边缘斜刺；可灸。",
     "contraindication": "⚠️禁深刺，防刺入胸腔；孕妇禁针。", "self_moxa_safe": True},

    {"name": "秉风", "code": "SI12", "meridian": "手太阳小肠经",
     "location": "在肩胛区，腋后纹头直上，肩胛冈上窝中点。",
     "anatomy_note": "浅层：斜方肌；深层：冈下肌、圆肌（小圆肌、肩胛下动脉）。",
     "depth_limit": "直刺0.3～0.5寸",
     "indications": ["肩胛疼痛", "上肢酸麻", "项背强痛", "咳嗽"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️禁深刺，防刺入胸腔与肩胛下动脉。", "self_moxa_safe": True},

    {"name": "曲垣", "code": "SI13", "meridian": "手太阳小肠经",
     "location": "在肩胛区，肩胛冈内侧端上缘凹陷中。",
     "anatomy_note": "浅层：斜方肌；深层：冈上肌（肩胛上动脉、肩胛上神经）。",
     "depth_limit": "直刺0.3～0.5寸",
     "indications": ["肩胛拘挛疼痛", "上肢酸麻", "项背强痛"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️禁深刺，防刺入胸腔。", "self_moxa_safe": True},

    {"name": "臑俞", "code": "SI10", "meridian": "手太阳小肠经",
     "location": "在肩胛区，腋后纹头直上，肩胛冈下缘凹陷中。",
     "anatomy_note": "浅层：斜方肌；深层：冈下肌（肩胛下动脉、肩胛下神经）。⚠️"
                     "深方近肺与胸腔后壁。",
     "depth_limit": "直刺0.5～0.8寸",
     "indications": ["肩臂疼痛", "肩不举", "颈项强痛", "瘰疬"],
     "needling": "直刺或斜刺；可灸。",
     "contraindication": "⚠️⚠️禁深刺，防刺入胸腔与肺；孕妇禁针。", "self_moxa_safe": True},

    {"name": "天髎", "code": "SI15", "meridian": "手太阳小肠经",
     "location": "在肩胛区，肩胛骨上角骨际凹陷中。",
     "anatomy_note": "浅层：斜方肌；深层：冈上肌（肩胛上动脉、肩胛上神经）。⚠️"
                     "深方近肺与胸腔后壁。",
     "depth_limit": "直刺0.5～0.8寸",
     "indications": ["肩臂痛", "颈项强痛", "胸中烦满", "热病"],
     "needling": "直刺或斜刺；可灸。",
     "contraindication": "⚠️⚠️禁深刺，防刺入胸腔与肺；孕妇禁针。", "self_moxa_safe": True},
]

if __name__ == "__main__":
    raise SystemExit(apply(ITEMS, "T2·督脉与头颈面部24穴"))
