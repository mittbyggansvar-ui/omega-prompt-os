param(
    [Parameter(Mandatory = $true)]
    [string]$TargetPath,

    [string]$ManifestPath = "omega_runtime_manifest.json"
)

$ErrorActionPreference = "Stop"

if (!(Test-Path $ManifestPath)) {
    throw "Saknar manifest: $ManifestPath"
}

if (!(Test-Path $TargetPath)) {
    throw "Saknar målfil: $TargetPath"
}

$manifest = Get-Content $ManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json

if (-not $manifest.active_line) {
    throw "Manifest saknar active_line"
}

$normalizedTarget = $TargetPath.Replace('\','/').ToLower()
$newHash = (Get-FileHash $TargetPath -Algorithm SHA256).Hash.ToLower()

$found = $false
foreach ($entry in $manifest.active_line) {
    if ($entry.path.Replace('\','/').ToLower() -eq $normalizedTarget) {
        $entry.sha256 = $newHash
        $found = $true
        break
    }
}

if (-not $found) {
    $manifest.active_line += [pscustomobject]@{
        path   = $TargetPath.Replace('\','/')
        sha256 = $newHash
    }
}

$manifest | ConvertTo-Json -Depth 10 | Set-Content $ManifestPath -Encoding UTF8

Write-Host "Manifest uppdaterat säkert via JSON: $TargetPath" -ForegroundColor Green
Write-Host "Ny SHA256: $newHash" -ForegroundColor Green
