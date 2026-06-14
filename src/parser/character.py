"""角色数据解析器"""

from typing import Any

from ..models.character import Character


class CharacterParser:
    """角色数据解析器"""

    def parse(self, raw_data: dict[str, Any]) -> Character:
        """解析原始数据为角色模型"""
        # TODO: 实现解析逻辑
        pass

    def parse_list(self, raw_data_list: list[dict[str, Any]]) -> list[Character]:
        """解析多个角色数据"""
        return [self.parse(data) for data in raw_data_list]
