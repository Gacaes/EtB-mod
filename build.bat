@echo off
python -m PyInstaller main.py -n EtB_Installer_v.1.0 -F -c
cls
echo EXE built, press ENTER to close
pause