@echo off

REM Check if Python is installed using the py launcher
py -3 --version >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed.
    echo Downloading and installing Python...
   
    curl -o python-installer.exe https://www.python.org/ftp/python/3.9.6/python-3.9.6-amd64.exe
    
    start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
    
    del python-installer.exe
    
    REM Verify installation
    py -3 --version >nul 2>nul
    IF %ERRORLEVEL% NEQ 0 (
        echo Failed to install Python.
        exit /b 1
    )
)

REM Install required Python packages
py -3 -m pip install --upgrade pip
py -3 -m pip install pypdf2 tk

echo Python and dependencies installed successfully.
pause
