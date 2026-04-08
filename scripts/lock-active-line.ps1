param(
    [string]$CommitMessage = "Lock verified active line update"
)

$ErrorActionPreference = "Stop"

$mainPath = "src/orchestrator/main.py"
$manifestPath = "omega_runtime_manifest.json"

if (!(Test-Path $mainPath)) { throw "Saknar $mainPath" }
if (!(Test-Path $manifestPath)) { throw "Saknar $manifestPath" }

$newHash = (Get-FileHash $mainPath -Algorithm SHA256).Hash.ToLower()
Write-Output "Ny SHA256 för main.py: $newHash"

$manifest = Get-Content $manifestPath -Raw -Encoding UTF8
$pattern = '("path"\s*:\s*"src/orchestrator/main\.py"\s*,\s*"sha256"\s*:\s*")[^"]+(")'

if ($manifest -notmatch $pattern) {
    throw "Hittade ingen manifestpost för src/orchestrator/main.py"
}

$updatedManifest = [regex]::Replace(
    $manifest,
    $pattern,
    "`$1$newHash`$2",
    1
)

Set-Content $manifestPath $updatedManifest -Encoding UTF8
Write-Output "Manifest uppdaterat."

python -c "import sys; sys.path.insert(0, '.'); import src.orchestrator.main; print('main.py loaded as module successfully')"
if ($LASTEXITCODE -ne 0) {
    throw "Verifiering misslyckades. Avbryter."
}

git add $mainPath $manifestPath
git commit -m $CommitMessage
if ($LASTEXITCODE -ne 0) {
    throw "Git commit misslyckades."
}

Write-Output "Låsning klar."
