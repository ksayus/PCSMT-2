@echo off
cd /d "%~dp0"
REM OmniArk-Old build script (PyInstaller single-file exe)
REM Requires dev deps: pip install -r requirements-dev.txt
pyinstaller -F -c --name=OmniArk-Old ^
  --add-data ".\omniark\interfaces\web\templates;omniark/interfaces/web/templates" ^
  --add-data ".\omniark\interfaces\web\static;omniark/interfaces/web/static" ^
  --icon=.\omniark\interfaces\web\static\PCSMT2.ico ^
  main.py