@echo off
chcp 65001 >nul
title 饥荒联机版专用服务器配置工具

echo.
echo ========================================
echo    🎮 饥荒联机版专用服务器配置工具
echo ========================================
echo.

:: 检查Python
echo [1/3] 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python未安装或未添加到PATH
    echo 请访问 https://www.python.org/downloads/ 下载安装
    pause
    exit /b 1
)
echo ✅ Python环境正常

:: 检查tkinter
echo [2/3] 检查GUI模块...
python -c "import tkinter" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ tkinter模块缺失，正在安装...
    pip install tk
    if %errorlevel% neq 0 (
        echo ❌ tkinter安装失败
        pause
        exit /b 1
    )
)
echo ✅ GUI模块正常

:: 检查脚本文件
echo [3/3] 检查脚本文件...
if not exist "饥荒服务器配置工具.py" (
    echo ❌ 脚本文件不存在
    pause
    exit /b 1
)
echo ✅ 脚本文件存在

echo.
echo 🚀 启动配置工具...
echo.

python "饥荒服务器配置工具.py"

echo.
echo 程序已退出
pause