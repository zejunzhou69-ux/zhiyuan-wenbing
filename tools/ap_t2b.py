r"""T2 临床高频补录 · 第2批（上肢 18 穴）

大肠：二间 LI2、三间 LI3、阳溪 LI5、偏历 LI6、温溜 LI7、下廉 LI8、上廉 LI9
小肠：养老 SI6、支正 SI7、阳谷 SI5、颧髎 SI18
心包：郄门 PC4、间使 PC5、中冲 PC9
三焦：关冲 SJ1、液门 SJ2、支沟 SJ6、会宗 SJ7、天井 SJ10、
      清冷渊 SJ11、消泺 SJ12、臑会 SJ13、肩髎 SJ14

⚠️ 郄门、间使位于前臂内侧，穴下有正中神经与前臂血管，禁深刺。
全部 verified=false。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from add_acupoints import apply  # noqa: E402

ITEMS = [
    {"name": "二间", "code": "LI2", "meridian": "手阳明大肠经",
     "location": "在手指，第2掌指关节桡侧远端赤白肉际处。",
     "anatomy_note": "浅层：指背动脉的分支；深层：桡神经浅支。",
     "depth_limit": "直刺0.2～0.3寸",
     "indications": ["鼻衄", "齿痛", "咽喉肿痛", "目痛", "口眼歪斜", "腹胀"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️手部末梢，禁深刺。", "self_moxa_safe": True},

    {"name": "三间", "code": "LI3", "meridian": "手阳明大肠经",
     "location": "在手背，第2掌指关节桡侧近端凹陷中。",
     "anatomy_note": "浅层：指背动脉的分支；深层：第1骨间背侧肌、拇短伸肌（桡神经深支）。",
     "depth_limit": "直刺0.3～0.5寸",
     "indications": ["齿痛", "咽喉肿痛", "身热", "腹胀", "肠鸣", "目痛", "鼻衄"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️禁深刺，禁提插。", "self_moxa_safe": True},

    {"name": "阳溪", "code": "LI5", "meridian": "手阳明大肠经",
     "location": "在腕区，桡骨茎突远端，解剖学「鼻烟窝」凹陷中。",
     "anatomy_note": "浅层：桡动脉的分支；深层：拇短伸肌腱与拇长展肌腱（桡神经浅支）。⚠️鼻烟窝内有桡动脉与桡神经浅支，位置表浅。",
     "depth_limit": "直刺0.3～0.5寸",
     "indications": ["头痛", "目赤肿痛", "齿痛", "咽喉肿痛", "手腕痛", "腱鞘炎"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️⚠️鼻烟窝内桡动脉与桡神经浅支紧邻，禁深刺、禁提插。", "self_moxa_safe": True},

    {"name": "偏历", "code": "LI6", "meridian": "手阳明大肠经",
     "location": "在前臂，腕背侧远端横纹上3寸，阳溪与曲池连线的中点。",
     "anatomy_note": "浅层：桡动脉的分支；深层：桡侧腕伸肌、桡侧腕短伸肌（桡神经深支）。",
     "depth_limit": "直刺或斜刺0.3～0.5寸",
     "indications": ["耳鸣", "耳聋", "鼻衄", "手臂酸痛", "水肿", "小便不利"],
     "needling": "直刺或斜刺；可灸。",
     "contraindication": "⚠️禁深刺，防桡动脉损伤。", "self_moxa_safe": True},

    {"name": "温溜", "code": "LI7", "meridian": "手阳明大肠经",
     "location": "在前臂，腕背侧远端横纹上5寸，阳溪与曲池连线的中点。",
     "anatomy_note": "浅层：桡动脉的分支；深层：桡侧腕伸肌、桡侧腕短伸肌（桡神经深支）。",
     "depth_limit": "直刺或斜刺0.3～0.5寸",
     "indications": ["头痛", "面肿", "咽喉肿痛", "疔疮", "肩背酸痛", "肠鸣腹痛", "舌痛"],
     "needling": "直刺或斜刺；可灸。",
     "contraindication": "禁深刺，防桡动脉损伤。", "self_moxa_safe": True},

    {"name": "下廉", "code": "LI8", "meridian": "手阳明大肠经",
     "location": "在前臂，肘横纹下4寸，阳溪与曲池连线的中点。",
     "anatomy_note": "浅层：桡动脉的分支；深层：桡侧腕伸肌、桡侧腕短伸肌。",
     "depth_limit": "直刺或斜刺0.5～0.8寸",
     "indications": ["腹痛", "腹胀", "肘臂痛", "头痛", "眩晕"],
     "needling": "直刺或斜刺；可灸。",
     "contraindication": "禁深刺，防桡动脉损伤。", "self_moxa_safe": True},

    {"name": "上廉", "code": "LI9", "meridian": "手阳明大肠经",
     "location": "在前臂，肘横纹下3寸，阳溪与曲池连线的中点。",
     "anatomy_note": "浅层：桡动脉的分支；深层：桡侧腕伸肌、桡侧腕短伸肌（桡神经深支）。",
     "depth_limit": "直刺或斜刺0.5～0.8寸",
     "indications": ["肩臂酸痛", "麻木", "半身不遂", "肠鸣腹痛"],
     "needling": "直刺或斜刺；可灸。",
     "contraindication": "禁深刺，防桡动脉损伤。", "self_moxa_safe": True},

    {"name": "养老", "code": "SI6", "meridian": "手太阳小肠经",
     "location": "在前臂后区，腕背横纹上1寸，尺骨头桡侧凹陷中。",
     "anatomy_note": "浅层：尺背侧动脉的分支；深层：尺侧腕伸肌（尺神经手背支与尺神经深支的分支）。",
     "depth_limit": "直刺0.3～0.5寸",
     "indications": ["目视不明", "肩背肘臂酸痛", "急性腰痛", "落枕", "疔疮", "白内障"],
     "needling": "直刺，掌心向胸；可灸。",
     "contraindication": "⚠️禁深刺猛刺，防尺神经与血管损伤。", "self_moxa_safe": True},

    {"name": "支正", "code": "SI7", "meridian": "手太阳小肠经",
     "location": "在前臂后区，腕背侧远端横纹上5寸，尺骨尺侧与尺侧腕屈肌之间。",
     "anatomy_note": "浅层：尺动脉的分支；深层：尺侧腕屈肌（尺神经与尺动脉掌浅支伴行）。⚠️穴下有尺神经与尺动脉。",
     "depth_limit": "直刺0.5～0.8寸",
     "indications": ["头痛", "项强", "肘臂酸痛", "热病", "癫狂", "疣"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️⚠️穴下有尺神经与尺动脉，禁深刺、禁提插。", "self_moxa_safe": True},

    {"name": "阳谷", "code": "SI5", "meridian": "手太阳小肠经",
     "location": "在腕后区，尺骨茎突与三角骨之间的凹陷中。",
     "anatomy_note": "浅层：尺动脉掌浅支与腕背侧动脉的分支；深层：尺侧腕伸肌、尺侧腕屈肌（尺神经）。",
     "depth_limit": "直刺0.3～0.5寸",
     "indications": ["头痛", "目眩", "耳鸣", "耳聋", "齿痛", "癫狂痫", "腕痛"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️禁深刺，禁提插。", "self_moxa_safe": True},

    {"name": "颧髎", "code": "SI18", "meridian": "手太阳小肠经",
     "location": "在面部，颧骨上缘外侧凹陷中，目外眦直下。",
     "anatomy_note": "浅层：颧浅动脉与面动脉的分支；深层：颧小肌（有面神经颧支与上颌神经颧眶支）。⚠️面部，禁深刺。",
     "depth_limit": "直刺0.3～0.5寸",
     "indications": ["口眼歪斜", "眼睑𥉜动", "齿痛", "面痛", "颊肿", "目赤"],
     "needling": "直刺或斜刺；可灸。",
     "contraindication": "⚠️面部有面动脉分支，禁深刺猛刺。"},

    {"name": "郄门", "code": "PC4", "meridian": "手厥阴心包经",
     "location": "在前臂前区，腕横纹上5寸，掌长肌腱与桡侧腕屈肌腱之间。",
     "anatomy_note": "浅层：前臂浅静脉；深层：桡动脉掌浅支、掌长肌腱、桡侧腕屈肌腱。⚠️⚠️"
                     "正中神经位于本穴桡侧约1～2cm处，桡动脉掌浅支在桡侧。",
     "depth_limit": "直刺0.5～1寸",
     "indications": ["心痛", "心悸", "心烦", "咯血", "呕血", "疔疮", "癫痫"],
     "needling": "直刺，针感为麻电样；可灸。",
     "contraindication": "⚠️⚠️⚠️正中神经紧邻桡侧，针尖勿偏向桡侧，禁深刺、禁提插，"
                        "以免造成正中神经损伤（致拇指屈曲障碍）；孕妇禁针。"},

    {"name": "间使", "code": "PC5", "meridian": "手厥阴心包经",
     "location": "在前臂前区，腕横纹上3寸，掌长肌腱与桡侧腕屈肌腱之间。",
     "anatomy_note": "浅层：前臂浅静脉；深层：正中神经、掌长肌腱与桡侧腕屈肌腱。⚠️⚠️"
                     "正中神经在本穴桡侧紧邻，桡动脉掌浅支在其桡侧。",
     "depth_limit": "直刺0.5～1寸",
     "indications": ["心痛", "心悸", "胃痛", "呕吐", "热病", "疟疾", "癫狂痫"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️⚠️⚠️正中神经紧邻，针尖勿偏向桡侧，禁深刺、禁提插；孕妇禁针。"},

    {"name": "中冲", "code": "PC9", "meridian": "手厥阴心包经",
     "location": "在手指，中指末端最高点。",
     "anatomy_note": "浅层：掌指动脉的终末支；深层：屈指肌腱末端。⚠️指端末梢，血管神经丰富。",
     "depth_limit": "浅刺0.1寸或点刺出血",
     "indications": ["中风昏迷", "中暑", "小儿惊风", "舌强肿痛", "掌中热"],
     "needling": "浅刺或点刺出血；可灸。",
     "contraindication": "⚠️⚠️指端末梢，禁深刺（可致指端麻木或感染）；孕妇禁针。", "self_moxa_safe": True},

    {"name": "关冲", "code": "SJ1", "meridian": "手少阳三焦经",
     "location": "在手指，第4指末节尺侧，指甲根角侧上方0.1寸（指寸）。",
     "anatomy_note": "浅层：掌背动脉的指背动脉；深层：甲床。⚠️指端末梢。",
     "depth_limit": "浅刺0.1寸或点刺出血",
     "indications": ["头痛", "目赤", "耳聋", "咽喉肿痛", "热病", "昏厥"],
     "needling": "浅刺或点刺出血；可灸。",
     "contraindication": "⚠️禁深刺伤及甲床。", "self_moxa_safe": True},

    {"name": "液门", "code": "SJ2", "meridian": "手少阳三焦经",
     "location": "在手背，第4、5指间，指蹼缘上方赤白肉际凹陷中。",
     "anatomy_note": "浅层：掌背动脉的分支；深层：掌骨间背侧肌（有指背神经与掌背动脉）。",
     "depth_limit": "直刺0.5～0.8寸",
     "indications": ["头痛", "目赤", "耳鸣耳聋", "咽喉肿痛", "疟疾", "手臂痛", "精神分裂"],
     "needling": "直刺或向上斜刺；可灸。",
     "contraindication": "⚠️禁深刺，防掌背动脉损伤。", "self_moxa_safe": True},

    {"name": "支沟", "code": "SJ6", "meridian": "手少阳三焦经",
     "location": "在前臂后区，腕背侧远端横纹上3寸，尺骨与桡骨间隙的中点。",
     "anatomy_note": "浅层：前臂浅静脉；深层：尺侧腕伸肌、掌长肌腱（桡神经浅支与骨间前动脉）。",
     "depth_limit": "直刺0.5～1寸",
     "indications": ["便秘", "耳鸣耳聋", "暴喑", "胁肋痛", "热病", "瘰疬", "落枕"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️禁深刺，防骨间前动脉与桡神经损伤。", "self_moxa_safe": True},

    {"name": "会宗", "code": "SJ7", "meridian": "手少阳三焦经",
     "location": "在前臂后区，腕背侧远端横纹上3寸，尺骨的桡侧缘。",
     "anatomy_note": "浅层：前臂浅静脉；深层：尺侧腕伸肌、尺侧腕屈肌（尺神经与尺动脉掌浅支）。⚠️"
                     "穴下有尺神经与尺动脉掌浅支。",
     "depth_limit": "直刺0.5～0.8寸",
     "indications": ["耳聋", "癫痫", "上肢肌肤痛", "便秘"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️⚠️穴下有尺神经与尺动脉，禁深刺、禁提插。", "self_moxa_safe": True},

    {"name": "天井", "code": "SJ10", "meridian": "手少阳三焦经",
     "location": "在肘后区，屈肘，肘尖上1寸凹陷中。",
     "anatomy_note": "浅层：头静脉与贵要静脉的交通支；深层：肱三头肌（桡神经与尺神经的分支）。",
     "depth_limit": "直刺0.5～1寸",
     "indications": ["偏头痛", "耳聋", "瘰疬", "癫痫", "肘臂痛", "胁肋痛"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️禁深刺，防桡神经与血管损伤。", "self_moxa_safe": True},

    {"name": "清冷渊", "code": "SJ11", "meridian": "手少阳三焦经",
     "location": "在臂后区，肘尖与肩髎角连线上，肘尖上2寸。",
     "anatomy_note": "浅层：头静脉与贵要静脉的交通支；深层：肱三头肌（桡神经与尺神经的分支）。",
     "depth_limit": "直刺0.5～0.8寸",
     "indications": ["头痛", "目赤", "耳鸣耳聋", "肩臂痛不能举", "咽喉肿痛"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️禁深刺，防神经与血管损伤。", "self_moxa_safe": True},

    {"name": "消泺", "code": "SJ12", "meridian": "手少阳三焦经",
     "location": "在臂后区，肘尖与肩髎角连线上，肘尖上5寸。",
     "anatomy_note": "浅层：臂静脉的属支；深层：肱三头肌（桡神经与尺神经的分支）。",
     "depth_limit": "直刺0.5～0.8寸",
     "indications": ["头痛", "齿痛", "项强", "臂痛不能举", "癫痫"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️禁深刺，防神经与血管损伤。", "self_moxa_safe": True},

    {"name": "臑会", "code": "SJ13", "meridian": "手少阳三焦经",
     "location": "在臂后区，肩髎角下3寸，三角肌的后下缘。",
     "anatomy_note": "浅层：臂静脉的属支；深层：三角肌（桡神经与臂后皮神经）。",
     "depth_limit": "直刺0.5～0.8寸",
     "indications": ["瘿疬", "瘰疬", "上肢痹痛", "肩周炎"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️禁深刺，防神经损伤。", "self_moxa_safe": True},

    {"name": "肩髎", "code": "SJ14", "meridian": "手少阳三焦经",
     "location": "在三角肌区，肩峰外侧缘前端与肱骨大结节两骨间凹陷中。",
     "anatomy_note": "浅层：肩峰动脉的分支；深层：三角肌（腋神经与旋后肌）。⚠️"
                     "深方近肩关节囊与肱骨。",
     "depth_limit": "直刺0.5～0.8寸",
     "indications": ["肩臂疼痛不举", "上肢痿痹", "瘾疹"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️禁深刺，防刺入关节腔与腋神经损伤。", "self_moxa_safe": True},
]

if __name__ == "__main__":
    raise SystemExit(apply(ITEMS, "T2·上肢18穴"))
