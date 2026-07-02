@echo off
setlocal
cd /d "%~dp0"

title ANC Demo - Learning Studio
set DEMO_MODE=conference
REM The launcher opens the browser tab itself (once), so tell the server not to —
REM otherwise the crash-restart loop below would spawn a new tab on every restart.
set DEMO_OPEN_BROWSER=0

echo ============================================================
echo    ANC Demo - Learning Studio  (conference mode)
echo ============================================================
echo.
echo Checking Claude login (needed for TRUE-LIVE generation)...
python preflight_auth.py
if errorlevel 1 (
  echo.
  echo   [!] Live generation will NOT work until the login above is fixed.
  echo   [!] The demo still runs using the pre-recorded fallback.
  echo   [!] For true-live: close this window, run   claude login   then reopen.
  echo.
  pause
)

REM Open the app in the default browser ONCE, a few seconds after the server starts.
start "" powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 4; Start-Process 'http://127.0.0.1:8001'"

:loop
echo.
echo Starting server on http://127.0.0.1:8001   (press Ctrl+C or close window to stop)
python demo_app.py
echo.
echo Server exited. Restarting in 2 seconds...   (close this window to stop for good)
timeout /t 2 >nul
goto loop
