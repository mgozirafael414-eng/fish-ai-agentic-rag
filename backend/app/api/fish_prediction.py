# ============================================================
# FISHAI — FISH IMAGE PREDICTION API
# ============================================================

from pathlib import Path

from fastapi import APIRouter, File, UploadFile, HTTPException

from app.fish_model_service import predict_fish


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

        with open(
            image_path,
            "wb"
        ) as image_file:

            image_file.write(
                contents
            )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to save image: {str(error)}"
        )


    # --------------------------------------------------------
    # Run model prediction
    # --------------------------------------------------------

    try:

        result = predict_fish(
            str(image_path),
            top_k=5
        )

    except Exception as error:

        # Remove failed image
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