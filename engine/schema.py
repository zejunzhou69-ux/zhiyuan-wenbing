"""知源问病 · 结构化知识的数据契约

所有知识条目必须符合这里定义的字段规范。
字段存在的意义：**让每一条知识都能被追溯到出处**，否则不允许用于输出结论。
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Literal


# ---------------------------------------------------------------- 溯源
@dataclass
class Provenance:
    """溯源信息。缺 source_book 的条目视为未验证知识。"""

    source_book: str = ""          # 来自哪本书，如《方剂学》
    source_chapter: str = ""       # 章节，如 "解表剂·辛温解表剂"
    source_page: str = ""          # 页码（PDF 有则必填）
    source_type: str = "textbook"  # textbook | classic | regulation | clinical_note
    verified: bool = False         # 是否已人工核对原文

    def is_usable(self) -> bool:
        """能否用于输出结论。"""
        return bool(self.source_book)


# ---------------------------------------------------------------- 方剂
@dataclass
class Herb:
    name: str
    dose_std: str = ""             # 教材常用量，如 "9g"
    role: str = ""                 # 君/臣/佐/使
    note: str = ""                 # 炮制、配伍要点、特有病机作用


@dataclass
class Formula:
    id: str
    name: str                      # 方名，如 "麻黄汤"
    aliases: list[str] = field(default_factory=list)
    category: str = ""             # 治法分类，如 "辛温解表剂"
    source_text: str = ""          # 出处原文，如 "《伤寒论》"
    functions: str = ""            # 功用
    indications: str = ""          # 主治
    syndrome_key: str = ""         # 关联证型 id（对到证型库）
    herbs: list[Herb] = field(default_factory=list)
    formula_meaning: str = ""      # 方义
    formula_analysis: str = ""     # 配伍解析（君臣佐使）
    similar_diff: str = ""         # 类方鉴别
    modifications: list[str] = field(default_factory=list)  # 加减
    cautions: list[str] = field(default_factory=list)       # 禁忌/注意
    provenance: Provenance = field(default_factory=Provenance)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------- 中药
@dataclass
class ChineseHerb:
    id: str
    name: str
    pinyin: str = ""
    category: str = ""             # 解表药/清热药/…（教材分类）
    nature: str = ""               # 性（寒热温凉平）
    flavor: str = ""               # 味
    meridian: list[str] = field(default_factory=list)   # 归经
    effects: list[str] = field(default_factory=list)     # 功效
    indications: str = ""          # 主治
    dosage: str = ""               # 用法用量
    contraindications: list[str] = field(default_factory=list)  # 禁忌/慎用
    toxicity: str = ""             # 毒性等级与中毒表现
    processing: list[str] = field(default_factory=list)  # 炮制品
    provenance: Provenance = field(default_factory=Provenance)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------- 穴位
@dataclass
class Acupoint:
    id: str
    name: str
    code: str = ""                 # 国标腧穴代码，如 LI4
    source_system: str = "经穴"   # 经穴 | 董氏奇穴 | 奇穴（其他）
    meridian: str = ""             # 所属经络（董氏奇穴可空）
    location: str = ""             # 体表定位（经穴：解剖描述；董氏：原书定位）
    anatomy_note: str = ""         # 解剖层次与毗邻（来自解剖学/局部表面解剖）
    depth_limit: str = ""          # 针刺深度上限
    indications: list[str] = field(default_factory=list)   # 主治
    needling: str = ""             # 操作要领
    contraindication: str = ""     # 禁忌
    self_moxa_safe: bool = False   # 是否适合家庭自行艾灸
    conflict_note: str = ""        # 与其他体系的定位冲突说明
    provenance: Provenance = field(default_factory=Provenance)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------- 证型
@dataclass
class Syndrome:
    id: str
    name: str                      # 如 "咳嗽·风寒袭肺证"
    system: str = ""               # 八纲/脏腑/气血津液/六经/卫气营血/三焦/经络
    category: str = ""             # 内科病名归属，如 "咳嗽"
    key_symptoms: list[str] = field(default_factory=list)   # 主症（诊断要点）
    secondary: list[str] = field(default_factory=list)      # 兼症
    tongue: str = ""               # 舌象
    pulse: str = ""                # 脉象
    mechanism: str = ""            # 病机
    treatment: str = ""            # 治法
    formula_ids: list[str] = field(default_factory=list)    # 主方
    acupoint_ids: list[str] = field(default_factory=list)   # 主穴
    differential: str = ""         # 鉴别
    provenance: Provenance = field(default_factory=Provenance)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------- 急症红旗
@dataclass
class RedFlag:
    id: str
    trigger: list[str] = field(default_factory=list)   # 命中关键词/描述
    category: str = ""             # 急症类别
    action: str = ""               # 必须采取的动作
    emergency: bool = True         # 是否急诊级

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_records(path) -> list[dict[str, Any]]:
    """读取 JSON 记录文件（UTF-8），返回原始 dict 列表。

    Windows 控制台默认 GBK，这里强制 UTF-8。
    """
    import json
    import os

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)