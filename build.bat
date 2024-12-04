@echo off
REM Title: Build Script for PyInstaller
REM Author: Guy Vitelson
REM Date: Today's Date

REM Step 1: Set Python Path
set PYTHON_PATH=C:\Users\Studio\AppData\Local\Programs\Python\Python311
set SCRIPTS_PATH=%PYTHON_PATH%\Scripts

REM Step 2: Navigate to the Project Directory
echo Navigating to the project directory...
cd /d %~dp0

REM Step 3: Run PyInstaller to Create Executable
echo Running PyInstaller to create the executable...
"%SCRIPTS_PATH%\pyinstaller" --onefile ^
    --add-data "config/*.py;config" ^
    --add-data "core/*.py;core" ^
    --add-data "display/*.py;display" ^
    --add-data "utils/*.py;utils" ^
    main.py

REM Step 4: Notify Completion
if %errorlevel%==0 (
    echo Build process completed successfully!
    echo Executable created in the "dist" directory.
) else (
    echo Build process failed. Please check for errors.
)

pause
