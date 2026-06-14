"""定时任务脚本 - 用于服务器定时执行"""

import asyncio
import sys
import os
from datetime import datetime
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import load_config
from src.pipeline.updater import AutoUpdater
from src.utils.logger import setup_logger


async def run_scheduled_update():
    """运行定时更新"""
    setup_logger(level="INFO", log_file="logs/update.log")

    print(f"[{datetime.now().isoformat()}] Starting scheduled update...")

    config = load_config()
    updater = AutoUpdater(config)

    try:
        result = await updater.run_update(force=False)

        print(f"[{datetime.now().isoformat()}] Update complete:")
        print(f"  Characters: {result.get('characters', {})}")
        print(f"  Lightcones: {result.get('lightcones', {})}")

        return result

    except Exception as e:
        print(f"[{datetime.now().isoformat()}] Update failed: {e}")
        return {"error": str(e)}


def main():
    """主函数"""
    # 确保日志目录存在
    Path("logs").mkdir(exist_ok=True)

    # 运行更新
    result = asyncio.run(run_scheduled_update())

    # 返回退出码
    if "error" in result:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
