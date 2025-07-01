@echo off 
echo Creating automation dashboard... 
cd /d "%~dp0" 
python create_dashboard.py 
start automation_dashboard.html 
pause 
