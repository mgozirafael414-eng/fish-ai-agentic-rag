# ==========================================
# FISHAI COMPUTER VISION SERVICE
# ==========================================

from pathlib import Path
from typing import Dict, Any


# ==========================================
# MODEL CONFIGURATION
# ==========================================

MODEL_PATH = Path(
    "models/fish_classifier.pt"
)


# ==========================================
# CHECK MODEL
# ==========================================

def model_available() -> bool:
    """
    Check whether the trained fish
    classification model exists.
    """

    return MODEL_PATH.exists()


# ==========================================
# LOAD MODEL
# ==========================================

def load_model():
    """
    Load the computer vision model.

    The actual YOLO model will be connected
    once the trained model is available.
    """

    if not model_available():
        return None

    try:

        from ultralytics import YOLO

        model = YOLO(
            str(MODEL_PATH)
        )

        return model

    except Exception as error:

        print(
            "MODEL LOAD ERROR:",
            error
        )

        return None


# ==========================================
# PREDICT FISH SPECIES
# ==========================================

def predict_fish(
    image_path: str
) -> Dict[str, Any]:
    """
    Predict fish species from an image.
    """

    image = Path(image_path)

    # ------------------------------------------
    # CHECK IMAGE
    # ------------------------------------------

    if not image.exists():

        return {
            "success": False,
            "error": "Image file not found.",
        }


    # ------------------------------------------
    # CHECK MODEL
    # ------------------------------------------

    if not model_available():

        return {
            "success": False,
            "error": (
                "Fish classification model "
                "is not available yet."
            ),
        }


    # ------------------------------------------
    # LOAD MODEL
    # ------------------------------------------

    model = load_model()

    if model is None:

        return {
            "success": False,
            "error": (
                "Unable to load the "
                "fish classification model."
            ),
        }


    # ------------------------------------------
    # RUN PREDICTION
    # ------------------------------------------

    try:

        results = model.predict(
            source=str(image),
            verbose=False
        )

        if not results:

            return {
                "success": False,
                "error": "No prediction result."
            }


        result = results[0]


        # --------------------------------------
        # CLASSIFICATION RESULT
        # --------------------------------------

        if hasattr(result, "probs") and result.probs:

            top_class = int(
                result.probs.top1
            )

            confidence = float(
                result.probs.top1conf
            )

            class_name = result.names[
                top_class
            ]


            return {

                "success": True,

                "species": class_name,

                "confidence": round(
                    confidence * 100,
                    2
                ),

                "class_id": top_class,

                "model": "YOLO"
            }


        # --------------------------------------
        # DETECTION RESULT
        # --------------------------------------

        if hasattr(result, "boxes") and result.boxes:

            boxes = result.boxes

            if len(boxes) == 0:

                return {
                    "success": False,
                    "error": (
                        "No fish detected "
                        "in the image."
                    )
                }


            best_box = boxes[
                boxes.conf.argmax()
            ]

            class_id = int(
                best_box.cls.item()
            )

            confidence = float(
                best_box.conf.item()
            )

            class_name = result.names[
                class_id
            ]


            return {

                "success": True,

                "species": class_name,

                "confidence": round(
                    confidence * 100,
                    2
                ),

                "class_id": class_id,

                "model": "YOLO"
            }


        return {
            "success": False,
            "error": (
                "The model returned "
                "no usable prediction."
            )
        }


    except Exception as error:

        print(
            "PREDICTION ERROR:",
            error
        )

        return {
            "success": False,
            "error": str(error)
        }