@echo off
REM ==========================================================
REM  DW_CollisionCheck  Build and Deploy
REM   1) Concatenate _build/src/*.txt into DW_CollisionCheck.py
REM   2) Pull latest from GitHub
REM   3) Commit and push
REM ==========================================================

setlocal EnableDelayedExpansion

REM --- Move to this bat file's folder -----------------------
cd /d "%~dp0"

echo.
echo ============================================
echo  DW_CollisionCheck  Build and Deploy
echo ============================================
echo.

REM ==========================================================
REM  STEP 1: Build DW_CollisionCheck.py
REM ==========================================================
echo [1/4] Building DW_CollisionCheck.py ...
echo.

set "OUT=DW_CollisionCheck.py"
if exist "%OUT%" del "%OUT%"

if not exist "_build\src" (
    echo [ERROR] _build\src folder not found.
    pause
    exit /b 1
)

set /a COUNT=0
for /f "delims=" %%F in ('dir /b /on "_build\src\*.txt"') do (
    echo   + %%F
    type "_build\src\%%F" >> "%OUT%"
    echo.>> "%OUT%"
    set /a COUNT+=1
)

if "!COUNT!"=="0" (
    echo [ERROR] No .txt files in _build\src\
    pause
    exit /b 1
)

if not exist "%OUT%" (
    echo [ERROR] Build failed.
    pause
    exit /b 1
)

for %%A in ("%OUT%") do set "SIZE=%%~zA"
echo.
echo   Built: %OUT%  ^(!SIZE! bytes, !COUNT! files^)
echo.

REM ==========================================================
REM  STEP 2: Check git
REM ==========================================================
echo [2/4] Checking git ...

if not exist ".git" (
    echo [ERROR] Not a git repository.
    echo         Run: git init
    echo              git remote add origin https://github.com/Kiasejapan/DW_CollisionCheck.git
    pause
    exit /b 1
)

where git >nul 2>&1
if errorlevel 1 (
    echo [ERROR] git command not found in PATH.
    pause
    exit /b 1
)

echo   OK
echo.

REM ==========================================================
REM  STEP 3: Pull latest
REM ==========================================================
echo [3/4] Pulling latest from GitHub ...
echo.

git pull --rebase
if errorlevel 1 (
    echo.
    echo [WARN] git pull failed.
    echo        Resolve conflicts manually, then re-run.
    pause
    exit /b 1
)
echo.

REM ==========================================================
REM  STEP 4: Commit and push
REM ==========================================================
echo [4/4] Commit and push ...
echo.

git add .
if errorlevel 1 goto git_error

git diff --cached --quiet
if not errorlevel 1 (
    echo.
    echo   No changes to commit. Skipping push.
    echo.
    echo ============================================
    echo  Done.  No changes.
    echo ============================================
    echo.
    pause
    exit /b 0
)

set "MSG=%*"
if "!MSG!"=="" set "MSG=build"

git commit -m "!MSG!"
if errorlevel 1 goto git_error

git push
if errorlevel 1 goto git_error

echo.
echo ============================================
echo  Done!
echo    Local : %OUT%
echo    GitHub: https://github.com/Kiasejapan/DW_CollisionCheck
echo ============================================
echo.
pause
exit /b 0

:git_error
echo.
echo [ERROR] git operation failed. See messages above.
pause
exit /b 1
