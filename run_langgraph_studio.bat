@echo off
setlocal EnableExtensions
title LangGraph Studio - Week 16 Research Agent
cd /d "%~dp0"

set "STUDIO_URL=https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024"
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"

where uv >nul 2>nul
if errorlevel 1 (
    echo [ERROR] uv is not installed or not on PATH.
    echo Install it from https://docs.astral.sh/uv/ and try again.
    pause
    exit /b 1
)

if not exist ".env" (
    echo [ERROR] .env not found in "%CD%".
    echo Copy .env.example to .env and fill in your keys.
    pause
    exit /b 1
)

rem If the dev server is already running, just open Studio.
rem Exit codes: 0 = server ready, 2 = port busy but not ready, 1 = free.
powershell -NoProfile -Command "try { $r = Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:2024/ok' -TimeoutSec 2; if ($r.StatusCode -eq 200 -and $r.Content -match 'ok') { exit 0 } } catch { }; if (Get-NetTCPConnection -LocalPort 2024 -State Listen -ErrorAction SilentlyContinue) { exit 2 }; exit 1"

if errorlevel 2 goto port_busy
if errorlevel 1 goto start_server
goto already_running

:already_running
echo LangGraph dev server is already running on http://127.0.0.1:2024
echo Opening LangGraph Studio...
start "" "%STUDIO_URL%"
exit /b 0

:port_busy
echo [ERROR] Port 2024 is already in use, but the LangGraph server is not responding.
echo Wait a few seconds and run this file again, or stop the process on that port:
echo   Get-NetTCPConnection -LocalPort 2024 -State Listen ^| ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
pause
exit /b 1

:start_server
echo Starting the LangGraph dev server for the Week 16 research agent...
echo.
echo   Studio: %STUDIO_URL%
echo.
echo The first start can take ~30 seconds while the guardrail models load.
echo Press Ctrl+C to stop the server.
echo.

uv run --env-file .env langgraph dev --allow-blocking --port 2024
set "EXITCODE=%ERRORLEVEL%"

if not "%EXITCODE%"=="0" (
    echo.
    echo [ERROR] langgraph dev exited with code %EXITCODE%.
    pause
)

exit /b %EXITCODE%
