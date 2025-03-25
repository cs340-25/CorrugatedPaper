@echo off
setlocal enabledelayedexpansion

set "outputFile=combinedResults.json"
set "filePattern=searchResults*.json"

:: Create or clear the output file
type nul > "%outputFile%"

:: Loop through files 01 to 22 and append them to the output file
for /l %%i in (1,1,22) do (
    set "num=0%%i"
    set "num=!num:~-2!"
    if exist "searchResults!num!.json" (
        type "searchResults!num!.json" >> "%outputFile%"
    ) else (
        echo File "searchResults!num!.json" not found.
    )
)

echo All files have been concatenated into %outputFile%
pause