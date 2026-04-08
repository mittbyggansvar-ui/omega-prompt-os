param(
    [string]$StableRef = "active-line-stable",
    [string]$Main = "src/orchestrator/main.py",
    [string]$Manifest = "omega_runtime_manifest.json",
    [string]$CommitMessage = "Rollback active line to stable tag"
)

$ErrorActionPreference = "Stop"

if (!(Test-Path $Main)) { throw "Saknar $Main" }
if (!(Test-Path $Manifest)) { throw "Saknar $Manifest" }

Write-Output "=== Hämtar stabil main.py från tag ==="
$stableContent = git show "${StableRef}:src/orchestrator/main.py"
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($stableContent)) {
    throw "Kunde inte läsa src/orchestrator/main.py från $StableRef"
}

Set-Content $Main $stableContent -Encoding UTF8

Write-Output "=== Uppdaterar manifest-hash ==="
$newHash = (Get-FileHash $Main -Algorithm SHA256).Hash.ToLower()
$content = Get-Content $Manifest -Raw -Encoding UTF8
$pattern = '("path"\s*:\s*"src/orchestrator/main\.py"\s*,\s*"sha256"\s*:\s*")[^"]+(")'

if ($content -notmatch $pattern) {
    throw "Hittade ingen manifestpost för src/orchestrator/main.py"
}

$content = [regex]::Replace($content, $pattern, "`$1$newHash`$2", 1)
Set-Content $Manifest $content -Encoding UTF8

Write-Output "=== Verifierar rollbackad active line ==="
python -c "import sys; sys.path.insert(0, '.'); import src.orchestrator.main; print('main.py loaded as module successfully')"
if ($LASTEXITCODE -ne 0) { throw "Rollback verifiering misslyckades" }

git add $Main $Manifest
git commit -m $CommitMessage
if ($LASTEXITCODE -ne 0) { throw "Git commit misslyckades" }

Write-Output "Rollback klar."
