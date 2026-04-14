#!/bin/bash
# ロボットアーム制御サーバー起動スクリプト

cd "$(dirname "$0")"

# 既存のプロセスを終了
echo "Checking for existing processes..."
pkill -f "python.*app.py" 2>/dev/null
sleep 1

# サーバーを起動
echo "Starting Robot Arm Control Server..."
python app.py
