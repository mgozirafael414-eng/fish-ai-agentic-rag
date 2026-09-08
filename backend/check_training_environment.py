
import torch
import torchvision


print("=" * 50)
print("FISHAI TRAINING ENVIRONMENT CHECK")
print("=" * 50)

print(f"PyTorch version   : {torch.__version__}")
print(f"Torchvision       : {torchvision.__version__}")

print(f"CUDA available    : {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"GPU               : {torch.cuda.get_device_name(0)}")
    print(f"CUDA version      : {torch.version.cuda}")
else:
    print("GPU               : Not available")
    print("Training device   : CPU")

print("=" * 50)
print("ENVIRONMENT CHECK COMPLETED")
print("=" * 50)
