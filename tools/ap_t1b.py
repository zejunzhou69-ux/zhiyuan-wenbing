r"""临床超高频补录 · 第2批（督脉与特定穴 6 穴）

悬钟 GB39、腰阳关 GV3、风府 GV16、哑门 GV15、阑尾 EX-LE7、胆囊 EX-LE6

⚠️ 风府、哑门位于枕骨大孔附近，为针刺风险最高的区域之一，
禁忌按解剖逐条写明。全部 verified=false。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from add_acupoints import apply  # noqa: E402

ITEMS = [
    {"name": "悬钟", "code": "GB39", "meridian": "足少阳胆经",
     "location": "在小腿外侧，外踝尖上3寸，腓骨前缘。",
     "anatomy_note": "浅层：腓动脉的分支；深层：腓骨短肌与长肌之间，腓总神经本干在稍后方（腓骨后缘）。",
     "depth_limit": "直刺0.5～0.8寸",
     "indications": ["颈项强痛", "半身不遂", "下肢痿痹", "痴呆", "癫狂", "耳鸣耳聋", "目赤肿痛", "胁肋痛", "疟疾", "落枕"],
     "needling": "直刺，针尖略向上；可灸。",
     "contraindication": "⚠️⚠️腓总神经本干在腓骨后缘，与穴相距约1.5cm，针尖勿向后偏，禁深刺、禁提插；孕妇禁针。", "self_moxa_safe": True},

    {"name": "腰阳关", "code": "GV3", "meridian": "督脉",
     "location": "在脊柱后正中线上，第4腰椎棘突下凹陷中。",
     "anatomy_note": "浅层：腰背筋膜；深层：棘突间韧带、棘突肌；深方为腰椎管。⚠️⚠️再深即达硬膜外腔，腰椎间盘突出急性期禁直刺深刺。",
     "depth_limit": "直刺0.5～1寸",
     "indications": ["腰骶疼痛", "下肢痿痹", "遗精", "阳痿", "月经不调", "带下", "泄泻", "痢疾"],
     "needling": "直刺，针尖略向上；可灸。",
     "contraindication": "⚠️⚠️⚠️深方为腰椎管与脊髓，禁深刺、禁提插，禁在腰椎间盘突出急性期直刺；孕妇禁针。", "self_moxa_safe": True},

    {"name": "风府", "code": "GV16", "meridian": "督脉",
     "location": "在项后区，枕骨上缘凹陷中。",
     "anatomy_note": "浅层：枕动脉的分支；深层：头夹肌（枕大神经、副神经、枕动脉在此交织）。⚠️⚠️⚠️枕骨大孔紧邻其下，深刺可经枕骨大孔入颅，损伤延髓。",
     "depth_limit": "直刺或向下斜刺0.5～1寸",
     "indications": ["头痛", "项强", "眩晕", "中风", "癫狂痫", "咽喉肿痛", "暴喑", "感冒"],
     "needling": "直刺或向下方斜刺，针尖朝向鼻尖方向；宜浅；可灸。",
     "contraindication": "⚠️⚠️⚠️⚠️枕骨大孔在该穴下方约1cm，深刺可刺入颅腔伤及延髓（可致呼吸骤停）；"
                        "严禁深刺、严禁大幅度提插捻转；"
                        "椎动脉型颈椎病、严重骨质疏松者禁针或极浅刺。", "self_moxa_safe": True},

    {"name": "哑门", "code": "GV15", "meridian": "督脉",
     "location": "在项后区，第2颈椎棘突上际凹陷中。",
     "anatomy_note": "浅层：枕动脉的分支；深层：项韧带；⚠️⚠️⚠️再深即达椎管，内有脊髓与椎动脉、椎静脉。",
     "depth_limit": "直刺或向下斜刺0.5～1寸",
     "indications": ["暴喑", "舌强不语", "癫狂痫", "头痛", "项强", "中风", "失眠", "鼻衄"],
     "needling": "直刺或向下方斜刺，针尖朝向口腔方向；宜浅；可灸。",
     "contraindication": "⚠️⚠️⚠️⚠️深方为椎管与脊髓（延髓下端），深刺可致瘫痪或呼吸停止；"
                        "严禁深刺、严禁提插；禁灸宜慎灸。", "self_moxa_safe": True},

    {"name": "阑尾", "code": "EX-LE7", "meridian": "经外奇穴",
     "location": "在小腿外侧，髌韧带外侧凹陷下5寸，胫骨前嵴外一横指。",
     "anatomy_note": "浅层：胫前动脉的分支、腓深神经；深层：胫骨前肌、趾长伸肌。⚠️穴下有胫前动脉与腓深神经。",
     "depth_limit": "直刺1～1.5寸",
     "indications": ["急慢性阑尾炎", "消化不良", "腹痛", "泄泻", "下肢痿痹"],
     "needling": "直刺，针尖略向内下方；可灸。",
     "contraindication": "⚠️⚠️⚠️阑尾炎属急腹症，本穴只作辅助，不能替代外科处理；禁深刺大幅提插（防胫前动脉、腓深神经损伤）；孕妇禁针。", "self_moxa_safe": True},

    {"name": "胆囊", "code": "EX-LE6", "meridian": "经外奇穴",
     "location": "在小腿外侧，腓骨小头直下2寸。",
     "anatomy_note": "浅层：腓动脉的分支；深层：腓长肌。",
     "depth_limit": "直刺1～1.5寸",
     "indications": ["急慢性胆囊炎", "胆石症", "胆道蛔虫症", "胁痛", "下肢痿痹", "坐骨神经痛"],
     "needling": "直刺，针尖略向内下方；可灸。",
     "contraindication": "⚠️⚠️⚠️⚠️胆囊炎、胆结石、胆道蛔虫均可危及生命，本穴只作辅助，"
                        "必须先外科处理；禁深刺猛刺；孕妇禁针。", "self_moxa_safe": True},
]

if __name__ == "__main__":
    raise SystemExit(apply(ITEMS, "临床高频·督脉与特定穴6穴"))
