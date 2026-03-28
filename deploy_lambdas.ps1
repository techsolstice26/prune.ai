# CloudScope AIOps - Lambda Deployment Script
Write-Host "Deploying CloudScope Lambdas..." -ForegroundColor Cyan

# 1. Zip Detector
$detectorPy = "C:\Users\ritvi\.gemini\antigravity\scratch\prune.ai\terraform\src\detector\detector.py"
$detectorZip = "C:\Users\ritvi\.gemini\antigravity\scratch\prune.ai\terraform\detector_deploy.zip"
if (Test-Path $detectorZip) { Remove-Item $detectorZip -Force }
Compress-Archive -Path $detectorPy -DestinationPath $detectorZip -Force
Write-Host "Detector zipped." -ForegroundColor Green

# 2. Zip Explainer
$explainerPy = "C:\Users\ritvi\.gemini\antigravity\scratch\prune.ai\terraform\src\explainer\explainer.py"
$explainerZip = "C:\Users\ritvi\.gemini\antigravity\scratch\prune.ai\terraform\explainer_deploy.zip"
if (Test-Path $explainerZip) { Remove-Item $explainerZip -Force }
Compress-Archive -Path $explainerPy -DestinationPath $explainerZip -Force
Write-Host "Explainer zipped." -ForegroundColor Green

# 3. Deploy Detector Lambda
Write-Host "Deploying Detector Lambda..." -ForegroundColor Yellow
& "C:\Program Files\Amazon\AWSCLIV2\aws.exe" lambda update-function-code --function-name CloudScope-Detector --zip-file "fileb://$detectorZip" --region us-east-1

# 4. Deploy Explainer Lambda
Write-Host "Deploying Explainer Lambda..." -ForegroundColor Yellow
& "C:\Program Files\Amazon\AWSCLIV2\aws.exe" lambda update-function-code --function-name CloudScope-Explainer --zip-file "fileb://$explainerZip" --region us-east-1

# 5. Upload backend to EC2 and restart
Write-Host "Uploading backend to EC2..." -ForegroundColor Yellow
$keyPath = "C:\Users\ritvi\.gemini\antigravity\scratch\prune.ai\terraform\CloudScope-Key.pem"
$mainPy = "C:\Users\ritvi\.gemini\antigravity\scratch\prune.ai\backend\main.py"
scp -i $keyPath -o StrictHostKeyChecking=no $mainPy ubuntu@34.201.22.230:/home/ubuntu/backend/main.py
ssh -i $keyPath -o StrictHostKeyChecking=no ubuntu@34.201.22.230 "sudo fuser -k 8000/tcp; cd /home/ubuntu/backend && nohup /home/ubuntu/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 > /home/ubuntu/backend/server.log 2>&1 &"

Write-Host ""
Write-Host "ALL DEPLOYED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "- Detector Lambda: Updated" -ForegroundColor Cyan
Write-Host "- Explainer Lambda: Updated" -ForegroundColor Cyan
Write-Host "- EC2 Backend: Restarted" -ForegroundColor Cyan
