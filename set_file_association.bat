@echo off
setlocal

:menu
cls
echo =========================================
echo MoonBall Archiver File Association Tool
echo =========================================
echo 1. Backup Registry
echo 2. Create System Restore Point
echo 3. Set File Associations for .mnbl and .🌕
echo 4. Exit
echo =========================================
set /p choice="Enter your choice (1-4): "

if '%choice%'=='1' goto backup_registry
if '%choice%'=='2' goto create_restore_point
if '%choice%'=='3' goto set_file_associations
if '%choice%'=='4' goto exit

echo Invalid choice, please select an option between 1 and 4.
pause
goto menu

:backup_registry
echo Backing up registry...
set backup_file=%~dp0moonball_registry_backup.reg
reg export HKCR %backup_file% /y
if %errorlevel%==0 (
    echo Registry backup successful! Saved to %backup_file%
) else (
    echo Error: Failed to backup registry.
)
pause
goto menu

:create_restore_point
echo Creating system restore point...
wmic.exe /Namespace:\\root\default Path SystemRestore Call CreateRestorePoint "MoonBall Restore Point", 100, 7
if %errorlevel%==0 (
    echo System restore point created successfully!
) else (
    echo Error: Failed to create system restore point.
)
pause
goto menu

:set_file_associations
echo Setting file associations for .mnbl and .🌕 extensions...
set icon_path=%~dp0assets\moonball_file.ico
if not exist "%icon_path%" (
    echo Error: moonball_file.ico not found in the assets folder.
    pause
    goto menu
)

rem Create registry entries for .mnbl
reg add "HKCR\.mnbl" /ve /d "MoonBallFile" /f
reg add "HKCR\MoonBallFile" /ve /d "MoonBall File" /f
reg add "HKCR\MoonBallFile\DefaultIcon" /ve /d "\"%icon_path%\"" /f
reg add "HKCR\MoonBallFile\shell\open\command" /ve /d "\"%~dp0moonball_archiver.exe\" \"%%1\"" /f

rem Create registry entries for .🌕
reg add "HKCR\.🌕" /ve /d "MoonBallFile" /f

if %errorlevel%==0 (
    echo File associations set successfully!
) else (
    echo Error: Failed to set file associations.
)
pause
goto menu

:exit
echo Exiting the program.
endlocal
exit