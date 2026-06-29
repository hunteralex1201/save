@echo off
REM ====================================================================
REM  Personal Downloader Server - start script (Windows)
REM  Prothombar double-click korle: venv banabe, package install korbe,
REM  tarpor server চালু hobe. Porer bar sudhu server চালু hobe.
REM ====================================================================
cd /d "%~dp0"

REM ---- ffmpeg ase kina check ----
where ffmpeg >nul 2>nul
if errorlevel 1 (
    echo [!] ffmpeg paoa jayni. HD video + mp3 er jonno eta dorkar.
    echo     Install korte: winget install Gyan.FFmpeg   ^(tarpor ei window bondho kore abar cholao^)
    echo.
)

REM ---- venv toiri (sudhu prothombar) ----
if not exist ".venv" (
    echo [*] Virtual environment toiri hocche...
    python -m venv .venv
    call ".venv\Scripts\activate.bat"
    echo [*] Package install hocche...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
) else (
    call ".venv\Scripts\activate.bat"
    echo [*] yt-dlp update hocche (site change hole jate kaj kore)...
    pip install --upgrade yt-dlp
)

echo.
echo ====================================================================
echo  Tomar PC er local IP gulo (ekta diye iPhone theke connect korbe):
ipconfig | findstr /C:"IPv4"
echo  iPhone Shortcut e likhbe:  http://^<oi IP^>:8000/dl
echo ====================================================================
echo.

python server.py
pause
