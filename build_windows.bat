@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo [1/3] 安装建置工具...
py -m pip install -r requirements.txt pyinstaller
if errorlevel 1 goto failed
echo [2/3] 打包 Windows 程式...
py -m PyInstaller --noconfirm --clean --windowed --onefile --name CreamCatPet --add-data "assets;assets" main.py
if errorlevel 1 goto failed
echo [3/3] 完成！程式位于 dist\CreamCatPet.exe
echo 你可以将 CreamCatPet.exe 分享给其他 Windows 使用者。
pause
exit /b 0
:failed
echo 建置失败。请确认已安装 Python 3.10+，并连接网路安装依赖。
pause
exit /b 1
