param(
    [string]$Main = "src/orchestrator/main.py",
    [string]$Candidate = "src/orchestrator/main_unified_candidate.py",
    [string]$RuntimeLLM = "src/orchestrator/runtime_llm.py",
    [string]$RuntimeModes = "src/orchestrator/runtime_modes.py",
    [string]$Manifest = "omega_runtime_manifest.json",
    [string]$CommitMessage = "Promote unified runtime candidate to active line",
    [string]$CandidateHeader1 = "# Ω Prompt OS v1.27 - Unified Runtime Candidate",
    [string]$CandidateHeader2 = "# Thin orchestrator for unified runtime",
    [switch]$DryRun,
    [switch]$RequireAllProviderRuns
)

$ErrorActionPreference = "Stop"

function Write-Utf8NoBom([string]$Path, [string]$Content) {
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $Content, $utf8NoBom)
}

function Get-Sha256Hex([string]$Path) {
    return (Get-FileHash $Path -Algorithm SHA256).Hash.ToLower()
}

function Ensure-PathExists([string]$Path) {
    if (!(Test-Path $Path)) {
        throw "Saknar $Path"
    }
}

function Assert-ManifestStructure([object]$ManifestObject) {
    if ($null -eq $ManifestObject) {
        throw "Manifest kunde inte läsas"
    }
    if ($null -eq $ManifestObject.policy -or [string]::IsNullOrWhiteSpace([string]$ManifestObject.policy)) {
        throw "Manifest saknar policy"
    }
    if ($null -eq $ManifestObject.version -or [string]::IsNullOrWhiteSpace([string]$ManifestObject.version)) {
        throw "Manifest saknar version"
    }
    if ($null -eq $ManifestObject.enforcement -or [string]::IsNullOrWhiteSpace([string]$ManifestObject.enforcement)) {
        throw "Manifest saknar enforcement"
    }
    if ($null -eq $ManifestObject.active_line) {
        throw "Manifest saknar active_line"
    }
    if (!($ManifestObject.active_line -is [System.Array])) {
        throw "Manifest active_line är inte en array"
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

function Assert-ManifestEntry([object]$ManifestObject, [string]$TargetPath, [string]$ExpectedHash) {
    $entry = $ManifestObject.active_line | Where-Object { $_.path -eq $TargetPath }
    if ($null -eq $entry) {
        throw "Manifest saknar entry för $TargetPath efter uppdatering"
    }
    if ([string]::IsNullOrWhiteSpace([string]$entry.sha256)) {
        throw "Manifest entry för $TargetPath saknar sha256"
    }
    if ($entry.sha256.ToLower() -ne $ExpectedHash.ToLower()) {
        throw "Manifest-hash mismatch för $TargetPath efter uppdatering"
    }
}

function Assert-CandidateIdentity([string]$CandidatePath, [string]$Header1, [string]$Header2) {
    $content = Get-Content $CandidatePath -Raw -Encoding UTF8
    if ($content -notmatch [regex]::Escape($Header1)) {
        throw "Candidate identity check misslyckades: saknar marker '$Header1'"
    }
    if ($content -notmatch [regex]::Escape($Header2)) {
        throw "Candidate identity check misslyckades: saknar marker '$Header2'"
    }
}

function Invoke-CompileCheck([string]$Path, [string]$Label) {
    Write-Output "=== Preflight: $Label compile ==="
    python -m py_compile $Path
    if ($LASTEXITCODE -ne 0) {
        throw "$Label compile misslyckades."
    }
}

function Invoke-ImportCheck([string]$ModuleName, [string]$Label) {
    Write-Output "=== Preflight: $Label import ==="
    python -c "import sys; sys.path.insert(0, '.'); import $ModuleName; print('$Label import OK')"
    if ($LASTEXITCODE -ne 0) {
        throw "$Label import misslyckades."
    }
}

function Test-ProviderAvailable([string]$Provider) {
    switch ($Provider) {
        "auto"   { return $true }
        "xai"    { return ![string]::IsNullOrWhiteSpace($env:XAI_API_KEY) }
        "openai" { return ![string]::IsNullOrWhiteSpace($env:OPENAI_API_KEY) }
        default  { return $false }
    }
}

function Invoke-ModuleRun([string]$ModuleName, [string]$Provider) {
    $oldProvider = $env:OMEGA_RUNTIME_PROVIDER
    try {
        $env:OMEGA_RUNTIME_PROVIDER = $Provider
        Write-Output "=== Post-promotion run: provider=$Provider module=$ModuleName ==="
        python -m $ModuleName
        if ($LASTEXITCODE -ne 0) {
            throw "Post-promotion körtest misslyckades för provider=$Provider"
        }
    }
    finally {
        if ($null -eq $oldProvider) {
            Remove-Item Env:\OMEGA_RUNTIME_PROVIDER -ErrorAction SilentlyContinue
        }
        else {
            $env:OMEGA_RUNTIME_PROVIDER = $oldProvider
        }
    }
}

function Assert-CleanGitState([string[]]$Paths) {
    $statusLines = git status --short -- @Paths
    if ($LASTEXITCODE -ne 0) {
        throw "Kunde inte läsa git status för preflight"
    }
    $nonEmpty = @($statusLines | Where-Object { $_ -and $_.Trim() -ne "" })
    if ($nonEmpty.Count -gt 0) {
        Write-Output "=== Git preflight failed: berörda filer är inte rena ==="
        $nonEmpty | ForEach-Object { Write-Output $_ }
        throw "Git working tree/index måste vara rent före promotion"
    }
}

Ensure-PathExists $Main
Ensure-PathExists $Candidate
Ensure-PathExists $RuntimeLLM
Ensure-PathExists $RuntimeModes
Ensure-PathExists $Manifest

Write-Output "=== Git preflight ==="
Assert-CleanGitState -Paths @($Main, $Candidate, $RuntimeLLM, $RuntimeModes, $Manifest)

Write-Output "=== Candidate identity check ==="
Assert-CandidateIdentity -CandidatePath $Candidate -Header1 $CandidateHeader1 -Header2 $CandidateHeader2

Invoke-CompileCheck -Path $Candidate -Label "candidate"
Invoke-CompileCheck -Path $RuntimeLLM -Label "runtime_llm"
Invoke-CompileCheck -Path $RuntimeModes -Label "runtime_modes"

Invoke-ImportCheck -ModuleName "src.orchestrator.main_unified_candidate" -Label "main_unified_candidate"
Invoke-ImportCheck -ModuleName "src.orchestrator.runtime_llm" -Label "runtime_llm"
Invoke-ImportCheck -ModuleName "src.orchestrator.runtime_modes" -Label "runtime_modes"

Write-Output "=== Läs manifest preflight ==="
$manifestObject = Get-Content $Manifest -Raw -Encoding UTF8 | ConvertFrom-Json
Assert-ManifestStructure -ManifestObject $manifestObject

$plannedMainHash = Get-Sha256Hex $Candidate
$plannedRuntimeHash = Get-Sha256Hex $RuntimeLLM
$plannedModesHash = Get-Sha256Hex $RuntimeModes

if ($DryRun) {
    Write-Output "=== DRY RUN: inga filer skrivs ==="
    Write-Output ("Planned main target:   {0}" -f $Main)
    Write-Output ("Planned source:        {0}" -f $Candidate)
    Write-Output ("Planned main sha256:   {0}" -f $plannedMainHash)
    Write-Output ("Planned runtime sha256:{0}" -f $plannedRuntimeHash)
    Write-Output ("Planned modes sha256:  {0}" -f $plannedModesHash)
    Write-Output ("Manifest policy:       {0}" -f $manifestObject.policy)
    Write-Output ("Manifest version:      {0}" -f $manifestObject.version)
    Write-Output ("Manifest enforcement:  {0}" -f $manifestObject.enforcement)
    Write-Output "Planned active_line entries:"
    Write-Output (" - {0}" -f $Main)
    Write-Output (" - {0}" -f $RuntimeLLM)
    Write-Output (" - {0}" -f $RuntimeModes)
    exit 0
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupRoot = "_analysis_artifacts/promote_backups/$timestamp"
New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null

$backupMain = Join-Path $backupRoot "main.py"
$backupManifest = Join-Path $backupRoot "omega_runtime_manifest.json"

Write-Output "=== Backup active line + manifest ==="
Copy-Item $Main $backupMain -Force
Copy-Item $Manifest $backupManifest -Force

$restored = $false
$indexRestored = $false

try {
    $currentMain = Get-Content $Main -Raw -Encoding UTF8
    $candidateContent = Get-Content $Candidate -Raw -Encoding UTF8

    if ($currentMain -eq $candidateContent) {
        Write-Output "=== Candidate matchar redan main.py ==="
    }
    else {
        Write-Output "=== Promote candidate -> main ==="
        Copy-Item $Candidate $Main -Force
    }

    Write-Output "=== Läs manifest för uppdatering ==="
    $manifestObject = Get-Content $Manifest -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-ManifestStructure -ManifestObject $manifestObject

    $mainHash = Get-Sha256Hex $Main
    $runtimeHash = Get-Sha256Hex $RuntimeLLM
    $modesHash = Get-Sha256Hex $RuntimeModes

    Write-Output "=== Uppdaterar manifest-hashar ==="
    Set-ManifestHash -ManifestObject $manifestObject -TargetPath $Main -Sha256 $mainHash
    Set-ManifestHash -ManifestObject $manifestObject -TargetPath $RuntimeLLM -Sha256 $runtimeHash
    Set-ManifestHash -ManifestObject $manifestObject -TargetPath $RuntimeModes -Sha256 $modesHash

    $manifestJson = $manifestObject | ConvertTo-Json -Depth 20
    Write-Utf8NoBom -Path $Manifest -Content $manifestJson

    Write-Output "=== Verifiera manifest efter skrivning ==="
    $manifestVerify = Get-Content $Manifest -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-ManifestStructure -ManifestObject $manifestVerify
    Assert-ManifestEntry -ManifestObject $manifestVerify -TargetPath $Main -ExpectedHash $mainHash
    Assert-ManifestEntry -ManifestObject $manifestVerify -TargetPath $RuntimeLLM -ExpectedHash $runtimeHash
    Assert-ManifestEntry -ManifestObject $manifestVerify -TargetPath $RuntimeModes -ExpectedHash $modesHash

    Invoke-ImportCheck -ModuleName "src.orchestrator.main" -Label "promoted main"
    Invoke-ImportCheck -ModuleName "src.orchestrator.runtime_llm" -Label "runtime_llm"
    Invoke-ImportCheck -ModuleName "src.orchestrator.runtime_modes" -Label "runtime_modes"

    $providers = @("auto", "xai", "openai")
    foreach ($provider in $providers) {
        if (Test-ProviderAvailable $provider) {
            Invoke-ModuleRun -ModuleName "src.orchestrator.main" -Provider $provider
        }
        elseif ($RequireAllProviderRuns) {
            throw "Provider-test krävs men credentials saknas för provider=$provider"
        }
        else {
            Write-Output "=== SKIP provider=$provider (credentials saknas) ==="
        }
    }

    Write-Output "=== Git add ==="
    git add $Main $Candidate $RuntimeLLM $RuntimeModes $Manifest $PSCommandPath

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

    $commitHash = (git rev-parse --short HEAD).Trim()
    $tagStatus = (git tag --list active-line-stable).Trim()

    Write-Output "=== PROMOTION SUMMARY ==="
    Write-Output ("main.py sha256:         {0}" -f $mainHash)
    Write-Output ("runtime_llm.py sha256:  {0}" -f $runtimeHash)
    Write-Output ("runtime_modes.py sha256:{0}" -f $modesHash)
    Write-Output ("backup path:            {0}" -f $backupRoot)
    Write-Output ("commit hash:            {0}" -f $commitHash)
    Write-Output ("tag status:             {0}" -f $tagStatus)
    Write-Output "Klart: unified candidate promoted till active line med uppdaterat manifest för main.py + runtime_llm.py + runtime_modes.py."
}
catch {
    Write-Output "=== PROMOTION FAILED - återställer main.py och manifest ==="
    if ((Test-Path $backupMain) -and (Test-Path $backupManifest)) {
        Copy-Item $backupMain $Main -Force
        Copy-Item $backupManifest $Manifest -Force
        $restored = $true
    }

    Write-Output "=== Återställ staged state för main.py + manifest ==="
    git restore --source=HEAD --staged -- $Main $Manifest
    if ($LASTEXITCODE -eq 0) {
        $indexRestored = $true
    }

    if ($restored) {
        Write-Output "Återställning av working tree klar från backup."
    }
    if ($indexRestored) {
        Write-Output "Återställning av staged state klar från HEAD."
    }

    throw
}

