@echo off
REM CR7 Token Bot - Production Deployment Script for Windows
REM This script handles the complete deployment process

echo 🚀 CR7 Token Bot - Production Deployment
echo ========================================

REM Check if .env file exists
if not exist ".env" (
    echo [ERROR] .env file not found!
    echo [WARNING] Please copy env_template.txt to .env and fill in your values
    echo [WARNING] Or copy production.env to .env for production settings
    pause
    exit /b 1
)

echo [INFO] Environment file found!

REM Create logs directory
echo [INFO] Creating logs directory...
if not exist "logs" mkdir logs

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed!
    echo [WARNING] Please install Docker Desktop to continue with containerized deployment
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose is not installed!
    echo [WARNING] Please install Docker Compose to continue
    pause
    exit /b 1
)

echo [INFO] Docker and Docker Compose are available!

REM Build and start the application
echo [INFO] Building Docker image...
docker-compose build

echo [INFO] Starting CR7 Token Bot...
docker-compose up -d

REM Wait for the service to be healthy
echo [INFO] Waiting for service to be healthy...
timeout /t 10 /nobreak >nul

REM Check if the service is running
docker-compose ps | findstr "Up" >nul
if errorlevel 1 (
    echo [ERROR] ❌ Failed to start CR7 Token Bot
    echo [WARNING] Check logs with: docker-compose logs
    pause
    exit /b 1
) else (
    echo [INFO] ✅ CR7 Token Bot is running successfully!
    echo [INFO] Health check endpoint: http://localhost:8000/health
    echo [INFO] Metrics endpoint: http://localhost:8000/metrics
    echo [INFO] View logs with: docker-compose logs -f
)

echo.
echo 🎉 Deployment completed successfully!
echo.
echo 📋 Useful commands:
echo   View logs:     docker-compose logs -f
echo   Stop bot:      docker-compose down
echo   Restart bot:   docker-compose restart
echo   Update bot:    docker-compose pull ^&^& docker-compose up -d
echo.
echo 🔍 Monitoring:
echo   Health check:  curl http://localhost:8000/health
echo   Metrics:       curl http://localhost:8000/metrics
echo.
pause
