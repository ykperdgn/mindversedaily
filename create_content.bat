@echo off 
echo Creating daily content... 
cd /d "%~dp0" 
python scripts\master_automation.py content 
pause 
