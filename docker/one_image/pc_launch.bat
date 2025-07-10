@echo off
REM Start Docker Desktop
start Docker Desktop

echo Waiting for Docker engine to be ready...

:wait_docker
docker info >nul 2>&1
IF ERRORLEVEL 1 (
    timeout /t 3 >nul
    goto wait_docker
)

echo Docker is ready!
REM Now run your container
docker run --env-file "env1.env" --env-file "env2.env" -it "miguelgp13/rag-complete:latest"
pause
