# ==========================================
# FISH IDENTIFICATION AGENT
# ==========================================

import logging
from typing import Optional

from app.fish_model_service import predict_fish

logger = logging.getLogger(__name__)


async def fish_identification_agent(
    image_path: Optional[str] = None,
    user_message: str = "",
    conversation: list = None,
) -> str:
    """
    Fish Identification Agent

    Uses the project's existing EfficientNet-B0 model to
    classify the uploaded fish image and return a readable result.
    """

    if conversation is None:
        conversation = []

    if not image_path:
        return (
            "🐟 **Fish Identification Agent**\n\n"
            "Please upload an image of the fish you want me "
            "to identify.\n\n"
            "I will analyze the image and provide:\n"
            "- Possible fish species\n"
            "- Confidence score\n"
            "- Confidence level\n"
            "- Top predictions"
        )

    try:
        result = predict_fish(image_path, top_k=5)

        top_predictions = result.get("top_predictions", [])
        prediction_lines = [
            f"{index + 1}. **{item['species']}** — {float(item['confidence']):.2f}%"
            for index, item in enumerate(top_predictions[:5])
        ]

        summary = (
            "🐟 **Fish Identification Result**\n\n"
            f"**Predicted species:** {result['predicted_species']}\n\n"
            f"**Confidence:** {float(result['confidence']):.2f}%\n\n"
            f"**Confidence level:** {result['confidence_level']}\n\n"
            f"**Status:** {result['status']}\n\n"
            "### Top predictions\n\n"
            + "\n".join(prediction_lines)
        )

        logger.info(
            "Fish identification complete: image=%s predicted_species=%s confidence=%.2f",
            image_path,
            result["predicted_species"],
            float(result["confidence"]),
        )

        return summary

    except FileNotFoundError as error:
        logger.exception("Fish identification failed: image not found")
        return (
            "🐟 **Fish Identification Agent**\n\n"
            "The uploaded image could not be found or opened. "
            "Please upload a valid fish image again."
        )

    except ValueError as error:
        logger.exception("Fish identification failed: invalid image")
        return (
            "🐟 **Fish Identification Agent**\n\n"
            f"The uploaded image could not be processed: {str(error)}"
        )

    except Exception as error:
        logger.exception("Fish identification failed unexpectedly")
        return (
            "🐟 **Fish Identification Agent**\n\n"
            "The fish classification model could not complete the prediction. "
            "Please try another image or check the backend logs."
        )

