"""材料数据模型"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel


class MaterialCategory(str, Enum):
    """材料类别枚举"""

    ASCENSION = "ascension"  # 角色晋级材料
    TRACE = "trace"  # 行迹材料
    EXP = "exp"  # 经验材料
    CREDIT = "credit"  # 信用点
    RELIC = "relic"  # 遗器经验
    LIGHTCONE = "lightcone"  # 光锥材料
    OTHER = "other"  # 其他


class Material(BaseModel):
    """材料模型"""

    id: str
    name: str
    name_en: str
    rarity: int  # 1-5
    category: MaterialCategory
    description: Optional[str] = None

    # 获取方式
    source: Optional[str] = None  # 获取来源

    # 用途
    used_for: list[str] = []  # 用途列表

    # 图片
    image_url: Optional[str] = None
