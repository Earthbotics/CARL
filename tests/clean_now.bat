@echo off
echo Deleting files from the "memories" and "concepts" subfolders...

REM -- Move all files in "concepts" (including subfolders) to Recycle Bin
for /r "C:\Users\Joe\Dropbox\Carl4\concepts" %%A in (*) do (
    if not "%%~fA"=="%~f0" call :MoveFile "%%~fA"
)

REM -- Move all files in "memories" (including subfolders) to Recycle Bin
for /r "C:\Users\Joe\Dropbox\Carl4\memories" %%A in (*) do (
    if not "%%~fA"=="%~f0" call :MoveFile "%%~fA"
)


REM -- Move all files in "goals" (including subfolders) to Recycle Bin
for /r "C:\Users\Joe\Dropbox\Carl4\goals" %%A in (*) do (
    if not "%%~fA"=="%~f0" call :MoveFile "%%~fA"
)

REM -- Move all files in "needs" (including subfolders) to Recycle Bin
for /r "C:\Users\Joe\Dropbox\Carl4\needs" %%A in (*) do (
    if not "%%~fA"=="%~f0" call :MoveFile "%%~fA"
)

REM -- Move all files in "senses" (including subfolders) to Recycle Bin
for /r "C:\Users\Joe\Dropbox\Carl4\senses" %%A in (*) do (
    if not "%%~fA"=="%~f0" call :MoveFile "%%~fA"
)

REM -- Move all files in "skills" (including subfolders) to Recycle Bin
for /r "C:\Users\Joe\Dropbox\Carl4\skills" %%A in (*) do (
    if not "%%~fA"=="%~f0" call :MoveFile "%%~fA"
)
REM -- Move all files in "values" (including subfolders) to Recycle Bin
for /r "C:\Users\Joe\Dropbox\Carl4\values" %%A in (*) do (
    if not "%%~fA"=="%~f0" call :MoveFile "%%~fA"
)
REM -- Move all files in "people" (including subfolders) to Recycle Bin
if exist "C:\Users\Joe\Dropbox\Carl4\people" call :MoveFile "C:\Users\Joe\Dropbox\Carl4\people"

REM -- Move all files in "places" (including subfolders) to Recycle Bin
if exist "C:\Users\Joe\Dropbox\Carl4\places" call :MoveFile "C:\Users\Joe\Dropbox\Carl4\places"

REM -- Move "settings_current.ini"
if exist "C:\Users\Joe\Dropbox\Carl4\settings_current.ini" call :MoveFile "C:\Users\Joe\Dropbox\Carl4\settings_current.ini"

REM -- Move "concept_graph.graphml"
if exist "C:\Users\Joe\Dropbox\Carl4\concept_graph.graphml" call :MoveFile "C:\Users\Joe\Dropbox\Carl4\concept_graph.graphml" 


echo.
echo All matching files have been moved to the Recycle Bin.
exit /b

:MoveFile
echo Moving file "%~1" to the Recycle Bin...

REM -- Create a temporary VBScript to use Shell.Application
echo Set objShell = CreateObject("Shell.Application") > "%TEMP%\temp_vbs.vbs"
echo objShell.Namespace(10).MoveHere "%~1" >> "%TEMP%\temp_vbs.vbs"

REM -- Run the VBScript (no console output) 
cscript //nologo "%TEMP%\temp_vbs.vbs"

REM -- Remove the temporary script
del "%TEMP%\temp_vbs.vbs"

exit /b

