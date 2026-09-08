import os
import json
import torch

from torchvision import datasets, transforms
from torch.utils.data import DataLoader


# ==========================================
# DATASET CONFIGURATION
# ==========================================

DATASET_ROOT = r"C:\Users\HomePC\Documents\fish_dataset_split"

TRAIN_DIR = os.path.join(DATASET_ROOT, "train")
VAL_DIR = os.path.join(DATASET_ROOT, "val")
TEST_DIR = os.path.join(DATASET_ROOT, "test")

BATCH_SIZE = 16
IMAGE_SIZE = 224
NUM_WORKERS = 0

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# ==========================================
# NORMALIZATION
# ==========================================

NORMALIZE = transforms.Normalize(
    mean=[0.485, 0.456, 0.406],
    std=[0.229, 0.224, 0.225]
)


# ==========================================
# TRAINING AUGMENTATION
# ==========================================

train_transforms = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),

    transforms.RandomHorizontalFlip(p=0.5),

    transforms.RandomRotation(10),

    transforms.ColorJitter(
        brightness=0.2,
        contrast=0.2,
        saturation=0.2
    ),

    transforms.ToTensor(),

    NORMALIZE
])


# ==========================================
# VALIDATION / TEST TRANSFORMS
# ==========================================

val_test_transforms = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),

    transforms.ToTensor(),

    NORMALIZE
])


# ==========================================
# START
# ==========================================

print("=" * 60)
print("FISHAI DATA LOADER TEST")
print("=" * 60)

print(f"Dataset root : {DATASET_ROOT}")
print(f"Device       : {DEVICE}")
print(f"Image size   : {IMAGE_SIZE} x {IMAGE_SIZE}")
print(f"Batch size   : {BATCH_SIZE}")

print("\nLoading datasets...")


# ==========================================
# TRAIN DATASET
# ==========================================

train_dataset = datasets.ImageFolder(
    root=TRAIN_DIR,
    transform=train_transforms,
    allow_empty=True
)


# ==========================================
# VALIDATION DATASET
# ==========================================

val_dataset = datasets.ImageFolder(
    root=VAL_DIR,
    transform=val_test_transforms,
    allow_empty=True
)


# ==========================================
# TEST DATASET
# ==========================================

test_dataset = datasets.ImageFolder(
    root=TEST_DIR,
    transform=val_test_transforms,
    allow_empty=True
)


# ==========================================
# CHECK CLASS MAPPINGS
# ==========================================

if train_dataset.class_to_idx != val_dataset.class_to_idx:
    raise ValueError(
        "ERROR: Train and Validation class mappings do not match."
    )

if train_dataset.class_to_idx != test_dataset.class_to_idx:
    raise ValueError(
        "ERROR: Train and Test class mappings do not match."
    )


# ==========================================
# DATASET INFORMATION
# ==========================================

print("\nDATASET INFORMATION")
print("-" * 60)

print(f"Number of classes : {len(train_dataset.classes)}")
print(f"Training images   : {len(train_dataset)}")
print(f"Validation images : {len(val_dataset)}")
print(f"Testing images    : {len(test_dataset)}")


# ==========================================
# FIRST 10 CLASSES
# ==========================================

print("\nFIRST 10 CLASSES")
print("-" * 60)

for index, class_name in enumerate(
    train_dataset.classes[:10]
):
    print(f"{index}: {class_name}")


# ==========================================
# CREATE DATALOADERS
# ==========================================

train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True,
    num_workers=NUM_WORKERS
)

val_loader = DataLoader(
    val_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=NUM_WORKERS
)

test_loader = DataLoader(
    test_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=NUM_WORKERS
)


# ==========================================
# TEST TRAINING DATALOADER
# ==========================================

print("\nTESTING TRAINING DATALOADER")
print("-" * 60)

images, labels = next(iter(train_loader))

print(f"Images tensor shape : {images.shape}")
print(f"Labels tensor shape : {labels.shape}")
print(f"Images data type    : {images.dtype}")
print(f"Labels data type    : {labels.dtype}")

print("\nFirst batch labels:")
print(labels)


# ==========================================
# TEST VALIDATION DATALOADER
# ==========================================

print("\nTESTING VALIDATION DATALOADER")
print("-" * 60)

val_images, val_labels = next(iter(val_loader))

print(
    f"Validation images shape : {val_images.shape}"
)

print(
    f"Validation labels shape : {val_labels.shape}"
)


# ==========================================
# TEST TESTING DATALOADER
# ==========================================

print("\nTESTING TESTING DATALOADER")
print("-" * 60)

test_images, test_labels = next(iter(test_loader))

print(
    f"Test images shape : {test_images.shape}"
)

print(
    f"Test labels shape : {test_labels.shape}"
)


# ==========================================
# SAVE CLASS NAMES
# ==========================================

class_names_path = os.path.join(
    DATASET_ROOT,
    "class_names.json"
)

with open(
    class_names_path,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        train_dataset.classes,
        file,
        indent=4,
        ensure_ascii=False
    )


# ==========================================
# FINAL RESULT
# ==========================================

print("\nCLASS NAMES SAVED")
print("-" * 60)

print(class_names_path)

print("\n" + "=" * 60)
print("DATA LOADER CHECK COMPLETED")
print("=" * 60)

print(
    f"Classes             : {len(train_dataset.classes)}"
)

print(
    f"Training images     : {len(train_dataset)}"
)

print(
    f"Validation images   : {len(val_dataset)}"
)

print(
    f"Testing images      : {len(test_dataset)}"
)

print(
    f"Training batch      : {images.shape}"
)

print(
    f"Validation batch    : {val_images.shape}"
)

print(
    f"Testing batch       : {test_images.shape}"
)

print("\nData preprocessing is working correctly.")

print("We have NOT trained the model yet.")

print("=" * 60)
