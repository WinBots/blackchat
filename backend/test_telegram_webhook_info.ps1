param(
  [string]$BaseUrl = $env:BLACKCHAT_BASE_URL,
  [string]$Token = $env:BLACKCHAT_TOKEN,
  [int]$ChannelId = $(if ($env:BLACKCHAT_CHANNEL_ID) { [int]$env:BLACKCHAT_CHANNEL_ID } else { 2 }),
  [switch]$Sync
)

if ([string]::IsNullOrWhiteSpace($BaseUrl)) {
  $BaseUrl = 'https://app.blackchatpro.com'
}
$BaseUrl = $BaseUrl.TrimEnd('/')

if ([string]::IsNullOrWhiteSpace($Token)) {
  Write-Host ''
  Write-Host 'Informe o Bearer token (sem a palavra Bearer):' -ForegroundColor Yellow
  $Token = Read-Host
}

$headers = @{ Authorization = "Bearer $Token" }

$infoUrl = "$BaseUrl/api/v1/channels/$ChannelId/telegram-webhook-info"
$syncUrl = "$BaseUrl/api/v1/channels/$ChannelId/telegram-sync-webhook"

Write-Host ''
Write-Host "== BlackChat Telegram Webhook Check ==" -ForegroundColor Cyan
Write-Host "BaseUrl   : $BaseUrl"
Write-Host "ChannelId : $ChannelId"
Write-Host "Info URL  : $infoUrl"
Write-Host "Sync URL  : $syncUrl"

function Print-Info($data) {
  Write-Host ''
  Write-Host '--- expected_url ---' -ForegroundColor Cyan
  Write-Host ($data.expected_url | Out-String)

  Write-Host '--- telegram (raw) ---' -ForegroundColor Cyan
  ($data.telegram | ConvertTo-Json -Depth 20) | Write-Host

  $tg = $data.telegram
  $result = $tg.result

  if ($null -ne $result) {
    Write-Host ''
    Write-Host '--- telegram.result (highlights) ---' -ForegroundColor Cyan
    Write-Host ("url                 : {0}" -f $result.url)
    Write-Host ("has_custom_certificate: {0}" -f $result.has_custom_certificate)
    Write-Host ("pending_update_count : {0}" -f $result.pending_update_count)
    Write-Host ("last_error_date      : {0}" -f $result.last_error_date)
    Write-Host ("last_error_message   : {0}" -f $result.last_error_message)
    Write-Host ("last_synchronization_error_date: {0}" -f $result.last_synchronization_error_date)
  }

  if ($data.expected_url -and $result -and $result.url -and ($data.expected_url -ne $result.url)) {
    Write-Host ''
    Write-Host '!!! ATENÇÃO: URL do Telegram diferente da expected_url !!!' -ForegroundColor Red
  }
}

try {
  $info = Invoke-RestMethod -Method GET -Uri $infoUrl -Headers $headers -TimeoutSec 20
  Print-Info $info
} catch {
  Write-Host ''
  Write-Host 'Falha ao consultar webhook-info:' -ForegroundColor Red
  Write-Host $_.Exception.Message
  if ($_.ErrorDetails -and $_.ErrorDetails.Message) {
    Write-Host $_.ErrorDetails.Message
  }
  exit 1
}

if ($Sync) {
  Write-Host ''
  Write-Host '>> Executando sync (setWebhook) usando URL do .env...' -ForegroundColor Yellow
  try {
    $syncResult = Invoke-RestMethod -Method POST -Uri $syncUrl -Headers $headers -TimeoutSec 20
    Print-Info $syncResult
  } catch {
    Write-Host ''
    Write-Host 'Falha ao executar sync:' -ForegroundColor Red
    Write-Host $_.Exception.Message
    if ($_.ErrorDetails -and $_.ErrorDetails.Message) {
      Write-Host $_.ErrorDetails.Message
    }
    exit 1
  }
}

Write-Host ''
Write-Host 'Concluído.' -ForegroundColor Green
