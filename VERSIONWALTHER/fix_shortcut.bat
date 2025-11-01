@echo off
setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "PYTHON_EXE=pythonw.exe"
set "GAME_SCRIPT=juego.py"
set "SHORTCUT_NAME=Block Maze"
set "ICON_PATH=%SCRIPT_DIR%assets\player\CRISTAL.ico"

REM Get the user's desktop path
for /f "tokens=2*" %%a in ('reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders" /v "Desktop" ^| find "REG_"') do set "DESKTOP_PATH=%%~b"

REM Expand any environment variables in the path
call :ExpandVars "DESKTOP_PATH"

REM Create a VBS script to create the shortcut
set "VBS_SCRIPT=%TEMP%\CreateShortcut.vbs"

echo Set oWS = WScript.CreateObject("WScript.Shell") > "%VBS_SCRIPT%"
echo desktopPath = oWS.ExpandEnvironmentStrings("!DESKTOP_PATH!") >> "%VBS_SCRIPT%"
echo Set fso = CreateObject("Scripting.FileSystemObject") >> "%VBS_SCRIPT%"
echo If Not fso.FolderExists(desktopPath) Then >> "%VBS_SCRIPT%"
echo   Set shell = CreateObject("Shell.Application") >> "%VBS_SCRIPT%"
echo   Set objFolder = shell.Namespace("0x0010") ' CSIDL_DESKTOP >> "%VBS_SCRIPT%"
echo   desktopPath = objFolder.Self.Path >> "%VBS_SCRIPT%"
echo End If >> "%VBS_SCRIPT%"
echo sLinkFile = fso.BuildPath(desktopPath, "%SHORTCUT_NAME%.lnk") >> "%VBS_SCRIPT%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%VBS_SCRIPT%"
echo oLink.TargetPath = "%PYTHON_EXE%" >> "%VBS_SCRIPT%"
echo oLink.Arguments = """%SCRIPT_DIR%%GAME_SCRIPT%""" >> "%VBS_SCRIPT%"
echo oLink.WorkingDirectory = "%SCRIPT_DIR%" >> "%VBS_SCRIPT%"

REM Check if icon exists, if not convert PNG to ICO
if not exist "%ICON_PATH%" (
    if exist "%SCRIPT_DIR%assets\player\CRISTAL.png" (
        echo Converting PNG to ICO...
        python -c "from PIL import Image; Image.open(r'%SCRIPT_DIR%assets\player\CRISTAL.png').resize((256, 256)).save(r'%ICON_PATH%', format='ICO')" 2>nul
    )
)

if exist "%ICON_PATH%" (
    echo oLink.IconLocation = "%ICON_PATH%" >> "%VBS_SCRIPT%"
) else (
    echo oLink.IconLocation = "%%WINDIR%%\System32\SHELL32.dll,1" >> "%VBS_SCRIPT%"
)

echo oLink.Save >> "%VBS_SCRIPT%"
echo WScript.Echo "Shortcut created at: " ^& sLinkFile >> "%VBS_SCRIPT%"

REM Run the VBS script
cscript //nologo "%VBS_SCRIPT%"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Shortcut created successfully on your desktop: %SHORTCUT_NAME%.lnk
) else (
    echo.
    echo Failed to create shortcut. Please run this script as Administrator.
)

del "%VBS_SCRIPT%" 2>nul

echo.
pause

goto :eof

:ExpandVars
set "%~1=!%~1!"
goto :eof
