# Genera docs/Informe_Taller02_RabbitMQ.pdf a partir de informe.html usando Chrome o Edge en modo headless.
$ErrorActionPreference = "Stop"
$aqui = $PSScriptRoot
$html = Join-Path $aqui "informe.html"
$pdf  = Join-Path (Split-Path $aqui -Parent) "Informe_Taller02_RabbitMQ.pdf"

$navegadores = @(
    "C:\Program Files\Google\Chrome\Application\chrome.exe",
    "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
)
$nav = $navegadores | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $nav) { throw "No se encontro Chrome ni Edge" }

$url = "file:///" + ($html -replace '\\', '/')
& $nav --headless=new --disable-gpu --no-pdf-header-footer --print-to-pdf="$pdf" $url | Out-Null
Write-Host "PDF generado: $pdf"
