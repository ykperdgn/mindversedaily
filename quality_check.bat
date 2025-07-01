@echo off 
echo Running quality control... 
cd /d "%~dp0" 
python scripts\quality_control.py both 
pause 
