@echo off
chcp 65001 >nul
cd /d "%~dp0"
py -m pip install -r requirements.txt
if errorlevel 1 (
  echo 安装依赖失败，请确认已安装 Python 3.10 或更新版本。
  pause
  exit /b 1
)
py main.py
pause
