r"""临床超高频补录 · 第1批（手足部 7 穴）

腕骨 SI5、通里 HT5、灵道 HT4、侠溪 GB43、阳辅 GB44、
足临泣 GB41、膝眼 EX-LE5

选取依据：临床取穴频率（治病用），非考试大纲。
定位依 GB/T 12346-2006 与规划教材通行表述，verified=false。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from add_acupoints import apply  # noqa: E402

ITEMS = [
    {"name": "腕骨", "code": "SI5", "meridian": "手太阳小肠经",
     "location": "在腕掌尺侧，第5掌骨桡侧与钩骨之间，尺侧腕屈肌腱的桡侧缘凹陷中。",
     "anatomy_note": "浅层：尺动脉掌深支的腕掌侧动脉；深层：尺侧腕屈肌（尺神经与尺动脉掌浅支伴行）。⚠️穴内有尺神经与尺动脉分支。",
     "depth_limit": "直刺0.3～0.5寸",
     "indications": ["头项强痛", "耳鸣", "目翳", "黄疸", "热病", "指挛腕痛", "落枕"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️尺动脉与尺神经在此经过，禁深刺、禁提插，以免伤及血管神经。", "self_moxa_safe": True},

    {"name": "通里", "code": "HT5", "meridian": "手少阴心经",
     "location": "在前臂前区，尺侧腕屈肌腱的桡侧缘，腕横纹上1寸。",
     "anatomy_note": "浅层：尺动脉掌浅支；深层：尺侧腕屈肌、尺神经。⚠️尺神经与尺动脉掌浅支在桡侧伴行。",
     "depth_limit": "直刺0.3～0.5寸",
     "indications": ["心悸", "怔忡", "暴喑", "舌强不语", "腕臂痛"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️尺神经紧邻，禁深刺、禁大幅提插。", "self_moxa_safe": True},

    {"name": "灵道", "code": "HT4", "meridian": "手少阴心经",
     "location": "在前臂前区，尺侧腕屈肌腱的桡侧缘，腕横纹上1.5寸。",
     "anatomy_note": "浅层：尺动脉掌浅支；深层：尺侧腕屈肌、尺神经。",
     "depth_limit": "直刺0.3～0.5寸",
     "indications": ["心痛", "心悸", "暴喑", "肘臂挛痛"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️尺神经紧邻，禁深刺。", "self_moxa_safe": True},

    {"name": "侠溪", "code": "GB43", "meridian": "足少阳胆经",
     "location": "在足背，第4、5跖骨间，第4跖骨底与第5跖骨底结合部之间的凹陷中。",
     "anatomy_note": "浅层：第4跖背动脉的分支；深层：趾短伸肌腱、跖长伸肌腱。⚠️足背有动脉，禁深刺。",
     "depth_limit": "直刺0.3～0.5寸",
     "indications": ["头痛", "眩晕", "耳鸣", "耳聋", "目外眦痛", "颊肿", "胸胁痛", "膝痛", "足跗肿痛", "热病", "癫痫"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️足背动脉分支，禁深刺。", "self_moxa_safe": True},

    {"name": "阳辅", "code": "GB44", "meridian": "足少阳胆经",
     "location": "在小腿外侧，第4跖骨底与第5跖骨底结合部的前下方凹陷中。",
     "anatomy_note": "浅层：第4跖背动脉的分支；深层：趾长伸肌腱、腓骨短肌。",
     "depth_limit": "直刺0.5～0.8寸",
     "indications": ["偏头痛", "目外眦痛", "腋下肿痛", "胸胁痛", "下肢痿痹", "足跗肿痛", "胆病"],
     "needling": "直刺，针尖略向上；可灸。",
     "contraindication": "禁深刺，以免伤及足背动脉。", "self_moxa_safe": True},

    {"name": "足临泣", "code": "GB41", "meridian": "足少阳胆经",
     "location": "在足背，第4跖骨底与第5跖底结合部的前方，第5跖长肌腱的外侧凹陷中。",
     "anatomy_note": "浅层：第4跖背动脉的分支；深层：趾短伸肌、跖长伸肌腱。⚠️穴下有腓骨短肌与足背动脉分支。",
     "depth_limit": "直刺0.3～0.5寸",
     "indications": ["偏头痛", "目赤肿痛", "胁肋痛", "乳痈", "瘰疬", "足跗肿痛", "热病", "月经不调", "带下"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️足背动脉分支，禁深刺、禁提插。", "self_moxa_safe": True},

    {"name": "膝眼", "code": "EX-LE5", "meridian": "经外奇穴",
     "location": "在膝部，屈膝，髌韧带两侧凹陷处。内侧称内膝眼，外侧称外膝眼。",
     "anatomy_note": "浅层：膝关节的动脉网；深层：膝关节囊。⚠️膝关节腔与半月板在前下方，禁深刺直刺。",
     "depth_limit": "向膝中斜刺0.5～1寸，或透刺对侧膝眼",
     "indications": ["膝痛", "膝关节炎", "鹤膝风", "腿痛", "脚气", "膝关节积液"],
     "needling": "屈膝位，向膝关节腔斜刺，可透内膝眼与外膝眼；可灸。",
     "contraindication": "⚠️⚠️⚠️严禁直刺深刺，以免刺入关节腔、感染或损伤半月板；宜向膝中斜刺。", "self_moxa_safe": True},
]

if __name__ == "__main__":
    raise SystemExit(apply(ITEMS, "临床高频·手足部7穴"))
