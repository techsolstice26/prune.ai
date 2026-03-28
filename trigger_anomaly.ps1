# trigger_anomaly.ps1
# Run this script to trigger a live anomaly in your CloudScope AIOps dashboard

Write-Host "⚡ Triggering CloudScope AIOps Anomaly Pipeline..." -ForegroundColor Yellow

$aws_path = "C:\Program Files\Amazon\AWSCLIV2\aws.exe"

if (!(Test-Path $aws_path)) {
    $aws_path = "aws" # Fallback to PATH
}

& $aws_path lambda invoke --function-name CloudScope-Detector --region us-east-1 response.json | Out-Null

if ($LASTEXITCODE -eq 0) {
    $response = Get-Content response.json | ConvertFrom-Json
    Write-Host "✅ Anomaly Triggered! Suspicion Score: $($response.score)" -ForegroundColor Green
    Write-Host "Check your dashboard now!" -ForegroundColor Cyan
} else {
    Write-Host "❌ Failed to trigger anomaly. Check AWS credentials." -ForegroundColor Red
}

Remove-Item response.json -ErrorAction SilentlyContinue
