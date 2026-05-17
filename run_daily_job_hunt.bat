@echo off
REM Daily Job Hunt Agent Runner
REM This script runs the job hunting agent every morning
REM 
REM To schedule this:
REM 1. Save as: E:\hireme\run_daily_job_hunt.bat
REM 2. Open Windows Task Scheduler (Win+R → taskschd.msc)
REM 3. Create Basic Task → Name: "Daily Job Hunt"
REM 4. Trigger: Daily at 9:00 AM
REM 5. Action: Program: cmd.exe, Args: /c E:\hireme\run_daily_job_hunt.bat
REM 6. Done!

setlocal enabledelayedexpansion

REM Navigate to project directory
cd /d E:\hireme

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Run daily job hunt
echo.
echo ════════════════════════════════════════════════════════════════
echo   DAILY JOB HUNT SESSION - %date% %time%
echo ════════════════════════════════════════════════════════════════
echo.

python main.py daily

REM If job hunt completed successfully
if %errorlevel% equ 0 (
    echo.
    echo ✅ Daily job hunt completed successfully!
    echo 📊 Check your email for the daily report.
    echo.
) else (
    echo.
    echo ❌ Job hunt encountered an error (code: %errorlevel%)
    echo.
)

REM Keep window open so you can see output (remove "pause" if running as scheduled task)
pause
