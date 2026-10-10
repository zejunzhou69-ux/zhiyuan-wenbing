r"""修正国标编码错配（只修真错误，不动等价写法）

校验器报出 9 处，逐个核实后分两类：

真错误（会导致编码冲突或指向错误穴位）：
  头维  ST8 -> ST4   ST8 是巨髎，这正是补录巨髎时冲突检测报错的原因
  丘墟  GB40 -> GB36GB40 是已废的「悬仆」，国标丘墟为 GB36

等价写法（保留，不动）：
  大椎 DU14 = GV4、百会 DU20 = GV20、素髎 DU25 = GV25   督脉 DU/GV 两套编码等价
  外关 SJ5 = TE5、四渎 SJ9 = TE9                        三焦经 SJ/TE 两套编码等价
  定喘 EX-B1 = EX-BL1、夹脊 EX-B2 = EX-BL2             EX-B 是 EX-BL 的旧写法

盲目「统一编码」会把这些正确写法改错，所以只动真错误。
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
F = ROOT / "data" / "acupoints.json"

FIX = {"头维": "ST4", "丘墟": "GB36"}

EQUIV = {
    "大椎": ("DU14", "GV4"), "百会": ("DU20", "GV20"), "素髎": ("DU25", "GV25"),
    "外关": ("SJ5", "TE5"), "四渎": ("SJ9", "TE9"),
    "定喘": ("EX-B1", "EX-BL1"), "夹脊": ("EX-B2", "EX-BL2"),
}


def main() -> int:
    data = json.loads(F.read_text(encoding="utf-8"))
    n = 0
    for a in data["acupoints"]:
        want = FIX.get(a["name"])
        if want and a.get("code") != want:
            print(f"  修正 {a['id']} {a['name']}：{a['code']} -> {want}")
            a["code"] = want
            n += 1

    # 在 _meta 里记下编码体系说明，避免后人误以为这是错误
    meta = data.setdefault("_meta", {})
    meta["code_system"] = (
        "本库编码混用两套等价体系，均属规范写法，检索时两者都应能命中："
        "督脉 DU* = GV*（如大椎 DU14 = GV4）；"
        "三焦经 SJ* = TE*（如外关 SJ5 = TE5）；"
        "经外奇穴 EX-B* 为 EX-BL* 的旧写法。"
        "已按国标修正的错配：头维 ST8→ST4（原值与巨髎冲突）、丘墟 GB40→GB36。"
    )
    F.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n修正 {n} 处；已写入编码体系说明到 _meta.code_system")

    # 复核 ST8 / GB40 是否空出来
    aps = data["acupoints"]
    for c in ("ST8", "GB40", "GB36", "ST4"):
        who = [a["name"] for a in aps if a.get("code") == c]
        print(f"  {c}: {who or '(空)'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
