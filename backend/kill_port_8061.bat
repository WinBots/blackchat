@echo off
echo.
echo ========================================
echo  MATAR PROCESSOS NA PORTA 8061
echo ========================================
echo.

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8061 ^| findstr LISTENING') do (
    echo Matando processo PID: %%a
    taskkill /F /PID %%a >nul 2>&1
    if !errorlevel! equ 0 (
        echo [OK] Processo %%a finalizado
    ) else (
        echo [ERRO] Nao foi possivel finalizar %%a
    )
)

echo.
echo ========================================
echo  CONCLUIDO
echo ========================================
echo.
pause

