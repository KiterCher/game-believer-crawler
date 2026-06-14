"""光锥数据模型"""

from typing import Optional

from pydantic import BaseModel

from .character import Path


class LightConeStats(BaseModel):
    """光锥属性模型"""

    hp: int
    atk: int
    def_: int

    class Config:
        fields = {"def_": {"alias": "def"}}


class LightConePassive(BaseModel):
    """光锥被动效果"""

    name: str
    description: str
    superimpositions: list[str]  # 5个精炼等级的效果


class LightCone(BaseModel):
    """光锥模型"""

    id: str
    name: str
    name_en: str
    rarity: int  # 3, 4, or 5
    path: Path
    stats: LightConeStats
    passive: LightConePassive
    lore: Optional[str] = None

    # 图片
    image_url: Optional[str] = None
