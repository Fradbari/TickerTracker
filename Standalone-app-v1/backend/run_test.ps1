# PowerShell script to run tests with correct PYTHONPATH
# Usage: .\run_test.ps1 [test_file]
# Example: .\run_test.ps1 tests\test_estimate_repository.py

param(
    [string]$TestFile = "tests\test_estimate_repository.py"
)

# Ensure we're in backend directory
$BackendDir = $PSScriptRoot
Set-Location $BackendDir

Write-Host "\n" -NoNewline
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Running Test: $TestFile" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host "\n" -NoNewline

# Set PYTHONPATH to include backend directory
$env:PYTHONPATH = $BackendDir

# Run the test
python $TestFile

$exitCode = $LASTEXITCODE

if ($exitCode -eq 0) {
    Write-Host "\n" -NoNewline
    Write-Host "================================" -ForegroundColor Green
    Write-Host "✅ Tests Completed Successfully!" -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Green
    Write-Host "\n" -NoNewline
} else {
    Write-Host "\n" -NoNewline
    Write-Host "================================" -ForegroundColor Red
    Write-Host "❌ Tests Failed (Exit Code: $exitCode)" -ForegroundColor Red
    Write-Host "================================" -ForegroundColor Red
    Write-Host "\n" -NoNewline
}

exit $exitCode
