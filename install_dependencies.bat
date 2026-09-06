@echo off
setlocal

set "PYTHON=python"

echo Installing Python dependencies...
%PYTHON% -m pip install mutagen

if errorlevel 1 (
    echo.
    echo Dependency installation failed.
    pause
    exit /b 1
)

echo.
echo All dependencies installed successfully.
pause
exit /b 0
