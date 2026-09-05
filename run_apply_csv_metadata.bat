@echo off
setlocal

set "PYTHON=python"
set "SCRIPT=%~dp0apply_csv_metadata.py"
set "MP3_DIR=C:\path\to\your\mp3-folder"
set "CSV_FILE=C:\path\to\your\tracks.csv"

if "%MP3_DIR%"=="" (
    echo Error: MP3 directory is required.
    exit /b 1
)

if "%CSV_FILE%"=="" (
    echo Error: CSV file path is required.
    exit /b 1
)

%PYTHON% "%SCRIPT%" "%MP3_DIR%" "%CSV_FILE%"
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
    echo.
    echo Metadata processing failed with exit code %EXIT_CODE%.
)

pause
exit /b %EXIT_CODE%
