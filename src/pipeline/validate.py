"""数据校验模块"""

from typing import Any

from pydantic import BaseModel


class ValidationResult(BaseModel):
    """校验结果"""

    is_valid: bool
    errors: list[str] = []
    warnings: list[str] = []


class DataValidator:
    """数据校验器"""

    def validate(self, data: dict[str, Any], model: type[BaseModel]) -> ValidationResult:
        """校验数据是否符合模型"""
        # TODO: 实现校验逻辑
        pass

    def validate_batch(
        self, data_list: list[dict[str, Any]], model: type[BaseModel]
    ) -> list[ValidationResult]:
        """批量校验数据"""
        return [self.validate(data, model) for data in data_list]
