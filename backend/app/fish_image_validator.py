import logging
from functools import lru_cache
from pathlib import Path

import torch
from PIL import Image
from torchvision.models import MobileNet_V3_Small_Weights, mobilenet_v3_small

logger = logging.getLogger(__name__)

NOT_FISH_MESSAGE = (
    "The uploaded image does not appear to contain a fish. "
    "Please upload a clear image of a fish."
)

# ImageNet labels that represent fish or fish-like aquatic animals. This model
# is only a suitability gate; species identification remains with EfficientNet.
FISH_LABELS = {
    "tench",
    "goldfish",
    "great white shark",
    "tiger shark",
    "hammerhead",
    "electric ray",
    "stingray",
    "gar",
    "lionfish",
    "puffer",
    "eel",
    "rock beauty",
    "anemone fish",
    "sturgeon",
    "goby",
    "scorpion fish",
}

FISH_SCORE_THRESHOLD = 0.10
TOP_LABEL_COUNT = 5


@lru_cache(maxsize=1)
def _load_validator():
    weights = MobileNet_V3_Small_Weights.DEFAULT
    validator = mobilenet_v3_small(weights=weights)
    validator.eval()
    return validator, weights.transforms(), weights.meta["categories"]


def validate_fish_image(image_path: str) -> dict:
    """Check whether an image is suitable for the fish classifier."""
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    try:
        with Image.open(path) as image:
            image.verify()

        with Image.open(path) as image:
            image_tensor = _load_validator()[1](image.convert("RGB")).unsqueeze(0)
    except Exception as exc:
        raise ValueError(f"Invalid image: {exc}") from exc

    validator, _, categories = _load_validator()
    with torch.no_grad():
        probabilities = validator(image_tensor).softmax(dim=1)[0]

    top_probabilities, top_indices = probabilities.topk(TOP_LABEL_COUNT)
    top_labels = [categories[int(index)] for index in top_indices]
    fish_matches = [
        (label, float(probability))
        for label, probability in zip(top_labels, top_probabilities)
        if label in FISH_LABELS and float(probability) >= FISH_SCORE_THRESHOLD
    ]
    is_fish = bool(fish_matches)

    logger.info(
        "Image validation complete: image=%s is_fish=%s top_labels=%s",
        path.name,
        is_fish,
        top_labels,
    )

    return {
        "is_fish": is_fish,
        "reason": "fish_label_detected" if is_fish else "no_fish_label_detected",
        "top_labels": top_labels,
    }