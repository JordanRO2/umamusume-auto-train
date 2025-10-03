# Quick Install Commands - Copy & Paste

## Full Installation (PowerShell)

```powershell
# Clone repository
cd F:\Uma
git clone https://github.com/JordanRO2/umamusume-auto-train.git
cd umamusume-auto-train

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install all packages
python -m pip install --upgrade pip
pip install pyautogui opencv-python numpy Pillow pygetwindow keyboard mouse uvicorn fastapi pytesseract easyocr requests python-multipart aiofiles UnityPy

# Install PyTorch (CPU version)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Copy configuration
Copy-Item config.template.json config.json

# Run the bot
python main.py
```

## One-Line Installation (After Cloning)

```powershell
python -m venv venv; .\venv\Scripts\Activate.ps1; python -m pip install --upgrade pip; pip install pyautogui opencv-python numpy Pillow pygetwindow keyboard mouse uvicorn fastapi pytesseract easyocr requests python-multipart aiofiles UnityPy; pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu; Copy-Item config.template.json config.json; python main.py
```

## Daily Usage (After Installation)

```powershell
cd F:\Uma\umamusume-auto-train
.\venv\Scripts\Activate.ps1
python main.py
```

## Extract Game Assets (Optional)

```powershell
.\venv\Scripts\Activate.ps1
echo 1 | python extract_all_textures.py
```

## If Execution Policy Error

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```