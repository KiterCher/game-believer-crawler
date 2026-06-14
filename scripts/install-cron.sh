#!/bin/bash

# GameBeliever Crawler 定时任务安装脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PYTHON_PATH="$(which python3)"

echo "=== GameBeliever Crawler Cron Setup ==="
echo "Project directory: $PROJECT_DIR"
echo "Python path: $PYTHON_PATH"

# 创建日志目录
mkdir -p "$PROJECT_DIR/logs"

# 创建 cron 任务
CRON_CMD="0 2 * * * cd $PROJECT_DIR && $PYTHON_PATH scripts/schedule.py >> logs/cron.log 2>&1"

# 检查是否已存在 cron 任务
if crontab -l 2>/dev/null | grep -q "schedule.py"; then
    echo "Cron job already exists. Updating..."
    crontab -l 2>/dev/null | grep -v "schedule.py" | { cat; echo "$CRON_CMD"; } | crontab -
else
    echo "Adding new cron job..."
    (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
fi

echo "Cron job installed successfully!"
echo ""
echo "Schedule: Every day at 2:00 AM"
echo "Log file: $PROJECT_DIR/logs/cron.log"
echo ""
echo "To verify: crontab -l"
echo "To remove: crontab -l | grep -v 'schedule.py' | crontab -"
