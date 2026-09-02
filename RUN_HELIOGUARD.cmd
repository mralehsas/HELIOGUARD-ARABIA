@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
title HELIOGUARD ARABIA v1.0.1

echo ==================================================
echo        HELIOGUARD ARABIA v1.0.1
echo        Official Final - Resilient Space Weather Gateway
echo ==================================================
echo.

if not exist "HELIOGUARD_SERVER.py" (
  echo ERROR: HELIOGUARD_SERVER.py was not found.
  echo Keep all extracted files in the same folder.
  pause
  exit /b 1
)

where py >nul 2>nul
if %errorlevel%==0 (
  py -3 "HELIOGUARD_SERVER.py"
  goto :end
)

where python >nul 2>nul
if %errorlevel%==0 (
  python "HELIOGUARD_SERVER.py"
  goto :end
)

echo ERROR: Python was not found.
echo Install Python, then run this file again.
pause
exit /b 1

:end
if errorlevel 1 pause
endlocal
