@echo off
setlocal enabledelayedexpansion

echo ------------------------------
echo  CLEANING CARL4 DATA FAST
echo ------------------------------

:: Set base folder
set "BASE_DIR=C:\Users\Joe\Dropbox\Carl4"

:: Automatically detect the settings .ini file location
set "SETTINGS_FILE=%BASE_DIR%\settings_current.ini"

:: Delete any neucogar_session_*.json files in the same folder as the .ini
if exist "%SETTINGS_FILE%" (
    echo Found settings_current.ini in: %BASE_DIR%
    echo Looking for neucogar_session_*.json files...
    del /q "%BASE_DIR%\neucogar_session_*.json"
)

:: List of subfolders to delete contents from
set SUBFOLDERS=concepts memories goals needs senses skills places people values beliefs conflicts humor exercise assets commonsense

for %%F in (%SUBFOLDERS%) do (
    set "TARGET_DIR=%BASE_DIR%\%%F"
    if exist "!TARGET_DIR!" (
        echo Deleting all files in: !TARGET_DIR!
        del /q /s "!TARGET_DIR!\*.*"
    )
)

:: Delete people and places folders if they exist (non-recursive)
for %%G in (people places) do (
    set "TARGET_PATH=%BASE_DIR%\%%G"
    if exist "!TARGET_PATH!" (
        echo Deleting all files in: !TARGET_PATH!
        del /q /s "!TARGET_PATH!\*.*"
    )
)

:: Delete specific single files
for %%F in (
    "%BASE_DIR%\settings_current.ini"
    "%BASE_DIR%\concept_graph.graphml"
	"%BASE_DIR%\emotion_3d_visualization.html"
	"%BASE_DIR%\last_direction.json"
	"%BASE_DIR%\last_position.json"
) do (
    if exist %%F (
        echo Deleting file: %%F
        del /q %%F
    )
)

:: Delete any automatic_thoughts_*.txt files in the same folder as the .ini
echo Looking for automatic_thoughts_*.txt files...
del /q /s "%BASE_DIR%\automatic_thoughts_*.txt"
	
echo.
echo ✅ Fast cleaning complete.
endlocal
pause
