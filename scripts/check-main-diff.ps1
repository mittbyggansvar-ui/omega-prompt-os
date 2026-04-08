param(
    [string]$Left = "src/orchestrator/main.py",
    [string]$Right = "src/orchestrator/main_refactor_candidate.py"
)

$leftContent = Get-Content $Left -Raw -Encoding UTF8
$rightContent = Get-Content $Right -Raw -Encoding UTF8

if ($leftContent -eq $rightContent) {
    Write-Output "Ingen skillnad mellan filer."
} else {
    Write-Output "Skillnad upptäckt mellan:"
    Write-Output "  $Left"
    Write-Output "  $Right"
}
