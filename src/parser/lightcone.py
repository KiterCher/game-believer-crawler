"""光锥数据解析器"""

from typing import Any

from ..models.lightcone import LightCone


class LightConeParser:
    """光锥数据解析器"""

    def parse(self, raw_data: dict[str, Any]) -> LightCone:
        """解析原始数据为光锥模型"""
        # TODO: 实现解析逻辑
        pass

    def parse_list(self, raw_data_list: list[dict[str, Any]]) -> list[LightCone]:
        """解析多个光锥数据"""
        return [self.parse(data) for data in raw_data_list]
