@echo off
REM =====================================================
REM  DW_CollisionCheck build & deploy
REM  1) Concatenates _build/src/*.txt into DW_CollisionCheck.py
REM  2) Commits and pushes to GitHub
REM =====================================================
setlocal enabledelayedexpansion

echo.
echo [1/3] Building DW_CollisionCheck.py from _build/src/...
echo.

set OUT=DW_CollisionCheck.py
if exist "%OUT%" del "%OUT%"

REM Concatenate all .txt files in _build/src in sorted order
for /f "delims=" %%F in ('dir /b /on "_build\src\*.txt"') do (
    echo   + _build\src\%%F
    type "_build\src\%%F" >> "%OUT%"
    echo.>> "%OUT%"
)

if not exist "%OUT%" (
    echo.
    echo [ERROR] Build failed: %OUT% not generated.
    pause
    exit /b 1
)

echo.
echo   Built: %OUT%
for %%A in ("%OUT%") do echo   Size : %%~zA bytes

echo.
echo [2/3] Staging and committing...
echo.

git add .
if errorlevel 1 goto git_error

REM Use current date/time for the commit message if no arg supplied
set MSG=%*
if "%MSG%"=="" set MSG=build %DATE% %TIME%

git commit -m "%MSG%"
REM Don't abort on "nothing to commit"
if errorlevel 1 (
    echo   ^(nothing to commit, or commit skipped^)
)

echo.
echo [3/3] Pushing to GitHub...
echo.

git push
if errorlevel 1 goto git_error

echo.
echo ============================================
echo  Done. %OUT% is up to date.
echo ============================================
echo.
pause
exit /b 0

:git_error
echo.
echo [ERROR] git operation failed.
pause
exit /b 1
