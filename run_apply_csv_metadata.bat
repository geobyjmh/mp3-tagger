@echo off
setlocal

set "PYTHON=python"
set "SCRIPT=%~dp0apply_csv_metadata.py"
%PYTHON% "%SCRIPT%"
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
    echo.
    echo Metadata processing failed with exit code %EXIT_CODE%.
)

pause
exit /b %EXIT_CODE%
