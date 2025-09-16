@echo off
SET SCRIPT_DIR=%~dp0

REM Start Docker Desktop
echo Starting Docker Desktop...
docker desktop start

REM Run Docker Compose
echo Running Docker Compose...
cd /d "%SCRIPT_DIR%"
docker compose up -d
timeout /t 2 > nul

REM Open browser to target URL
SET URL=http://localhost:1380/main.html
echo Opening %URL%
start "" "%URL%"
