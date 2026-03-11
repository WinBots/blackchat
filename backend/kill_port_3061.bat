@echo off
setlocal
set PORT=3061
echo Killing process(es) on port %PORT%...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%PORT% ^| findstr LISTENING') do (
  echo - taskkill /F /PID %%a
  taskkill /F /PID %%a >nul 2>nul
)
echo Done.
endlocal
