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

if not exist venv\.deps-installed (
    echo First-time setup: installing dependencies. This takes a few minutes...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Installation failed. Please check the error above.
        pause
        exit /b 1
    )
    type nul > venv\.deps-installed
)

python main.py
if errorlevel 1 pause
