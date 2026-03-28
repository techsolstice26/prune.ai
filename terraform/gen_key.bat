@echo off
set PAGER=
aws ec2 delete-key-pair --key-name CloudScope-Key --region us-east-1
del /f CloudScope-Key.pem 2>nul
aws ec2 create-key-pair --key-name CloudScope-Key --region us-east-1 --query KeyMaterial --output text > CloudScope-Key.pem
echo Done. File size:
for %%A in (CloudScope-Key.pem) do echo %%~zA bytes
