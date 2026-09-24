# ============================================================
# FISHAI — FISH IMAGE PREDICTION API
# ============================================================

import logging
from pathlib import Path

from fastapi import APIRouter, File, UploadFile, HTTPException

from app.fish_model_service import predict_fish
from app.fish_image_validator import NOT_FISH_MESSAGE, validate_fish_image

logger = logging.getLogger(__name__)


# ============================================================
# CREATE ROUTER
# ============================================================

router = APIRouter(
    prefix="/api/fish",
    tags=["Fish Identification"]
)


# ============================================================
# PREDICT FISH SPECIES
# ============================================================

@router.post("/predict")
async def predict_fish_image(
    file: UploadFile = File(...)
):

    if not file or not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No image file uploaded."
        )

    # --------------------------------------------------------
    # Validate file type
    # --------------------------------------------------------

    allowed_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".bmp"
    }

    filename = file.filename or ""
    extension = Path(filename).suffix.lower()

    logger.info("Received upload filename=%s content_type=%s size_hint=%s", filename, file.content_type, getattr(file, 'size', 'unknown'))

    if extension not in allowed_extensions:

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid image format. "
                "Allowed formats: JPG, JPEG, PNG, WEBP, BMP."
            )
        )


    # --------------------------------------------------------
    # Create temporary upload directory
    # --------------------------------------------------------

    upload_dir = Path(
        "uploads/fish_images"
    )

    upload_dir.mkdir(
        parents=True,
        exist_ok=True
    )


    # --------------------------------------------------------
    # Create unique filename
    # --------------------------------------------------------

    import uuid

    unique_filename = (
        f"{uuid.uuid4()}{extension}"
    )

    image_path = (
        upload_dir /
        unique_filename
    )


    # --------------------------------------------------------
    # Save uploaded image
    # --------------------------------------------------------

    try:

        contents = await file.read()

        if not contents:
            raise HTTPException(
                status_code=400,
                detail="Uploaded image is empty."
            )

        with open(
            image_path,
            "wb"
        ) as image_file:

            image_file.write(
                contents
            )

    except HTTPException:
        raise

    except Exception as error:

        logger.exception("Failed to save uploaded image: %s", filename)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save image: {str(error)}"
        )


    # --------------------------------------------------------
    # Run model prediction
    # --------------------------------------------------------

    try:

        validation = validate_fish_image(str(image_path))
        logger.info(
            "Fish image validation decision: filename=%s is_fish=%s reason=%s",
            filename,
            validation["is_fish"],
            validation["reason"],
        )

        if not validation["is_fish"]:
            logger.info(
                "[Fish Prediction] classifier_called=false filename=%s reason=%s",
                filename,
                validation["reason"],
            )
            image_path.unlink(missing_ok=True)
            return {
                "success": False,
                "status": "NOT_FISH",
                "message": NOT_FISH_MESSAGE,
            }

        logger.info(
            "[Fish Prediction] classifier_called=true filename=%s",
            filename,
        )
        result = predict_fish(
            str(image_path),
            top_k=5
        )

    except ValueError as error:
        logger.info("Rejecting invalid image upload: filename=%s reason=%s", filename, error)
        image_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=400,
            detail=f"Invalid image: {str(error)}"
        )

    except Exception as error:

        logger.exception("Fish prediction failed for upload: %s", filename)

        if image_path.exists():
            image_path.unlink()

        raise HTTPException(
            status_code=500,
            detail=f"Fish model prediction failed: {str(error)}"
        )


    # --------------------------------------------------------
    # Return prediction
    # --------------------------------------------------------

    return {

        "success": True,

        "message":
            "Fish species identified successfully.",

        "filename":
            unique_filename,

        "predicted_species":
            result["predicted_species"],

        "confidence":
            result["confidence"],

        "confidence_level":
            result["confidence_level"],

        "status":
            result["status"],

        "top_predictions":
            result["top_predictions"]

    }