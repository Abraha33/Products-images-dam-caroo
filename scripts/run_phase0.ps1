param(
    [Parameter(Mandatory = $true)]
    [string]$InputPath,

    [string]$OutputPath = "",

    [int]$Workers = 0,

    [int]$PHashDistance = 5
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$Requirements = Join-Path $RepoRoot "requirements-phase0.txt"
$Auditor = Join-Path $PSScriptRoot "phase0_inventory.py"
$Venv = Join-Path $env:LOCALAPPDATA "envax-phase0-audit-venv"
$Python = Join-Path $Venv "Scripts\python.exe"

if (-not (Test-Path -LiteralPath $InputPath -PathType Container)) {
    throw "No existe la carpeta de entrada: $InputPath"
}

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $OutputPath = Join-Path (Split-Path -Parent (Resolve-Path -LiteralPath $InputPath)) "ENVAX_AUDIT_$stamp"
}

if (-not (Test-Path -LiteralPath $Python)) {
    Write-Host "Creando entorno Python aislado en: $Venv"
    $launcher = Get-Command py -ErrorAction SilentlyContinue
    if ($launcher) {
        & py -3 -m venv $Venv
    }
    else {
        $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
        if (-not $pythonCmd) {
            throw "Python 3 no esta instalado o no esta disponible en PATH."
        }
        & python -m venv $Venv
    }
}

Write-Host "Instalando/verificando dependencias del auditor..."
& $Python -m pip install --disable-pip-version-check -r $Requirements
if ($LASTEXITCODE -ne 0) { throw "Fallo instalando dependencias." }

$argsList = @(
    $Auditor,
    "--input", (Resolve-Path -LiteralPath $InputPath).Path,
    "--output", $OutputPath,
    "--phash-distance", $PHashDistance
)
if ($Workers -gt 0) {
    $argsList += @("--workers", $Workers)
}

Write-Host ""
Write-Host "=== ENVAX DAM - FASE 0 READ-ONLY ==="
Write-Host "Fuente : $InputPath"
Write-Host "Salida : $OutputPath"
Write-Host "Regla  : NO mover / NO renombrar / NO borrar / NO editar fuentes"
Write-Host ""

& $Python @argsList
if ($LASTEXITCODE -ne 0) { throw "El auditor termino con codigo $LASTEXITCODE" }

Write-Host ""
Write-Host "Auditoria terminada. Comparte conmigo la carpeta de salida o, como minimo:"
Write-Host "  audit_summary.md"
Write-Host "  folder_summary.csv"
Write-Host "  inventory.csv"
Write-Host "  duplicates_exact.csv"
Write-Host "  duplicates_visual.csv"
Write-Host "  audit_errors.log"
