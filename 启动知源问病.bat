@echo off
chcp 65001 > nul
title 知源问病 · 中医辨证问诊
cd /d "%~dp0"

echo ============================================================
echo   知源问病 · 中医辨证问诊智能体
echo ============================================================
echo.

where python > nul 2>nul
if errorlevel 1 (
    echo [错误] 没找到 python，请先安装 Python 3.10 及以上并加入 PATH。
    pause
    exit /b 1
)

echo [1/2] 数据自检...
python tools\check_json.py --quiet
if errorlevel 1 (
    echo.
    echo [错误] 数据文件有语法错误，请先修复。
    pause
    exit /b 1
)
echo       数据 OK
echo.
echo [2/2] 启动服务...
echo.
echo   浏览器会自动打开 http://127.0.0.1:8787
echo   关闭本窗口即停止服务
echo.

:: 后台等待 2 秒再开浏览器，确保服务已就绪
start "" /b cmd /c "timeout /t 2 >nul & start "" http://127.0.0.1:8787"

python web\app.py

pause