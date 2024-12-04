#!/bin/bash
set -e

echo "Using Python 3.11 for the build process..."
/c/Users/Studio/AppData/Local/Programs/Python/Python311/python.exe --version

echo "Step 1: Upgrading pip, setuptools, and wheel..."
/c/Users/Studio/AppData/Local/Programs/Python/Python311/python.exe -m pip install --upgrade pip setuptools wheel

echo "Step 2: Installing required Python libraries..."
/c/Users/Studio/AppData/Local/Programs/Python/Python311/python.exe -m pip install numpy noise matplotlib

echo "Step 3: Running PyInstaller to create the executable..."
/c/Users/Studio/AppData/Local/Programs/Python/Python311/python.exe -m pyinstaller --onefile \
    --add-data "config/*.py:config" \
    --add-data "core/*.py:core" \
    --add-data "display/*.py:display" \
    --add-data "utils/*.py:utils" \
    main.py

echo "Build process completed successfully!"
