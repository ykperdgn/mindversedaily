@echo off 
echo Deploying site... 
cd /d "%~dp0" 
python scripts\master_automation.py deploy 
pause 
