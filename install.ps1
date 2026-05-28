$ErrorActionPreference = "Stop"
$projectDir = $PSScriptRoot
$installDir = "$env:LOCALAPPDATA\pdf2pic"

# 1. venv + dependencies
Write-Host "[1/3] uv sync ..." -ForegroundColor Cyan
uv sync --project $projectDir

# 2. write launcher
Write-Host "[2/3] install launcher -> $installDir" -ForegroundColor Cyan
New-Item -ItemType Directory -Path $installDir -Force | Out-Null

@"
param(
    [Parameter(Position = 0)]
    [string]`$PdfPath
)
if (-not `$PdfPath) {
    Write-Host "Usage: pdf2pic <path-to.pdf>" -ForegroundColor Yellow
    exit 1
}
`$resolved = (Resolve-Path `$PdfPath -ErrorAction Stop).Path
& uv run --project "$projectDir" python "$projectDir\pdf2pic.py" `$resolved
"@ | Set-Content "$installDir\pdf2pic.ps1" -Encoding UTF8

# 3. add to user PATH
Write-Host "[3/3] configure PATH ..." -ForegroundColor Cyan
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -split ";" -notcontains $installDir) {
    [Environment]::SetEnvironmentVariable("Path", "$userPath;$installDir", "User")
    Write-Host "  added $installDir to user PATH (restart terminal to take effect)" -ForegroundColor Green
} else {
    Write-Host "  $installDir already in PATH" -ForegroundColor DarkGray
}

Write-Host "`ndone! open a new terminal and run:" -ForegroundColor Green
Write-Host "  pdf2pic <path-to.pdf>" -ForegroundColor White
