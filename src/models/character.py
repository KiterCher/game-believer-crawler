"""角色数据模型"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel


class Element(str, Enum):
    """属性枚举"""

    PHYSICAL = "Physical"
    FIRE = "Fire"
    ICE = "Ice"
    LIGHTNING = "Lightning"
    WIND = "Wind"
    QUANTUM = "Quantum"
    IMAGINARY = "Imaginary"


class Path(str, Enum):
    """命途枚举"""

    DESTRUCTION = "Destruction"
    HUNT = "Hunt"
    ERUDITION = "Erudition"
    HARMONY = "Harmony"
    NIHILITY = "Nihility"
    PRESERVATION = "Preservation"
    ABUNDANCE = "Abundance"


class Skill(BaseModel):
    """技能模型"""

    name: str
    type: str  # Basic, Skill, Ultimate, Talent, Technique
    description: str
    multiplier: Optional[str] = None
    energy_cost: Optional[int] = None


class Trace(BaseModel):
    """行迹模型"""

    id: str
    name: str
    description: str
    unlock_level: str  # A2, A4, A6


class TraceStat(BaseModel):
    """行迹属性加成"""

    type: str  # ATK%, HP%, etc.
    value: str  # 28%, 18%, etc.


class Eidolon(BaseModel):
    """星魂模型"""

    level: int  # 1-6
    name: str
    description: str


class CharacterStats(BaseModel):
    """角色属性模型"""

    hp: list[int]  # 5个等级的HP
    atk: list[int]  # 5个等级的ATK
    def_: list[int]  # 5个等级的DEF
    spd: int

    class Config:
        # 使用 def_ 而不是 def（Python 关键字）
        fields = {"def_": {"alias": "def"}}


class Character(BaseModel):
    """角色模型"""

    id: str
    name: str
    name_en: str
    rarity: int  # 4 or 5
    element: Element
    path: Path
    faction: str
    release_version: str
    release_date: Optional[str] = None
    description: str
    role: str
    tags: list[str]

    # 详细数据
    skills: list[Skill] = []
    traces: list[Trace] = []
    trace_stats: list[TraceStat] = []
    eidolons: list[Eidolon] = []
    stats: Optional[CharacterStats] = None

    # 图片
    avatar_url: Optional[str] = None
    splash_url: Optional[str] = None
