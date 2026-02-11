@echo off
echo ======================================
echo   Stock Analyst - 启动服务
echo ======================================
echo.
echo 服务启动后，请访问：
echo   电脑端: http://localhost:5000
echo   手机端: http://192.168.2.8:5000
echo.
echo 按 Ctrl+C 停止服务
echo ======================================
echo.

cd /d "%~dp0"
python backend\app.py

pause
