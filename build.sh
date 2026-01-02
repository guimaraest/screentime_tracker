#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Run PyInstaller
pyinstaller pyinstaller --onefile --noconsole --clean src/main.py

echo "Build complete! Check the dist/ folder."
sss