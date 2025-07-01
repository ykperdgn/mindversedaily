@echo off 
echo Monitoring site performance... 
cd /d "%~dp0" 
python scripts\performance_monitor.py check 
pause 
