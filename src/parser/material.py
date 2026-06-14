"""材料数据解析器"""

from typing import Any

from ..models.material import Material


class MaterialParser:
    """材料数据解析器"""

    def parse(self, raw_data: dict[str, Any]) -> Material:
        """解析原始数据为材料模型"""
        # TODO: 实现解析逻辑
        pass

    def parse_list(self, raw_data_list: list[dict[str, Any]]) -> list[Material]:
        """解析多个材料数据"""
        return [self.parse(data) for data in raw_data_list]
