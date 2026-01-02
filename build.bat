@echo off

call venv\Scripts\activate.bat

pyinstaller --onefile --noconsole --clean src\main.py

echo Build complete! Check the dist\ folder.
pause
