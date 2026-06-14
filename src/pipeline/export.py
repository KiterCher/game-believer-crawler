"""数据导出模块"""

import json
from pathlib import Path
from typing import Any, Union

from loguru import logger
from pydantic import BaseModel


class DataExporter:
    """数据导出器"""

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_json(self, data: BaseModel, filename: str) -> Path:
        """导出 Pydantic 模型为 JSON 文件"""
        output_path = self.output_dir / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data.model_dump(), f, indent=2, ensure_ascii=False)

        logger.debug(f"Exported: {output_path}")
        return output_path

    def export_json_file(self, data: dict[str, Any], filename: str) -> Path:
        """导出字典为 JSON 文件"""
        output_path = self.output_dir / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.debug(f"Exported: {output_path}")
        return output_path

    def export_batch_json(self, data_list: Union[list[BaseModel], list[dict]], directory: str) -> list[Path]:
        """批量导出为 JSON 文件"""
        paths = []
        for data in data_list:
            # 使用模型的 id 作为文件名
            if isinstance(data, BaseModel):
                filename = f"{data.id}.json" if hasattr(data, "id") else f"{len(paths)}.json"
                path = self.export_json(data, f"{directory}/{filename}")
            else:
                filename = f"{data.get('id', str(len(paths)))}.json"
                path = self.export_json_file(data, f"{directory}/{filename}")
            paths.append(path)

        logger.info(f"Exported {len(paths)} files to {directory}")
        return paths
