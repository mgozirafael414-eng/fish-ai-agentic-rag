# ==========================================
# FISH IDENTIFICATION AGENT
# ==========================================

from typing import Optional


async def fish_identification_agent(
    image_path: Optional[str] = None,
    user_message: str = "",
    conversation: list = None,
) -> str:
    """
    Fish Identification Agent

    Responsible for identifying fish species from
    an uploaded image.

    The computer vision model will be connected
    in a later step.
    """

    if conversation is None:
        conversation = []

    # ------------------------------------------
    # CHECK IMAGE
    # ------------------------------------------

    if not image_path:
        return (
            "🐟 **Fish Identification Agent**\n\n"
            "Please upload an image of the fish you want me "
            "to identify.\n\n"
            "I will analyze the image and provide:\n"
            "- Possible fish species\n"
            "- Scientific name\n"
            "- Confidence score\n"
            "- Identification features\n"
            "- Habitat information\n"
            "- Identification uncertainty"
        )

    # ------------------------------------------
    # TEMPORARY RESPONSE
    # ------------------------------------------
    # Computer vision model will be connected
    # in the next step.

    return (
        "🐟 **Fish Identification Agent**\n\n"
        f"Image received successfully.\n\n"
        f"Image path: `{image_path}`\n\n"
        "The image analysis model is not connected yet. "
        "The next step will connect a computer vision model "
        "for actual fish species identification."
    )

