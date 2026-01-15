#!/bin/bash
# run.sh - Typinger Web 実行スクリプト（macOS/Linux）

set -e

echo ""
echo "==================================="
echo "Typinger Web - Launcher"
echo "==================================="
echo ""

# Pythonがインストールされているか確認
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.8 or later from https://www.python.org"
    exit 1
fi

# 仮想環境が存在するか確認
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# 仮想環境を有効化
source venv/bin/activate

# 依存パッケージをインストール
echo "Installing dependencies..."
pip install -q -r requirements.txt

# セットアップスクリプトを実行
echo "Setting up scenarios..."
python3 setup_scenarios.py

# 出力ディレクトリを作成
mkdir -p output

# Flask アプリケーションを実行
echo ""
echo "==================================="
echo "Starting Typinger Web..."
echo "==================================="
echo ""
echo "Open your browser and go to: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""

python3 app.py
