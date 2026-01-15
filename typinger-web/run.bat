@echo off
REM run.bat - Typinger Web 実行スクリプト（Windows）

echo.
echo ===================================
echo Typinger Web - Launcher
echo ===================================
echo.

REM Pythonがインストールされているか確認
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or later from https://www.python.org
    pause
    exit /b 1
)

REM 仮想環境が存在するか確認
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM 仮想環境を有効化
call venv\Scripts\activate.bat

REM 依存パッケージをインストール
echo Installing dependencies...
pip install -q -r requirements.txt

REM セットアップスクリプトを実行
echo Setting up scenarios...
python setup_scenarios.py

REM 出力ディレクトリを作成
if not exist "output" mkdir output

REM Flask アプリケーションを実行
echo.
echo ===================================
echo Starting Typinger Web...
echo ===================================
echo.
echo Open your browser and go to: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
