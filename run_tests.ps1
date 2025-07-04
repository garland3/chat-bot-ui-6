# Configuration
$WaitTimeSeconds = 30

while ($true) {
    Clear-Host
    Write-Host "Test run at $(Get-Date)" -ForegroundColor Cyan
    python -m pytest --timeout=30 -v
    Write-Host "`nNext run in $WaitTimeSeconds seconds... (Press Ctrl+C to stop)" -ForegroundColor Yellow
    
    # PowerShell native progress bar
    for ($i = 1; $i -le $WaitTimeSeconds; $i++) {
        $percent = ($i / $WaitTimeSeconds) * 100
        $remaining = $WaitTimeSeconds - $i
        Write-Progress -Activity "Waiting for next test run" -Status "$remaining seconds remaining" -PercentComplete $percent
        Start-Sleep -Seconds 1
    }
    Write-Progress -Activity "Waiting for next test run" -Completed
}