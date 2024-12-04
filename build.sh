#!/bin/bash

# Exit the script on any error
set -e

echo "Step 1: Installing required Python libraries..."
pip install numpy==1.23.5 noise==1.2.3 matplotlib==3.7.2 pyinstaller

echo "Step 2: Running PyInstaller to create the executable..."

# PyInstaller command
pyinstaller --onefile --noconsole \
    --add-data "config/*.py:config" \
    --add-data "core/*.py:core" \
    --add-data "display/*.py:display" \
    --add-data "utils/*.py:utils" \
    main.py

echo "Step 3: Compilation complete!"
echo "Executable generated in the 'dist' folder: dist/main.exe"

# Optional: Check for UPX and compress the executable
if command -v upx &> /dev/null; then
    echo "UPX found. Compressing the executable..."
    upx dist/main.exe
    echo "Compression complete."
else
    echo "UPX not found. Skipping compression."
fi

echo "Step 4: Build process completed successfully!"
