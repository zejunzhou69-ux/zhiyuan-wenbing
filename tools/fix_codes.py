r"""知源问病 · 穴位编码与命名修正

修复两个实测发现的问题：

1) `EX-LE5` 编码被错误占用
   国标 EX-LE5 是「膝眼」，库里却给了「八正（八正穴说明）」。
   八正穴的正确编码是 EX-LE8。
   后果：补录膝眼时被幂等逻辑静默丢弃（code 已存在），膝眼实际缺失。

2) 穴名不统一
   「悬钟（绝骨）」应统一为「悬钟」，别名另存，
   否则用户按「悬钟」检索可能匹配不上。

顺带把 apply() 的幂等缺陷记在这里：原逻辑只判断 code 是否存在，
不判断该 code 对应的穴名是否一致，导致问题被静默掩盖。
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
F = ROOT / "data" / "acupoints.json"

# 正确的国标编码：八正穴 = EX-LE8
CODE_FIX = {"八正（八正穴说明）": "EX-LE8"}
# 命名统一：标准名（别名,）
NAME_FIX = {"悬钟（绝骨）": ("悬钟", ["绝骨"])}
# 这些 code 是「说明条目」占用的，不能代表真实穴位，需标注
NOTE_ENTRIES = {"八正（八正穴说明）", "涌泉引火（操作说明）",
                "足三里配中脘（说明）", "四神聪（附）"}


def main() -> int:
    data = json.loads(F.read_text(encoding="utf-8"))
    changed = 0

    for a in data["acupoints"]:
        # 1) 编码修正
        want = CODE_FIX.get(a["name"])
        if want and a.get("code") != want:
            print(f"  改码：{a['id']} {a['name']}：{a.get('code')} -> {want}")
            a["code"] = want
            changed += 1

        # 2) 命名统一：把括号别名挪到 alias 字段
        if a["name"] in NAME_FIX:
            new_name, aliases = NAME_FIX[a["name"]]
            print(f"  改名：{a['name']} -> {new_name}　别名 {aliases}")
            a["name"] = new_name
            a["alias"] = aliases
            changed += 1

        # 3) 说明条目标注，避免被误当作真实穴位引用
        if a["name"] in NOTE_ENTRIES and not a.get("note_entry"):
            a["note_entry"] = True
            changed += 1

    F.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n共修正 {changed} 处")

    # 复核：code 与 name 都应唯一
    codes = [a.get("code") for a in data["acupoints"] if a.get("code")]
    names = [a["name"] for a in data["acupoints"]]
    dup_c = [c for c in set(codes) if codes.count(c) > 1]
    dup_n = [n for n in set(names) if names.count(n) > 1]
    print(f"code 重复：{dup_c or '无'}")
    print(f"穴名重复：{dup_n or '无'}")

    # EX-LE5 现在应为空，膝眼待补
    le5 = [a["name"] for a in data["acupoints"] if a.get("code") == "EX-LE5"]
    print(f"EX-LE5 现状：{le5 or '已空出，可补录膝眼'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
