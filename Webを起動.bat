@echo off
cd /d "%~dp0"

if not exist venv\Scripts\activate.bat (
    echo First-time setup: creating virtual environment...
    py -3 -m venv venv || python -m venv venv
    if errorlevel 1 (
        echo Could not create a virtual environment. Please install Python 3.
        pause
        exit /b 1
    )
)

call venv\Scripts\activate.bat

rem Reinstall when requirements.txt changed since the last install
fc /b requirements.txt venv\.requirements-installed >nul 2>&1
if errorlevel 1 (
    echo Setup: installing dependencies. This takes a few minutes...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Installation failed. Please check the error above.
        pause
        exit /b 1
    )
    copy /y requirements.txt venv\.requirements-installed >nul
)

echo.
set /p MOJI_PASSWORD=Password to protect the page (leave empty for none):
echo.

python web_main.py
pause
