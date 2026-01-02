@echo off

call venv\Scripts\activate.bat

pyinstaller --onefile --clean src\main.py

echo Build complete! Check the dist\ folder.
pause
