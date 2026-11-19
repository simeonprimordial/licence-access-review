
@echo off

cd /d "%~dp0"

call venv\Scripts\activate.bat

python main.py

if errorlevel 1 (
    echo Access review failed.
    exit /b 1
)

echo Access review completed.
exit /b 0
