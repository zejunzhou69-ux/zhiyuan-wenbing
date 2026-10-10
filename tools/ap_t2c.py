r"""T2 临床高频补录 · 第3批（胸腹 + 下肢 22 穴，收尾）

胸腹：鸠尾 CV15、巨阙 CV14、阴交 CV7、气冲 ST30、气穴 ST31、归来 ST29
肾经：大钟 KI4、水泉 KI5、交信 KI7、筑宾 KI9、阴谷 KI10、然谷 KI2
脾经：大都 SP2、漏谷 SP7、地机 SP8、箕门 SP2→SP2
胆经：阳交 GB36、外丘 GB36、厉兑 ST45、陷谷 ST43
小肠：少泽 SI1、前谷 SI2

⚠️ 气冲、气穴、归来位于下腹部与腹股沟，邻近髂外动脉与股神经，
禁深刺提插。全部 verified=false。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from add_acupoints import apply  # noqa: E402

ITEMS = [
    {"name": "鸠尾", "code": "CV15", "meridian": "任脉",
     "location": "在上腹部，剑胸结合部下1寸，前正中线上。",
     "anatomy_note": "浅层：腹壁浅静脉；深层：腹直肌及其鞘（剑突）。⚠️深方为腹腔。",
     "depth_limit": "直刺0.5～1寸",
     "indications": ["心痛", "心悸", "癫狂痫", "腹胀", "呃逆", "噎膈"],
     "needling": "直刺，针尖略向上；可灸。",
     "contraindication": "⚠️上腹部，禁深刺，防刺入腹腔损伤脏器；孕妇禁针。"},

    {"name": "巨阙", "code": "CV14", "meridian": "任脉",
     "location": "在上腹部，脐中上6寸，前正中线上。",
     "anatomy_note": "浅层：腹壁浅静脉；深层：腹直肌及其鞘、腹壁筋膜。⚠️⚠️深方为肝左叶与胃，禁深刺。",
     "depth_limit": "直刺0.5～1寸",
     "indications": ["心痛", "心悸", "心烦", "癫狂痫", "胃痛", "呕吐", "吞咽困难"],
     "needling": "直刺，针尖略向上；可灸。",
     "contraindication": "⚠️⚠️⚠️上腹部，深方为肝与胃，禁深刺提插；孕妇禁针。"},

    {"name": "阴交", "code": "CV7", "meridian": "任脉",
     "location": "在下腹部，脐中下1寸，前正中线上。",
     "anatomy_note": "浅层：腹壁浅静脉；深层：腹直肌及其鞘。⚠️深方为腹腔，邻近小肠与腹主动脉。",
     "depth_limit": "直刺0.5～1寸",
     "indications": ["腹痛", "水肿", "疝气", "月经不调", "带下", "遗精", "阴茎痛"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️⚠️下腹部，禁深刺，防刺入腹腔；孕妇禁针。"},

    {"name": "气冲", "code": "ST30", "meridian": "足阳明胃经",
     "location": "在腹股沟区，耻骨联合上缘，前正中线旁开2寸，动脉搏动处。",
     "anatomy_note": "浅层：腹壁浅静脉；深层：腹股沟韧带、髂外动脉与股神经。⚠️⚠️⚠️"
                     "穴下即髂外动脉（可摸到搏动）与股神经。",
     "depth_limit": "直刺0.3～0.5寸",
     "indications": ["腹痛", "疝气", "月经不调", "不孕", "阳痿", "阴肿", "卒疝"],
     "needling": "直刺0.3～0.5寸，或向内下斜刺；可灸。",
     "contraindication": "⚠️⚠️⚠️⚠️⚠️穴下即髂外动脉，禁深刺、禁提插捻转，"
                        "刺中可致大出血；孕妇禁针。"},

    {"name": "气穴", "code": "", "code_note": "编码待核：疑为 ST33，未敢凭记忆确定，须对照 GB/T 12346-2006 核对", "meridian": "足阳明胃经",
     "location": "在下腹部，脐中下3寸，前正中线旁开2寸。",
     "anatomy_note": "浅层：腹壁浅静脉；深层：腹直肌及其鞘。⚠️深方为腹腔。",
     "depth_limit": "直刺0.5～0.8寸",
     "indications": ["月经不调", "带下", "不孕", "小便不利", "泄泻", "腹痛"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️⚠️下腹部禁深刺，防刺入腹腔；孕妇禁针。"},

    {"name": "归来", "code": "ST29", "meridian": "足阳明胃经",
     "location": "在下腹部，脐中下4寸，前正中线旁开2寸。",
     "anatomy_note": "浅层：腹壁浅静脉；深层：腹直肌及其鞘。⚠️深方为腹腔，邻近乙状结肠。",
     "depth_limit": "直刺0.5～0.8寸",
     "indications": ["腹痛", "疝气", "闭经", "带下", "阴挺", "遗精"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️⚠️下腹部禁深刺；孕妇禁针。"},

    {"name": "大钟", "code": "KI4", "meridian": "足少阴肾经",
     "location": "在内踝后下方，跟骨上缘，跟腱附着部前缘凹陷中。",
     "anatomy_note": "浅层：胫后动脉的分支；深层：屈趾长肌（胫神经与胫后动脉）。⚠️跟腱与神经血管相邻。",
     "depth_limit": "直刺0.3～0.5寸",
     "indications": ["癃闭", "遗尿", "便秘", "咯血", "气喘", "痴呆", "足跟痛", "消渴"],
     "needling": "直刺，针尖略向内；可灸。",
     "contraindication": "⚠️⚠️胫后动脉与胫神经紧邻，禁深刺、禁提插。", "self_moxa_safe": True},

    {"name": "水泉", "code": "KI5", "meridian": "足少阴肾经",
     "location": "在足内侧，内踝后下方，太多溪直下1寸，跟骨结节的内侧凹陷中。",
     "anatomy_note": "浅层：胫后动脉的分支；深层：屈趾长肌（胫神经）。",
     "depth_limit": "直刺0.3～0.5寸",
     "indications": ["月经不调", "痛经", "经闭", "小便不利", "水肿"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️禁深刺，防胫后动脉与胫神经损伤。", "self_moxa_safe": True},

    {"name": "交信", "code": "KI8", "meridian": "足少阴肾经",
     "location": "在小腿内侧，内踝尖上2寸，胫骨内侧缘后际凹陷中。",
     "anatomy_note": "浅层：胫后动脉的分支；深层：趾长屈肌、胫骨后肌（胫神经与胫后动脉）。⚠️穴下有胫神经与胫后动脉。",
     "depth_limit": "直刺0.5～0.8寸",
     "indications": ["月经不调", "崩漏", "阴挺", "泄泻", "便秘", "睾丸肿痛"],
     "needling": "直刺0.5～0.8寸；可灸。",
     "contraindication": "⚠️⚠️穴下有胫神经与胫后动脉，禁深刺提插；孕妇禁针。", "self_moxa_safe": True},

    {"name": "筑宾", "code": "KI9", "meridian": "足少阴肾经",
     "location": "在小腿内侧，太溪直上5寸，比目鱼肌与跟腱移行处。",
     "anatomy_note": "浅层：胫后动脉的分支；深层：屈趾长肌、胫骨后肌（胫神经与胫后动脉）。",
     "depth_limit": "直刺0.5～0.8寸",
     "indications": ["癫狂", "疝气", "呕吐涎沫", "小腿内侧痛", "足跗肿痛"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️禁深刺，防胫神经与胫后动脉损伤。", "self_moxa_safe": True},

    {"name": "阴谷", "code": "KI10", "meridian": "足少阴肾经",
     "location": "在膝后区，腘横纹上，半腱肌肌腱外侧缘。",
     "anatomy_note": "浅层：腘静脉的属支；深层：半腱肌（胫神经与腓肠内侧皮神经）。⚠️"
                     "腘窝内有腘动脉、腘静脉与胫神经本干。",
     "depth_limit": "直刺0.5～1寸",
     "indications": ["阳痿", "疝气", "崩漏", "小便不利", "膝腘内侧痛"],
     "needling": "直刺，针尖略向外；可灸。",
     "contraindication": "⚠️⚠️⚠️腘窝内为腘动脉、腘静脉与胫神经本干，禁深刺、禁提插。", "self_moxa_safe": True},

    {"name": "然谷", "code": "KI2", "meridian": "足少阴肾经",
     "location": "在足内侧，足舟骨粗隆的下缘，赤白肉际处。",
     "anatomy_note": "浅层：足背动脉的分支（足底内侧动脉）；深层：拇展肌（足底内侧神经与胫神经）。⚠️足底动脉位置较深。",
     "depth_limit": "直刺0.5～0.8寸",
     "indications": ["遗精", "消渴", "泄泻", "咽喉肿痛", "足跗痛", "月经不调"],
     "needling": "直刺，针尖略向内；可灸。",
     "contraindication": "⚠️⚠️足底内侧动脉在深方，禁深刺，防动脉损伤。", "self_moxa_safe": True},

    {"name": "大都", "code": "SP2", "meridian": "足太阴脾经",
     "location": "在足内侧，第1跖趾关节的近端，赤白肉际处。",
     "anatomy_note": "浅层：足背动脉的分支；深层：拇展肌（足底内侧神经与胫神经）。",
     "depth_limit": "直刺0.3～0.5寸",
     "indications": ["腹胀", "泄泻", "热病无汗", "消渴", "足趾痛"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️禁深刺，防足背动脉损伤。", "self_moxa_safe": True},

    {"name": "漏谷", "code": "SP7", "meridian": "足太阴脾经",
     "location": "在小腿内侧，胫骨内侧缘后下方，内踝尖上8寸。",
     "anatomy_note": "浅层：小腿浅静脉；深层：比目鱼肌（胫神经与胫后动脉）。",
     "depth_limit": "直刺0.5～0.8寸",
     "indications": ["腹胀", "肠鸣", "下肢痿痹", "足胫痛"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️禁深刺，防胫神经与血管损伤。", "self_moxa_safe": True},

    {"name": "地机", "code": "SP8", "meridian": "足太阴脾经",
     "location": "在小腿内侧，胫骨内侧缘后下方，阴陵泉直下5寸。",
     "anatomy_note": "浅层：小腿浅静脉；深层：比目鱼肌（胫神经与胫后动脉）。",
     "depth_limit": "直刺0.5～0.8寸",
     "indications": ["痛经", "崩漏", "月经不调", "腹痛", "泄泻", "水肿"],
     "needling": "直刺，针尖略向上；可灸。",
     "contraindication": "⚠️禁深刺，防胫神经与血管损伤；孕妇禁针。", "self_moxa_safe": True},

    {"name": "箕门", "code": "SP11", "meridian": "足太阴脾经",
     "location": "在股前区，髌底内侧端与冲门的连线上1/3与下2/3交点处，长收肌与缝匠肌交角的动脉搏动处。",
     "anatomy_note": "浅层：股静脉的属支；深层：长收肌、缝匠肌（股神经与股动脉）。⚠️"
                     "穴下即股动脉（可摸到搏动），缝匠肌下为股静脉与股神经。",
     "depth_limit": "直刺0.3～0.5寸",
     "indications": ["小便不利", "遗尿", "腹股沟肿痛", "下肢痿痹"],
     "needling": "直刺0.3～0.5寸；可灸。",
     "contraindication": "⚠️⚠️⚠️⚠️穴下即股动脉，禁深刺、禁提插捻转，可致大出血；孕妇禁针。"},

    {"name": "阳交", "code": "GB36", "meridian": "足少阳胆经",  # 与丘墟(GB40)不同穴，编码不冲突
     "location": "在小腿外侧，外踝尖上7寸，腓骨后缘。",
     "anatomy_note": "浅层：腓浅静脉；深层：腓骨短肌（腓总神经与腓浅动脉）。⚠️腓总神经本干在此分出腓浅、腓深神经。",
     "depth_limit": "直刺0.5～0.8寸",
     "indications": ["胸胁胀满", "下肢痿痹", "癫狂", "失眠", "急惊风"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️⚠️腓总神经本干在腓骨后缘，针尖勿后偏，禁深刺、禁提插。", "self_moxa_safe": True},

    {"name": "外丘", "code": "GB37", "meridian": "足少阳胆经",
     "location": "在小腿外侧，外踝尖上7寸，腓骨前缘。",
     "anatomy_note": "浅层：腓浅动脉的分支；深层：腓骨长肌、腓骨短肌（腓浅神经）。",
     "depth_limit": "直刺0.5～0.8寸",
     "indications": ["颈项强痛", "胸胁胀痛", "下肢痿痹", "癫狂", "转筋"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️禁深刺，防腓浅神经与血管损伤。", "self_moxa_safe": True},

    {"name": "厉兑", "code": "ST45", "meridian": "足阳明胃经",
     "location": "在足趾，第2趾末节外侧，趾甲根角侧后方0.1寸（指寸）。",
     "anatomy_note": "浅层：趾背动脉的终末支；深层：趾骨与甲床。⚠️指端末梢。",
     "depth_limit": "浅刺0.1寸或点刺出血",
     "indications": ["鼻衄", "齿痛", "咽喉肿痛", "热病", "多梦", "癫狂", "足跗肿痛"],
     "needling": "浅刺或点刺出血；可灸。",
     "contraindication": "⚠️禁深刺伤及甲床。", "self_moxa_safe": True},

    {"name": "陷谷", "code": "ST43", "meridian": "足阳明胃经",
     "location": "在足背，第2、3跖骨间，第2跖趾关节近端凹陷中。",
     "anatomy_note": "浅层：第2跖背动脉的分支；深层：趾短伸肌、拇长伸肌腱（腓深神经）。",
     "depth_limit": "直刺0.3～0.5寸",
     "indications": ["面目浮肿", "肠鸣腹痛", "足背肿痛", "热病", "癫狂"],
     "needling": "直刺或斜刺，针尖向足心方向；可灸。",
     "contraindication": "⚠️⚠️禁深刺，防足背动脉与腓深神经损伤。", "self_moxa_safe": True},

    {"name": "少泽", "code": "SI1", "meridian": "手太阳小肠经",
     "location": "在手指，小指末节尺侧，指甲根角侧上方0.1寸（指寸）。",
     "anatomy_note": "浅层：掌背动脉的指背动脉；深层：甲床。⚠️指端末梢。",
     "depth_limit": "浅刺0.1寸或点刺出血",
     "indications": ["乳痈", "乳少", "昏迷", "热病", "头痛", "目翳", "咽喉肿痛"],
     "needling": "浅刺或点刺出血；可灸。",
     "contraindication": "⚠️禁深刺伤及甲床；孕妇禁针。", "self_moxa_safe": True},

    {"name": "前谷", "code": "SI2", "meridian": "手太阳小肠经",
     "location": "在手指，第5掌指关节尺侧远端赤白肉际凹陷中。",
     "anatomy_note": "浅层：指背动脉的分支；深层：小指展肌（尺神经手背支）。",
     "depth_limit": "直刺0.2～0.3寸",
     "indications": ["热病", "乳少", "头痛", "目痛", "耳鸣", "咽喉肿痛"],
     "needling": "直刺；可灸。",
     "contraindication": "⚠️手部末梢，禁深刺；孕妇禁针。", "self_moxa_safe": True},
]

if __name__ == "__main__":
    raise SystemExit(apply(ITEMS, "T2·胸腹与下肢22穴"))
