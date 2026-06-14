"""遗器数据模型"""

from typing import Optional

from pydantic import BaseModel


class RelicStat(BaseModel):
    """遗器属性"""

    type: str  # HP, ATK, DEF, SPD, etc.
    value: str  # 固定值或百分比
    is_main: bool = False  # 是否是主属性
    is_sub: bool = False  # 是否是副属性


class RelicSet(BaseModel):
    """遗器套装效果"""

    pieces: int  # 2 or 4
    name: str
    description: str


class Relic(BaseModel):
    """遗器模型"""

    id: str
    name: str
    name_en: str
    slot: str  # Head, Hands, Body, Feet, PlanarSphere, LinkRope
    rarity: int  # 3, 4, or 5
    set_name: str
    set_id: str

    # 套装效果（只有2件套和4件套效果）
    set_effects: list[RelicSet] = []

    # 主属性和副属性
    main_stats: list[RelicStat] = []
    sub_stats: list[RelicStat] = []

    # 图片
    image_url: Optional[str] = None
