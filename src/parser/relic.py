"""遗器数据解析器"""

from typing import Any

from ..models.relic import Relic


class RelicParser:
    """遗器数据解析器"""

    def parse(self, raw_data: dict[str, Any]) -> Relic:
        """解析原始数据为遗器模型"""
        # TODO: 实现解析逻辑
        pass

    def parse_list(self, raw_data_list: list[dict[str, Any]]) -> list[Relic]:
        """解析多个遗器数据"""
        return [self.parse(data) for data in raw_data_list]
