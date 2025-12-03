import sys
import torch
import os

print(f"Python version: {sys.version}")
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"CUDA version: {torch.version.cuda}")
    print(f"GPU device: {torch.cuda.get_device_name(0)}")
    
    try:
        import gsplat
        print("gsplat: Installed successfully")
    except ImportError:
        print("gsplat: Not installed")
else:
    print("WARNING: CUDA not available!")

print("\nEnvironment setup verification complete.")
