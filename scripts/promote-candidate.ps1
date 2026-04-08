param(
    [string]$Main = "src/orchestrator/main.py",
    [string]$Candidate = "src/orchestrator/main_refactor_candidate.py",
    [string]$Manifest = "omega_runtime_manifest.json",
    [string]$CommitMessage = "Promote verified orchestration candidate to active line"
)

$ErrorActionPreference = "Stop"

if (!(Test-Path $Main)) { throw "Saknar $Main" }
if (!(Test-Path $Candidate)) { throw "Saknar $Candidate" }
if (!(Test-Path $Manifest)) { throw "Saknar $Manifest" }

Write-Output "=== Verifierar kandidat ==="
python -c "import sys; sys.path.insert(0, '.'); import src.orchestrator.main_refactor_candidate; print('candidate loaded as module successfully')"
if ($LASTEXITCODE -ne 0) { throw "Kandidat laddar inte. Promotion stoppad." }

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backup = "src/orchestrator/main.backup_$timestamp.py"

Write-Output "=== Backup av active line ==="
Copy-Item $Main $backup -Force

Write-Output "=== Promote candidate -> main ==="
Copy-Item $Candidate $Main -Force

Write-Output "=== Uppdaterar manifest-hash ==="
$newHash = (Get-FileHash $Main -Algorithm SHA256).Hash.ToLower()
$content = Get-Content $Manifest -Raw -Encoding UTF8
$pattern = '("path"\s*:\s*"src/orchestrator/main\.py"\s*,\s*"sha256"\s*:\s*")[^"]+(")'

if ($content -notmatch $pattern) {
    throw "Hittade ingen manifestpost för src/orchestrator/main.py"
}

$content = [regex]::Replace($content, $pattern, "`$1$newHash`$2", 1)
Set-Content $Manifest $content -Encoding UTF8

Write-Output "=== Verifierar promoted active line ==="
python -c "import sys; sys.path.insert(0, '.'); import src.orchestrator.main; print('main.py loaded as module successfully')"
if ($LASTEXITCODE -ne 0) { throw "Promoted main.py verifiering misslyckades" }

Write-Output "=== Commit + tag ==="
git add $Main $Manifest $backup
git commit -m $CommitMessage
if ($LASTEXITCODE -ne 0) { throw "Git commit misslyckades" }

git tag -f active-line-stable

Write-Output "Klart: candidate promoted, verifierad och låst."
