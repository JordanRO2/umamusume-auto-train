# Windows PowerShell - Complete Installation Commands

## Copy & Paste This Entire Block into PowerShell (Run as Administrator):

```powershell
# Install Chocolatey package manager
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install Git
choco install git -y

# Install Python 3.10
choco install python310 -y

# Refresh environment variables
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Navigate to F drive and create Uma folder
cd F:\
if (!(Test-Path "Uma")) { mkdir Uma }
cd Uma

# Clone the repository
git clone https://github.com/JordanRO2/umamusume-auto-train.git
cd umamusume-auto-train

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip

# Install all requirements with CUDA support
pip install pyautogui opencv-python numpy Pillow pygetwindow keyboard mouse uvicorn fastapi pytesseract easyocr requests python-multipart aiofiles UnityPy
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Copy config template
Copy-Item config.template.json config.json

# Display success message
Write-Host "`n`n===============================================" -ForegroundColor Green
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host "`nTo run the bot:" -ForegroundColor Yellow
Write-Host "python main.py" -ForegroundColor Cyan
Write-Host "`nControls:" -ForegroundColor Yellow
Write-Host "F1 - Start/Stop bot" -ForegroundColor White
Write-Host "F2 - Debug mode" -ForegroundColor White
Write-Host "F3 - Step-by-step mode" -ForegroundColor White
Write-Host "F4 - Region editor" -ForegroundColor White

# Run the bot
python main.py
```

## Alternative: If Chocolatey is blocked, use this instead:

```powershell
# Enable scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

# Download and install Git manually
Invoke-WebRequest -Uri "https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe" -OutFile "$env:TEMP\git-installer.exe"
Start-Process -FilePath "$env:TEMP\git-installer.exe" -ArgumentList "/SILENT" -Wait

# Download and install Python
Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe" -OutFile "$env:TEMP\python-installer.exe"
Start-Process -FilePath "$env:TEMP\python-installer.exe" -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1" -Wait

# Refresh PATH
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Navigate and clone
cd F:\
if (!(Test-Path "Uma")) { mkdir Uma }
cd Uma
& "$env:ProgramFiles\Git\bin\git.exe" clone https://github.com/JordanRO2/umamusume-auto-train.git
cd umamusume-auto-train

# Setup Python environment
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install pyautogui opencv-python numpy Pillow pygetwindow keyboard mouse uvicorn fastapi pytesseract easyocr requests python-multipart aiofiles UnityPy
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
Copy-Item config.template.json config.json
python main.py
```

## After Installation - Daily Use:

```powershell
cd F:\Uma\umamusume-auto-train
.\venv\Scripts\Activate.ps1
python main.py
```