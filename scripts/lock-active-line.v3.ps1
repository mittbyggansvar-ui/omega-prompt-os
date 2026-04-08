param(
    [string]$CommitMessage = "Lock verified active line update"
)

$ErrorActionPreference = "Stop"

$mainPath = "src/orchestrator/main.py"
$manifestPath = "omega_runtime_manifest.json"
$updateScript = "scripts/update-manifest-json.ps1"
$thisScript = "scripts/lock-active-line.v3.ps1"

if (!(Test-Path $mainPath)) { throw "Saknar $mainPath" }
if (!(Test-Path $manifestPath)) { throw "Saknar $manifestPath" }
if (!(Test-Path $updateScript)) { throw "Saknar $updateScript" }
if (!(Test-Path $thisScript)) { throw "Saknar $thisScript" }

$newHash = (Get-FileHash $mainPath -Algorithm SHA256).Hash.ToLower()
Write-Output "Ny SHA256 för main.py: $newHash"

Write-Output "=== Uppdaterar manifest via JSON-helper ==="
powershell -ExecutionPolicy Bypass -File $updateScript -TargetPath $mainPath -ManifestPath $manifestPath
if ($LASTEXITCODE -ne 0) {
    throw "Manifestuppdatering misslyckades."
}

Write-Output "=== Verifierar active line ==="
python -c "import sys; sys.path.insert(0, '.'); import src.orchestrator.main; print('main.py loaded as module successfully')"
if ($LASTEXITCODE -ne 0) {
    throw "Verifiering misslyckades. Avbryter."
}

git add $mainPath $manifestPath $updateScript $thisScript

git diff --cached --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Output "Ingen förändring att committa. Active line är redan låst."
    exit 0
}

git commit -m $CommitMessage
if ($LASTEXITCODE -ne 0) {
    throw "Git commit misslyckades."
}

Write-Output "Låsning klar (v3, JSON-säker och idempotent)."
