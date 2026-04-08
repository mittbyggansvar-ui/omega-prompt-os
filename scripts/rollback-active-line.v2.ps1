param(
    [string]$StableRef = "active-line-stable",
    [string]$Main = "src/orchestrator/main.py",
    [string]$Manifest = "omega_runtime_manifest.json",
    [string]$CommitMessage = "Rollback active line to stable tag"
)

$ErrorActionPreference = "Stop"

$updateScript = "scripts/update-manifest-json.ps1"
$thisScript = "scripts/rollback-active-line.v2.ps1"

if (!(Test-Path $Main)) { throw "Saknar $Main" }
if (!(Test-Path $Manifest)) { throw "Saknar $Manifest" }
if (!(Test-Path $updateScript)) { throw "Saknar $updateScript" }
if (!(Test-Path $thisScript)) { throw "Saknar $thisScript" }

Write-Output "=== Hämtar stabil main.py från tag ==="
$stableContent = git show "${StableRef}:src/orchestrator/main.py"
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($stableContent)) {
    throw "Kunde inte läsa src/orchestrator/main.py från $StableRef"
}

$currentContent = Get-Content $Main -Raw -Encoding UTF8
$willChangeMain = ($currentContent -ne $stableContent)

if ($willChangeMain) {
    Write-Output "=== Skriver rollbackad main.py ==="
    Set-Content $Main $stableContent -Encoding UTF8
} else {
    Write-Output "=== main.py matchar redan $StableRef ==="
}

Write-Output "=== Uppdaterar manifest via JSON-helper ==="
powershell -ExecutionPolicy Bypass -File $updateScript -TargetPath $Main -ManifestPath $Manifest
if ($LASTEXITCODE -ne 0) {
    throw "Manifestuppdatering misslyckades."
}

Write-Output "=== Verifierar rollbackad active line ==="
python -c "import sys; sys.path.insert(0, '.'); import src.orchestrator.main; print('main.py loaded as module successfully')"
if ($LASTEXITCODE -ne 0) {
    throw "Rollback verifiering misslyckades"
}

git add $Main $Manifest $updateScript $thisScript

git diff --cached --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Output "Ingen förändring att committa. Active line matchar redan stabil ref."
    exit 0
}

git commit -m $CommitMessage
if ($LASTEXITCODE -ne 0) {
    throw "Git commit misslyckades"
}

Write-Output "Rollback klar (v2, JSON-säker och idempotent)."
