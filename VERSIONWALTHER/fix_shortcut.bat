@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "PYTHON_EXE=pythonw.exe"
set "GAME_SCRIPT=juego.py"
set "SHORTCUT_NAME=Block Maze"
set "ICON_PATH=%SCRIPT_DIR%assets\player\CRISTAL.ico"

REM Create a VBS script to create the shortcut
set "VBS_SCRIPT=%TEMP%\CreateShortcut.vbs"

echo Set oWS = WScript.CreateObject("WScript.Shell") > "%VBS_SCRIPT%"
echo sLinkFile = oWS.ExpandEnvironmentStrings("%%USERPROFILE%%\Desktop\%SHORTCUT_NAME%.lnk") >> "%VBS_SCRIPT%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%VBS_SCRIPT%"
echo oLink.TargetPath = "%PYTHON_EXE%" >> "%VBS_SCRIPT%"
echo oLink.Arguments = """%SCRIPT_DIR%%GAME_SCRIPT%""" >> "%VBS_SCRIPT%"
echo oLink.WorkingDirectory = "%SCRIPT_DIR%" >> "%VBS_SCRIPT%"

REM Check if icon exists, if not convert PNG to ICO
if not exist "%ICON_PATH%" (
    echo Converting PNG to ICO...
    python -c "from PIL import Image; Image.open(r'%SCRIPT_DIR%assets\player\CRISTAL.png').resize((256, 256)).save(r'%ICON_PATH%', format='ICO')" 2>nul
)

if exist "%ICON_PATH%" (
    echo oLink.IconLocation = "%ICON_PATH%" >> "%VBS_SCRIPT%"
) else (
    echo oLink.IconLocation = "%%WINDIR%%\System32\SHELL32.dll,1" >> "%VBS_SCRIPT%"
)

echo oLink.Save >> "%VBS_SCRIPT%"

REM Run the VBS script
cscript //nologo "%VBS_SCRIPT%"

del "%VBS_SCRIPT%" 2>nul

echo.
echo Shortcut created successfully on your desktop: %SHORTCUT_NAME%.lnk
echo.
pause
