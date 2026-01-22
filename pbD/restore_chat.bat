@echo off
setlocal enabledelayedexpansion

echo ============================================
echo   Antigravity Chat RESTORE (from ZIP)
echo ============================================
echo.

set "SCRIPT_DIR=%~dp0"
set "GEMINI_DIR=%USERPROFILE%\.gemini\antigravity"

:: Find zip file
set "ZIP_FILE="
for %%F in ("%SCRIPT_DIR%chat_*.zip") do set "ZIP_FILE=%%F"

if "%ZIP_FILE%"=="" (
    set /p ZIP_FILE="Enter path to zip file: "
)

if not exist "%ZIP_FILE%" (
    echo Zip file not found: %ZIP_FILE%
    pause
    exit /b 1
)

echo Using: %ZIP_FILE%
echo.

:: Extract to temp
set "TEMP_DIR=%TEMP%\antigravity_restore"
rmdir /S /Q "%TEMP_DIR%" 2>nul
mkdir "%TEMP_DIR%"

echo Extracting...
powershell -Command "Expand-Archive -Path '%ZIP_FILE%' -DestinationPath '%TEMP_DIR%' -Force"

:: Get conversation ID
set /p CONV_ID=<"%TEMP_DIR%\conversation_id.txt"
echo Conversation ID: %CONV_ID%
echo.

:: Create directories
echo Creating directories...
if not exist "%GEMINI_DIR%\conversations" mkdir "%GEMINI_DIR%\conversations"
if not exist "%GEMINI_DIR%\annotations" mkdir "%GEMINI_DIR%\annotations"
if not exist "%GEMINI_DIR%\brain\%CONV_ID%" mkdir "%GEMINI_DIR%\brain\%CONV_ID%"

:: Restore files
echo Restoring conversation...
copy /Y "%TEMP_DIR%\conversations\%CONV_ID%.pb" "%GEMINI_DIR%\conversations\" >nul 2>nul

echo Restoring annotations...
copy /Y "%TEMP_DIR%\annotations\%CONV_ID%.pbtxt" "%GEMINI_DIR%\annotations\" >nul 2>nul

echo Restoring brain artifacts...
if exist "%TEMP_DIR%\brain\%CONV_ID%" (
    xcopy /E /Y /Q "%TEMP_DIR%\brain\%CONV_ID%\*" "%GEMINI_DIR%\brain\%CONV_ID%\" >nul 2>nul
)

:: Cleanup
rmdir /S /Q "%TEMP_DIR%" 2>nul

echo.
echo ============================================
echo   RESTORED to: %GEMINI_DIR%
echo ============================================
pause
