# Genera los PDF de cada entregable: primero los HTML con Python y luego los imprime con Chrome o Edge.
$ErrorActionPreference = "Stop"
$aqui = $PSScriptRoot
python (Join-Path $aqui "generar.py")

$navegadores = @(
    "C:\Program Files\Google\Chrome\Application\chrome.exe",
    "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
)
$nav = $navegadores | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $nav) { throw "No se encontro Chrome ni Edge" }

Get-ChildItem (Join-Path $aqui "html") -Filter *.html | ForEach-Object {
    $pdf = Join-Path $aqui ($_.BaseName + ".pdf")
    $url = "file:///" + ($_.FullName -replace '\\', '/')
    & $nav --headless=new --disable-gpu --no-pdf-header-footer --print-to-pdf="$pdf" $url | Out-Null
    Write-Host "PDF generado: $pdf"
}
