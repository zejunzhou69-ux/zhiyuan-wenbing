r"""补录膝眼（EX-LE5）

为什么单独一批：之前 ap_t1a.py 录膝眼时，EX-LE5 编码被
「八正（八正穴说明）」错误占用，幂等逻辑只判 code 是否存在，
就把膝眼静默丢弃了。现已由 fix_codes.py 把八正改回 EX-LE8，空出 EX-LE5。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from add_acupoints import apply  # noqa: E402

ITEMS = [
    {"name": "膝眼", "code": "EX-LE5", "meridian": "经外奇穴",
     "location": "在膝部，屈膝，髌韧带两侧凹陷处。内侧称内膝眼，外侧称外膝眼。",
     "anatomy_note": "浅层：膝关节动脉网；深层：膝关节囊。⚠️膝关节腔与半月板在关节腔内，"
                     "深刺可致关节腔感染或损伤半月板。",
     "depth_limit": "向膝中斜刺0.5～1寸，或透刺对侧膝眼",
     "indications": ["膝痛", "膝关节炎", "鹤膝风", "腿痛", "脚气", "膝关节积液", "膝痹"],
     "needling": "屈膝位，向膝关节腔斜刺，可由内膝眼透外膝眼（或反向）；可灸。",
     "contraindication": "⚠️⚠️⚠️严禁直刺深刺，以免刺入关节腔致感染或损伤半月板；"
                        "宜向膝中斜刺。孕妇禁针。", "self_moxa_safe": True},
]

if __name__ == "__main__":
    raise SystemExit(apply(ITEMS, "临床高频·膝眼"))
