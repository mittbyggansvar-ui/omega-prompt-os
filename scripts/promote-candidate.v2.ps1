param(
    [string]$Main = "src/orchestrator/main.py",
    [string]$Candidate = "src/orchestrator/main_refactor_candidate.py",
    [string]$Manifest = "omega_runtime_manifest.json",
    [string]$CommitMessage = "Promote verified orchestration candidate to active line"
)

$ErrorActionPreference = "Stop"

$updateScript = "scripts/update-manifest-json.ps1"
$thisScript = "scripts/promote-candidate.v2.ps1"

if (!(Test-Path $Main)) { throw "Saknar $Main" }
if (!(Test-Path $Candidate)) { throw "Saknar $Candidate" }
if (!(Test-Path $Manifest)) { throw "Saknar $Manifest" }
if (!(Test-Path $updateScript)) { throw "Saknar $updateScript" }
if (!(Test-Path $thisScript)) { throw "Saknar $thisScript" }

Write-Output "=== Verifierar kandidat ==="
python -c "import sys; sys.path.insert(0, '.'); import src.orchestrator.main_refactor_candidate; print('candidate loaded as module successfully')"
if ($LASTEXITCODE -ne 0) {
    throw "Kandidat laddar inte. Promotion stoppad."
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupRoot = "_analysis_artifacts/promote_backups/$timestamp"
New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
$backup = Join-Path $backupRoot "main.py"

Write-Output "=== Backup av active line ==="
Copy-Item $Main $backup -Force

$currentMain = Get-Content $Main -Raw -Encoding UTF8
$candidateContent = Get-Content $Candidate -Raw -Encoding UTF8

if ($currentMain -eq $candidateContent) {
    Write-Output "=== Candidate matchar redan main.py ==="
} else {
    Write-Output "=== Promote candidate -> main ==="
    Copy-Item $Candidate $Main -Force
}

Write-Output "=== Uppdaterar manifest via JSON-helper ==="
powershell -ExecutionPolicy Bypass -File $updateScript -TargetPath $Main -ManifestPath $Manifest
if ($LASTEXITCODE -ne 0) {
    throw "Manifestuppdatering misslyckades."
}

Write-Output "=== Verifierar promoted active line ==="
python -c "import sys; sys.path.insert(0, '.'); import src.orchestrator.main; print('main.py loaded as module successfully')"
if ($LASTEXITCODE -ne 0) {
    throw "Promoted main.py verifiering misslyckades"
}

Write-Output "=== Commit + tag ==="
git add $Main $Manifest $Candidate $updateScript $thisScript $backup

git diff --cached --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Output "Ingen förändring att committa. Candidate matchar redan active line."
    exit 0
}

git commit -m $CommitMessage
if ($LASTEXITCODE -ne 0) {
    throw "Git commit misslyckades"
}

git tag -f active-line-stable
if ($LASTEXITCODE -ne 0) {
    throw "Git tag misslyckades"
}

Write-Output "Klart: candidate promoted, verifierad och låst (v2, JSON-säker)."
