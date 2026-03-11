# Script para matar processos na porta 8061
Write-Host "🔍 Procurando processos na porta 8061..." -ForegroundColor Cyan

$connections = netstat -ano | findstr ":8061"

if ($connections) {
    Write-Host "✅ Encontrado(s) processo(s) na porta 8061:" -ForegroundColor Green
    Write-Host $connections
    
    # Extrair PIDs únicos
    $pids = $connections | ForEach-Object {
        if ($_ -match '\s+(\d+)\s*$') {
            $matches[1]
        }
    } | Select-Object -Unique | Where-Object { $_ -ne "0" }
    
    if ($pids) {
        foreach ($pid in $pids) {
            Write-Host "🔪 Matando processo PID: $pid" -ForegroundColor Yellow
            taskkill /PID $pid /F
        }
        Write-Host "✅ Processos finalizados!" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Nenhum PID válido encontrado" -ForegroundColor Yellow
    }
} else {
    Write-Host "✅ Nenhum processo encontrado na porta 8061" -ForegroundColor Green
}

Write-Host ""
Write-Host "Pressione qualquer tecla para sair..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

