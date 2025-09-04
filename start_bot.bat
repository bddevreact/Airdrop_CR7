@echo off
echo ========================================
echo    CR7 Token Bot - Quick Start
echo ========================================
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Choose an option:
echo 1. Setup Configuration (First time setup)
echo 2. Create .env file from template
echo 3. Test .env configuration
echo 4. Check deployment readiness
echo 5. Start CR7 Token Bot (Recommended)
echo.
set /p choice="Enter choice (1, 2, 3, 4, or 5): "
if "%choice%"=="1" (
    echo Starting Configuration Setup...
    python setup_config.py
    echo.
    echo Configuration complete! Now you can start the bot.
    echo Run this script again and choose option 5.
    pause
) else if "%choice%"=="2" (
    echo Creating .env file from template...
    python create_env.py
    echo.
    echo .env file created! Now you can start the bot.
    pause
) else if "%choice%"=="3" (
    echo Testing .env configuration...
    python test_env.py
    echo.
    echo Test complete! Check the results above.
    pause
) else if "%choice%"=="4" (
    echo Checking deployment readiness...
    python deploy.py
    echo.
    echo Deployment check complete! Check the results above.
    pause
) else if "%choice%"=="5" (
    echo Starting CR7 Token Bot...
    python main.py
) else (
    echo Invalid choice. Starting Configuration Setup...
    python setup_config.py
)
echo.
echo Press Ctrl+C to stop the bot
pause
