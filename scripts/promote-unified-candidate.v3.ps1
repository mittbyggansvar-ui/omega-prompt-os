param(
    [string]$Main = "src/orchestrator/main.py",
    [string]$Candidate = "src/orchestrator/main_unified_candidate.py",
    [string]$RuntimeLLM = "src/orchestrator/runtime_llm.py",
    [string]$Manifest = "omega_runtime_manifest.json",
    [string]$CommitMessage = "Promote unified runtime candidate to active line"
)

$ErrorActionPreference = "Stop"

function Get-Sha256Hex([string]$Path) {
    return (Get-FileHash $Path -Algorithm SHA256).Hash.ToLower()
}

function Ensure-PathExists([string]$Path) {
    if (!(Test-Path $Path)) {
        throw "Saknar $Path"
    }
}

function Set-ManifestHash([object]$ManifestObject, [string]$TargetPath, [string]$Sha256) {
    $existing = $ManifestObject.active_line | Where-Object { $_.path -eq $TargetPath }

    if ($null -ne $existing) {
        foreach ($entry in $ManifestObject.active_line) {
            if ($entry.path -eq $TargetPath) {
                $entry.sha256 = $Sha256
            }
        }
    }
    else {
        $newEntry = [pscustomobject]@{
            path   = $TargetPath
            sha256 = $Sha256
        }
        $ManifestObject.active_line += $newEntry
    }
}

Ensure-PathExists $Main
Ensure-PathExists $Candidate
Ensure-PathExists $RuntimeLLM
Ensure-PathExists $Manifest

Write-Output "=== Preflight: candidate compile ==="
python -m py_compile $Candidate
if ($LASTEXITCODE -ne 0) {
    throw "Candidate compile misslyckades."
}

Write-Output "=== Preflight: runtime_llm compile ==="
python -m py_compile $RuntimeLLM
if ($LASTEXITCODE -ne 0) {
    throw "runtime_llm compile misslyckades."
}

Write-Output "=== Preflight: candidate import ==="
python -c "import sys; sys.path.insert(0, '.'); import src.orchestrator.main_unified_candidate; print('main_unified_candidate import OK')"
if ($LASTEXITCODE -ne 0) {
    throw "Candidate import misslyckades."
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupRoot = "_analysis_artifacts/promote_backups/$timestamp"
New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null

$backupMain = Join-Path $backupRoot "main.py"
$backupManifest = Join-Path $backupRoot "omega_runtime_manifest.json"

Write-Output "=== Backup active line + manifest ==="
Copy-Item $Main $backupMain -Force
Copy-Item $Manifest $backupManifest -Force

$currentMain = Get-Content $Main -Raw -Encoding UTF8
$candidateContent = Get-Content $Candidate -Raw -Encoding UTF8

if ($currentMain -eq $candidateContent) {
    Write-Output "=== Candidate matchar redan main.py ==="
}
else {
    Write-Output "=== Promote candidate -> main ==="
    Copy-Item $Candidate $Main -Force
}

Write-Output "=== Läs manifest ==="
$manifestObject = Get-Content $Manifest -Raw -Encoding UTF8 | ConvertFrom-Json

if ($null -eq $manifestObject.active_line) {
    throw "Manifest saknar active_line"
}

$mainHash = Get-Sha256Hex $Main
$runtimeHash = Get-Sha256Hex $RuntimeLLM

Write-Output "=== Uppdaterar manifest-hashar ==="
Set-ManifestHash -ManifestObject $manifestObject -TargetPath $Main -Sha256 $mainHash
Set-ManifestHash -ManifestObject $manifestObject -TargetPath $RuntimeLLM -Sha256 $runtimeHash

$manifestObject | ConvertTo-Json -Depth 20 | Set-Content $Manifest -Encoding UTF8

Write-Output "=== Verifiera manifest efter skrivning ==="
$manifestVerify = Get-Content $Manifest -Raw -Encoding UTF8 | ConvertFrom-Json

$mainEntry = $manifestVerify.active_line | Where-Object { $_.path -eq $Main }
$runtimeEntry = $manifestVerify.active_line | Where-Object { $_.path -eq $RuntimeLLM }

if ($null -eq $mainEntry) {
    throw "Manifest saknar entry för $Main efter uppdatering"
}
if ($null -eq $runtimeEntry) {
    throw "Manifest saknar entry för $RuntimeLLM efter uppdatering"
}
if ($mainEntry.sha256.ToLower() -ne $mainHash) {
    throw "Manifest-hash mismatch för $Main efter uppdatering"
}
if ($runtimeEntry.sha256.ToLower() -ne $runtimeHash) {
    throw "Manifest-hash mismatch för $RuntimeLLM efter uppdatering"
}

Write-Output "=== Verifiera promoted active line import ==="
python -c "import sys; sys.path.insert(0, '.'); import src.orchestrator.main; print('main.py import OK')"
if ($LASTEXITCODE -ne 0) {
    throw "Promoted main.py import misslyckades"
}

Write-Output "=== Verifiera runtime_llm import ==="
python -c "import sys; sys.path.insert(0, '.'); import src.orchestrator.runtime_llm; print('runtime_llm import OK')"
if ($LASTEXITCODE -ne 0) {
    throw "runtime_llm import misslyckades"
}

Write-Output "=== Git add ==="
git add $Main $Candidate $RuntimeLLM $Manifest $backupMain $backupManifest $PSCommandPath

git diff --cached --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Output "Ingen förändring att committa."
    exit 0
}

Write-Output "=== Git commit ==="
git commit -m $CommitMessage
if ($LASTEXITCODE -ne 0) {
    throw "Git commit misslyckades"
}

Write-Output "=== Git tag ==="
git tag -f active-line-stable
if ($LASTEXITCODE -ne 0) {
    throw "Git tag misslyckades"
}

Write-Output "Klart: unified candidate promoted till active line med uppdaterat manifest för main.py + runtime_llm.py."

