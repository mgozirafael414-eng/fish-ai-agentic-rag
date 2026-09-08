# ============================================================
# FISHAI — FISH MODEL SERVICE
# EfficientNet-B0 Fish Species Classification
# ============================================================

import json
from pathlib import Path

import torch
import torch.nn as nn

from PIL import Image
from torchvision import models, transforms


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_DIR = BASE_DIR / "models"

MODEL_PATH = (
    MODEL_DIR /
    "fish_efficientnet_b0_best_phase2.pth"
)

CLASS_NAMES_PATH = (
    MODEL_DIR /
    "class_names.json"
)


# ============================================================
# DEVICE
# ============================================================

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# ============================================================
# LOAD CLASS NAMES
# ============================================================

with open(
    CLASS_NAMES_PATH,
    "r",
    encoding="utf-8"
) as file:

    CLASS_NAMES = json.load(file)


NUM_CLASSES = len(CLASS_NAMES)


# ============================================================
# CREATE EFFICIENTNET-B0
# ============================================================

model = models.efficientnet_b0(
    weights=None
)


# ============================================================
# REPLACE CLASSIFIER
# ============================================================

in_features = (
    model.classifier[1].in_features
)

model.classifier[1] = nn.Linear(
    in_features,
    NUM_CLASSES
)


# ============================================================
# LOAD TRAINED MODEL
# ============================================================

checkpoint = torch.load(
    MODEL_PATH,
    map_location=DEVICE
)


# Handle checkpoint structure
if "model_state_dict" in checkpoint:

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

else:

    model.load_state_dict(
        checkpoint
    )


# ============================================================
# MOVE MODEL TO DEVICE
# ============================================================

model = model.to(DEVICE)

model.eval()


# ============================================================
# IMAGE PREPROCESSING
# ============================================================

TRANSFORM = transforms.Compose([

    transforms.Resize(
        (224, 224)
    ),

    transforms.ToTensor(),

    transforms.Normalize(

        mean=[
            0.485,
            0.456,
            0.406
        ],

        std=[
            0.229,
            0.224,
            0.225
        ]
    )
])


# ============================================================
# CONFIDENCE THRESHOLDS
# ============================================================

HIGH_CONFIDENCE_THRESHOLD = 70.0

MODERATE_CONFIDENCE_THRESHOLD = 40.0


# ============================================================
# CONFIDENCE CLASSIFICATION
# ============================================================

def classify_confidence(
    confidence: float
):

    if confidence >= HIGH_CONFIDENCE_THRESHOLD:

        return {
            "level": "HIGH",
            "status": "HIGH CONFIDENCE"
        }

    elif confidence >= MODERATE_CONFIDENCE_THRESHOLD:

        return {
            "level": "MODERATE",
            "status": "MODERATE CONFIDENCE"
        }

    else:

        return {
            "level": "LOW",
            "status": "LOW CONFIDENCE"
        }


# ============================================================
# PREDICT FISH SPECIES
# ============================================================

def predict_fish(
    image_path: str,
    top_k: int = 5
):

    # --------------------------------------------------------
    # Load image
    # --------------------------------------------------------

    image = Image.open(
        image_path
    ).convert("RGB")


    # --------------------------------------------------------
    # Preprocess image
    # --------------------------------------------------------

    image_tensor = TRANSFORM(
        image
    )

    image_tensor = image_tensor.unsqueeze(
        0
    )

    image_tensor = image_tensor.to(
        DEVICE
    )


    # --------------------------------------------------------
    # Model inference
    # --------------------------------------------------------

    with torch.no_grad():

        outputs = model(
            image_tensor
        )

        probabilities = torch.softmax(
            outputs,
            dim=1
        )

        top_probabilities, top_indices = torch.topk(
            probabilities,
            k=min(top_k, NUM_CLASSES),
            dim=1
        )


    # --------------------------------------------------------
    # Convert results
    # --------------------------------------------------------

    top_probabilities = (
        top_probabilities[0]
        .cpu()
        .numpy()
    )

    top_indices = (
        top_indices[0]
        .cpu()
        .numpy()
    )


    # --------------------------------------------------------
    # Top prediction
    # --------------------------------------------------------

    predicted_index = int(
        top_indices[0]
    )

    predicted_species = CLASS_NAMES[
        predicted_index
    ]

    confidence = float(
        top_probabilities[0] * 100
    )


    # --------------------------------------------------------
    # Confidence level
    # --------------------------------------------------------

    confidence_info = classify_confidence(
        confidence
    )


    # --------------------------------------------------------
    # Top-K predictions
    # --------------------------------------------------------

    top_predictions = []

    for index, probability in zip(
        top_indices,
        top_probabilities
    ):

        top_predictions.append({

            "species": CLASS_NAMES[
                int(index)
            ],

            "confidence": round(
                float(probability * 100),
                2
            )

        })


    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    return {

        "predicted_species":
            predicted_species,

        "confidence":
            round(
                confidence,
                2
            ),

        "confidence_level":
            confidence_info[
                "level"
            ],

        "status":
            confidence_info[
                "status"
            ],

        "top_predictions":
            top_predictions

    }


# ============================================================
# MODEL INFORMATION
# ============================================================

def get_model_info():

    return {

        "model": "EfficientNet-B0",

        "task":
            "Fish Species Classification",

        "classes":
            NUM_CLASSES,

        "image_size":
            "224x224",

        "device":
            str(DEVICE),

        "high_confidence_threshold":
            HIGH_CONFIDENCE_THRESHOLD,

        "moderate_confidence_threshold":
            MODERATE_CONFIDENCE_THRESHOLD

    }