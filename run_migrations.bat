@echo off
REM Database Migration Runner for Windows
REM Executes Python migration script with proper error handling

echo Starting SERP Strategist Database Migrations...
echo.

REM Try different Python commands
python run_migrations.py %*
if %ERRORLEVEL% NEQ 0 (
    echo Python command failed, trying python3...
    python3 run_migrations.py %*
    if %ERRORLEVEL% NEQ 0 (
        echo Python3 command failed, trying py...
        py run_migrations.py %*
        if %ERRORLEVEL% NEQ 0 (
            echo.
            echo ERROR: Could not find Python interpreter
            echo Please ensure Python is installed and in your PATH
            echo.
            pause
            exit /b 1
        )
    )
)

echo.
echo Migration completed successfully!
pause