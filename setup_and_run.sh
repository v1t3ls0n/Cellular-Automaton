#!/bin/bash

# Navigate to 'core' directory
echo "Navigating to 'core' directory..."
cd core || { echo "Failed to navigate to 'core' directory."; exit 1; }

# Check if the user wants to compile Cython modules
if [ "$1" == "--compile" ]; then
  echo "Compiling Cython files in 'core'..."
  python setup.py build_ext --inplace || { echo "Failed to compile Cython files."; exit 1; }
  echo "Compilation complete."
else
  echo "Skipping Cython compilation."
fi

# Return to the root directory
cd .. || { echo "Failed to navigate back to the root directory."; exit 1; }

# Run the main script
echo "Running main.py..."
python main.py || { echo "Failed to precompute main.py."; exit 1; }

echo "Script execution complete."
