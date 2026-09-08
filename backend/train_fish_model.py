
import os
import json
import copy

import torch
import torch.nn as nn
import torch.optim as optim

from torchvision import datasets, transforms
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights
from torch.utils.data import DataLoader


# ============================================================
# CONFIGURATION
# ============================================================

DATASET_ROOT = r"C:\Users\HomePC\Documents\fish_dataset_split"

TRAIN_DIR = os.path.join(DATASET_ROOT, "train")
VAL_DIR = os.path.join(DATASET_ROOT, "val")

MODEL_DIR = r"C:\Users\HomePC\fish-ai-agentic-rag\backend\models"

os.makedirs(MODEL_DIR, exist_ok=True)


# ============================================================
# TRAINING SETTINGS
# ============================================================

IMAGE_SIZE = 224
BATCH_SIZE = 32

# Initial training
CLASSIFIER_EPOCHS = 5

# Fine tuning
FINETUNE_EPOCHS = 10

LEARNING_RATE = 0.001
FINETUNE_LEARNING_RATE = 0.0001

NUM_WORKERS = 2


# ============================================================
# DEVICE
# ============================================================

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("=" * 70)
print("FISHAI — EFFICIENTNET-B0 TRAINING")
print("=" * 70)

print(f"Device       : {DEVICE}")
print(f"Image size   : {IMAGE_SIZE} x {IMAGE_SIZE}")
print(f"Batch size   : {BATCH_SIZE}")
print(f"Classifier epochs : {CLASSIFIER_EPOCHS}")
print(f"Fine-tuning epochs: {FINETUNE_EPOCHS}")


# ============================================================
# IMAGE TRANSFORMS
# ============================================================

weights = EfficientNet_B0_Weights.DEFAULT

imagenet_mean = [0.485, 0.456, 0.406]
imagenet_std = [0.229, 0.224, 0.225]


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

    transforms.Normalize(
        mean=imagenet_mean,
        std=imagenet_std
    )
])


val_transforms = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),

    transforms.ToTensor(),

    transforms.Normalize(
        mean=imagenet_mean,
        std=imagenet_std
    )
])


# ============================================================
# LOAD DATASETS
# ============================================================

print("\nLoading datasets...")

train_dataset = datasets.ImageFolder(
    root=TRAIN_DIR,
    transform=train_transforms,
    allow_empty=True
)

val_dataset = datasets.ImageFolder(
    root=VAL_DIR,
    transform=val_transforms,
    allow_empty=True
)


# ============================================================
# CLASS MAPPING CHECK
# ============================================================

if train_dataset.class_to_idx != val_dataset.class_to_idx:

    raise ValueError(
        "ERROR: Train and Validation class mappings do not match."
    )


class_names = train_dataset.classes
num_classes = len(class_names)


print("\nDATASET INFORMATION")
print("-" * 70)

print(f"Number of classes : {num_classes}")
print(f"Training images   : {len(train_dataset)}")
print(f"Validation images : {len(val_dataset)}")


# ============================================================
# SAVE CLASS NAMES
# ============================================================

class_names_path = os.path.join(
    MODEL_DIR,
    "class_names.json"
)

with open(
    class_names_path,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        class_names,
        file,
        indent=4,
        ensure_ascii=False
    )

print(f"\nClass names saved:")
print(class_names_path)


# ============================================================
# DATALOADERS
# ============================================================

train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True,
    num_workers=NUM_WORKERS,
    pin_memory=True if DEVICE.type == "cuda" else False
)

val_loader = DataLoader(
    val_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=NUM_WORKERS,
    pin_memory=True if DEVICE.type == "cuda" else False
)


# ============================================================
# CREATE EFFICIENTNET-B0
# ============================================================

print("\nCreating EfficientNet-B0...")

model = efficientnet_b0(
    weights=weights
)


# ============================================================
# REPLACE CLASSIFICATION HEAD
# ============================================================

in_features = model.classifier[1].in_features

model.classifier[1] = nn.Linear(
    in_features,
    num_classes
)


model = model.to(DEVICE)


print("\nMODEL INFORMATION")
print("-" * 70)

print("Model          : EfficientNet-B0")
print("Pretrained     : ImageNet")
print(f"Output classes : {num_classes}")
print(f"Device         : {DEVICE}")


# ============================================================
# PHASE 1 — FREEZE BACKBONE
# ============================================================

print("\n" + "=" * 70)
print("PHASE 1 — TRAIN CLASSIFICATION HEAD")
print("=" * 70)

for parameter in model.features.parameters():
    parameter.requires_grad = False


criterion = nn.CrossEntropyLoss()


optimizer = optim.Adam(
    model.classifier.parameters(),
    lr=LEARNING_RATE
)


# ============================================================
# TRAINING FUNCTION
# ============================================================

