@echo off
title Hypersonic Nozzle - Setup

echo ============================================================
echo   Hypersonic Nozzle Design Tool - Automated Setup
echo ============================================================
echo.

REM ── Check that Python is installed ───────────────────────────
where py >nul 2>&1
if errorlevel 1 (
    where python >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Python was not found on this computer.
        echo.
        echo Please install Python 3.10 or newer from:
        echo     https://www.python.org/downloads/
        echo.
        echo Make sure to check "Add Python to PATH" during installation.
        echo.
        pause
        exit /b 1
    )
    set PYTHON_CMD=python
) else (
    set PYTHON_CMD=py -3.10
)

REM ── Create virtual environment ────────────────────────────────
echo [1/5] Creating virtual environment (.venv) ...
%PYTHON_CMD% -m venv .venv
if errorlevel 1 (
    echo.
    echo ERROR: Could not create virtual environment.
    echo        If Python 3.10 is not installed, try installing it from:
    echo            https://www.python.org/downloads/release/python-31011/
    echo.
    echo        Then re-run this script.
    echo.
    pause
    exit /b 1
)
echo        Done.
echo.

REM ── Activate the environment ──────────────────────────────────
echo [2/5] Activating virtual environment ...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo.
    echo ERROR: Could not activate virtual environment.
    echo        Try right-clicking this file and running as Administrator,
    echo        or run this command in PowerShell first:
    echo            Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
    echo.
    pause
    exit /b 1
)
echo        Done.
echo.

REM ── Upgrade pip ───────────────────────────────────────────────
echo [3/5] Upgrading pip (Python's package installer) ...
python -m pip install --upgrade pip setuptools wheel --quiet
echo        Done.
echo.

REM ── Install all Python packages ───────────────────────────────
echo [4/5] Installing required packages (this may take a few minutes) ...
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: Package installation failed.
    echo        Check your internet connection and try again.
    echo.
    pause
    exit /b 1
)
echo        Done.
echo.

REM ── Clone and install conturpy ────────────────────────────────
echo [5/5] Downloading and installing conturpy ...
where git >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Git was not found on this computer.
    echo.
    echo Please install Git from:
    echo     https://git-scm.com/downloads
    echo.
    echo Then re-run this script.
    echo.
    pause
    exit /b 1
)
if exist conturpy (
    echo        conturpy folder already exists, pulling latest changes ...
    cd conturpy
    git pull --quiet
    cd ..
) else (
    git clone https://github.com/noahess/conturpy conturpy --quiet
    if errorlevel 1 (
        echo.
        echo ERROR: Could not download conturpy.
        echo        Check your internet connection and try again.
        echo.
        pause
        exit /b 1
    )
)
cd conturpy
pip install -e . --quiet
if errorlevel 1 (
    echo.
    echo ERROR: Could not install conturpy.
    echo.
    cd ..
    pause
    exit /b 1
)
cd ..
echo        Done.
echo.

echo ============================================================
echo   Setup complete! Everything is installed.
echo ============================================================
echo.
echo NEXT STEPS:
echo   1. Open VS Code in this folder
echo   2. Press Ctrl+Shift+P, type "Python: Select Interpreter"
echo   3. Choose the one that shows ".venv" in its path
echo   4. Open Helium\runALL.py and press the Run button (triangle top-right)
echo.
pause
