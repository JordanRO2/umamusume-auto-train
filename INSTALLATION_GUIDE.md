# Umamusume Auto Train - Installation Guide

## Prerequisites Installation (PowerShell)

### Step 1: Install Python
```powershell
# Download Python installer (3.10 or higher recommended)
Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe" -OutFile "$env:TEMP\python-installer.exe"

# Install Python with PATH enabled
Start-Process -FilePath "$env:TEMP\python-installer.exe" -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1" -Wait

# Verify Python installation
python --version
```

### Step 2: Clone Repository
```powershell
# Navigate to desired directory
cd F:\Uma

# Clone the repository
git clone https://github.com/JordanRO2/umamusume-auto-train.git

# Enter project directory
cd umamusume-auto-train
```

## Setup Virtual Environment

### Step 3: Create and Activate Virtual Environment
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment (PowerShell)
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run this first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 4: Install Required Packages
```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install core requirements
pip install pyautogui
pip install opencv-python
pip install numpy
pip install Pillow
pip install pygetwindow
pip install keyboard
pip install mouse
pip install uvicorn
pip install fastapi
pip install pytesseract
pip install easyocr
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install Unity asset extraction support
pip install UnityPy

# Install additional dependencies
pip install requests
pip install python-multipart
pip install aiofiles
```

## Quick Install (All-in-One)

### Alternative: Single Command Installation
```powershell
# Navigate to project
cd F:\Uma\umamusume-auto-train

# Create venv and install everything
python -m venv venv; .\venv\Scripts\Activate.ps1; python -m pip install --upgrade pip; pip install pyautogui opencv-python numpy Pillow pygetwindow keyboard mouse uvicorn fastapi pytesseract easyocr torch torchvision --index-url https://download.pytorch.org/whl/cpu; pip install UnityPy requests python-multipart aiofiles
```

## Configuration

### Step 5: Setup Configuration
```powershell
# Copy template configuration
Copy-Item config.template.json config.json

# Edit config.json as needed (opens in notepad)
notepad config.json
```

## Running the Bot

### Step 6: Start the Bot
```powershell
# Make sure venv is activated
.\venv\Scripts\Activate.ps1

# Run the main bot
python main.py

# The bot will start on http://127.0.0.1:8000
# Press F1 to start/stop the bot
# Press F2 for debug mode
# Press F3 for step-by-step mode
# Press F4 for region editor
```

## Extracting Game Assets (Optional)

### Step 7: Extract Unity Textures
```powershell
# Activate venv if not already active
.\venv\Scripts\Activate.ps1

# Extract priority UI textures (recommended)
echo "1" | python extract_all_textures.py

# Or extract ALL textures (1000+ files)
echo "2" | python extract_all_textures.py
```

## Testing Features

### Test Debug Mode
```powershell
# Run with debug mode enabled
python main.py --debug

# Or step-by-step mode
python main.py --step
```

### Test Region Editor
```powershell
# Test the transparent overlay editor
python test_region_editor.py
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Execution Policy Error
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 2. Module Not Found Errors
```powershell
# Reinstall specific package
pip uninstall [package-name]
pip install [package-name]
```

#### 3. Screen Resolution Issues
```powershell
# Bot requires 1920x1080 resolution
# Set your display to 1920x1080 before running
```

#### 4. Game Window Not Found
```powershell
# Make sure game is running
# Check window name in config.json matches your game
# For DMM version: "Umamusume"
# For Steam version: might be different
```

## Complete Setup Script

Save this as `setup.ps1` and run it:

```powershell
# Complete setup script
Write-Host "Setting up Umamusume Auto Train..." -ForegroundColor Green

# Create venv
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate venv
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install requirements
Write-Host "Installing requirements..." -ForegroundColor Yellow
pip install pyautogui opencv-python numpy Pillow pygetwindow keyboard mouse
pip install uvicorn fastapi pytesseract easyocr
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install UnityPy requests python-multipart aiofiles

# Copy config
Write-Host "Setting up configuration..." -ForegroundColor Yellow
if (!(Test-Path "config.json")) {
    Copy-Item config.template.json config.json
    Write-Host "Created config.json from template" -ForegroundColor Green
}

Write-Host "Setup complete!" -ForegroundColor Green
Write-Host "Run 'python main.py' to start the bot" -ForegroundColor Cyan
```

## Running After Installation

Every time you want to run the bot:

```powershell
# Navigate to project
cd F:\Uma\umamusume-auto-train

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run bot
python main.py
```

## Updating the Bot

```powershell
# Pull latest changes
git pull

# Activate venv
.\venv\Scripts\Activate.ps1

# Update packages if needed
pip install -r requirements.txt --upgrade
```