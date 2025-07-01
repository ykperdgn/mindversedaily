@echo off 
echo Running system health check... 
cd /d "%~dp0" 
python scripts\master_automation.py health 
pause 
