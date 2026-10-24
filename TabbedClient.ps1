# TabbedClient — Windows PowerShell Indító
Set-Location -Path $PSScriptRoot

if (Get-Command python -ErrorAction SilentlyContinue) {
    python desktop/tabbedclient_windows.py
    exit 0
}

$edgeCandidates = @(
    "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe",
    "${env:ProgramFiles}\Microsoft\Edge\Application\msedge.exe",
    "${env:LocalAppData}\Microsoft\Edge\Application\msedge.exe"
)

$edgePath = $edgeCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1

if ($edgePath) {
    $indexUrl = "file:///" + ($PSScriptRoot -replace '\\', '/') + "/src/index.html"
    $profileDir = Join-Path $PSScriptRoot "data\profiles\default"
    Start-Process $edgePath -ArgumentList "--app=$indexUrl", "--user-data-dir=$profileDir", "--no-first-run", "--window-size=1280,840"
} else {
    Start-Process (Join-Path $PSScriptRoot "src\index.html")
}