def train_one_epoch(
    model,
    loader,
    criterion,
    optimizer,
    device
):

    model.train()

    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels in loader:

        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()

        outputs = model(images)

        loss = criterion(
            outputs,
            labels
        )

        loss.backward()

        optimizer.step()

        running_loss += (
            loss.item() * images.size(0)
        )

        _, predictions = torch.max(
            outputs,
            1
        )

        total += labels.size(0)

        correct += (
            predictions == labels
        ).sum().item()

    epoch_loss = running_loss / total

    epoch_accuracy = correct / total

    return epoch_loss, epoch_accuracy


# ============================================================
# VALIDATION FUNCTION
# ============================================================

def validate(
    model,
    loader,
    criterion,
    device
):

    model.eval()

    running_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():

        for images, labels in loader:

            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)

            loss = criterion(
                outputs,
                labels
            )

            running_loss += (
                loss.item() * images.size(0)
            )

            _, predictions = torch.max(
                outputs,
                1
            )

            total += labels.size(0)

            correct += (
                predictions == labels
            ).sum().item()

    epoch_loss = running_loss / total

    epoch_accuracy = correct / total

    return epoch_loss, epoch_accuracy


# ============================================================
# BEST MODEL TRACKING
# ============================================================

best_val_accuracy = 0.0

best_model_weights = copy.deepcopy(
    model.state_dict()
)


# ============================================================
# PHASE 1 TRAINING
# ============================================================

for epoch in range(
    CLASSIFIER_EPOCHS
):

    print(
        f"\nEpoch "
        f"{epoch + 1}/"
        f"{CLASSIFIER_EPOCHS}"
    )

    train_loss, train_accuracy = train_one_epoch(
        model,
        train_loader,
        criterion,
        optimizer,
        DEVICE
    )

    val_loss, val_accuracy = validate(
        model,
        val_loader,
        criterion,
        DEVICE
    )

    print(
        f"Train Loss: {train_loss:.4f}"
    )

    print(
        f"Train Accuracy: "
        f"{train_accuracy:.4f}"
    )

    print(
        f"Validation Loss: "
        f"{val_loss:.4f}"
    )

    print(
        f"Validation Accuracy: "
        f"{val_accuracy:.4f}"
    )

    if val_accuracy > best_val_accuracy:

        best_val_accuracy = val_accuracy

        best_model_weights = copy.deepcopy(
            model.state_dict()
        )

        print("✓ New best model")


# ============================================================
# PHASE 2 — FINE TUNING
# ============================================================

print("\n" + "=" * 70)
print("PHASE 2 — FINE-TUNING EFFICIENTNET-B0")
print("=" * 70)


# Unfreeze the entire feature extractor

for parameter in model.features.parameters():
    parameter.requires_grad = True


optimizer = optim.Adam(
    model.parameters(),
    lr=FINETUNE_LEARNING_RATE
)


# ============================================================
# FINE-TUNING
# ============================================================

for epoch in range(
    FINETUNE_EPOCHS
):

    print(
        f"\nFine-tuning Epoch "
        f"{epoch + 1}/"
        f"{FINETUNE_EPOCHS}"
    )

    train_loss, train_accuracy = train_one_epoch(
        model,
        train_loader,
        criterion,
        optimizer,
        DEVICE
    )

    val_loss, val_accuracy = validate(
        model,
        val_loader,
        criterion,
        DEVICE
    )

    print(
        f"Train Loss: {train_loss:.4f}"
    )

    print(
        f"Train Accuracy: "
        f"{train_accuracy:.4f}"
    )

    print(
        f"Validation Loss: "
        f"{val_loss:.4f}"
    )

    print(
        f"Validation Accuracy: "
        f"{val_accuracy:.4f}"
    )

    if val_accuracy > best_val_accuracy:

        best_val_accuracy = val_accuracy

        best_model_weights = copy.deepcopy(
            model.state_dict()
        )

        print("✓ New best model")


# ============================================================
# LOAD BEST WEIGHTS
# ============================================================

model.load_state_dict(
    best_model_weights
)


# ============================================================
# SAVE BEST MODEL
# ============================================================

best_model_path = os.path.join(
    MODEL_DIR,
    "fish_efficientnet_b0_best.pth"
)


torch.save(
    {
        "model_state_dict": model.state_dict(),

        "class_names": class_names,

        "num_classes": num_classes,

        "image_size": IMAGE_SIZE,

        "model_name": "efficientnet_b0",

        "best_validation_accuracy":
            best_val_accuracy
    },
    best_model_path
)


# ============================================================
# FINAL RESULT
# ============================================================

print("\n" + "=" * 70)
print("TRAINING COMPLETED")
print("=" * 70)

print(
    f"Best validation accuracy: "
    f"{best_val_accuracy:.4f}"
)

print("\nBest model saved to:")

print(best_model_path)

print("\nClass names saved to:")

print(class_names_path)

print("=" * 70)
