#!/usr/bin/env python3
"""Check CUDA and GPU availability"""

import sys
try:
    import torch
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    print(f"CUDA version: {torch.version.cuda if torch.cuda.is_available() else 'N/A'}")
    print(f"cuDNN version: {torch.backends.cudnn.version() if torch.cuda.is_available() else 'N/A'}")
    print(f"Number of GPUs: {torch.cuda.device_count()}")

    if torch.cuda.is_available():
        print(f"Current GPU: {torch.cuda.get_device_name(0)}")
        print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
    else:
        print("\nCUDA not available. Possible reasons:")
        print("1. No NVIDIA GPU present")
        print("2. NVIDIA drivers not installed or outdated")
        print("3. PyTorch CPU version installed instead of CUDA")
        print("4. CUDA toolkit version mismatch")

    # Check if this is CPU or CUDA build
    if '+cu' in torch.__version__:
        print(f"\n✓ PyTorch CUDA build detected: {torch.__version__}")
    else:
        print(f"\n✗ PyTorch CPU build detected: {torch.__version__}")
        print("Run: pip uninstall torch torchvision torchaudio -y")
        print("Then: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")

except ImportError as e:
    print(f"Error importing torch: {e}")
    sys.exit(1)

# Check EasyOCR
try:
    import easyocr
    print("\n--- EasyOCR Check ---")
    # This is where the warning comes from
    reader = easyocr.Reader(['en'], gpu=torch.cuda.is_available())
    print(f"EasyOCR using: {'GPU' if reader.device == 'cuda' else 'CPU'}")
except Exception as e:
    print(f"Error with EasyOCR: {e}")