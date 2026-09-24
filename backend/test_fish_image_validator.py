import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from fastapi import UploadFile
from io import BytesIO

from PIL import Image

from app.api import fish_prediction
from app.fish_image_validator import validate_fish_image


class FishImageValidatorTests(unittest.TestCase):
    def test_invalid_image_is_rejected_before_classification(self):
        with TemporaryDirectory() as directory:
            invalid_path = Path(directory) / "invalid.png"
            invalid_path.write_bytes(b"not an image")
            with self.assertRaises(ValueError):
                validate_fish_image(str(invalid_path))

    def test_validator_returns_a_machine_readable_decision(self):
        image_path = Path(self.id()).with_suffix(".png")
        Image.new("RGB", (224, 224), color=(128, 128, 128)).save(image_path)

        try:
            result = validate_fish_image(str(image_path))
        finally:
            image_path.unlink(missing_ok=True)

        self.assertIsInstance(result["is_fish"], bool)
        self.assertIn(result["reason"], {"fish_label_detected", "no_fish_label_detected"})

    def test_non_fish_decision_skips_species_classifier(self):
        upload = UploadFile(filename="person.png", file=BytesIO(b"image"))

        with patch.object(
            fish_prediction,
            "validate_fish_image",
            return_value={"is_fish": False, "reason": "no_fish_label_detected"},
        ), patch.object(fish_prediction, "predict_fish") as classifier:
            result = __import__("asyncio").run(fish_prediction.predict_fish_image(upload))

        self.assertFalse(result["success"])
        self.assertEqual(result["status"], "NOT_FISH")
        classifier.assert_not_called()

    def test_unrelated_object_decision_skips_species_classifier(self):
        upload = UploadFile(filename="car.png", file=BytesIO(b"image"))

        with patch.object(
            fish_prediction,
            "validate_fish_image",
            return_value={"is_fish": False, "reason": "no_fish_label_detected"},
        ), patch.object(fish_prediction, "predict_fish") as classifier:
            result = __import__("asyncio").run(fish_prediction.predict_fish_image(upload))

        self.assertFalse(result["success"])
        self.assertEqual(result["status"], "NOT_FISH")
        classifier.assert_not_called()

    def test_fish_decision_preserves_existing_prediction_payload(self):
        upload = UploadFile(filename="fish.png", file=BytesIO(b"image"))
        prediction = {
            "predicted_species": "example_fish",
            "confidence": 88.0,
            "confidence_level": "HIGH",
            "status": "HIGH CONFIDENCE",
            "top_predictions": [{"species": "example_fish", "confidence": 88.0}],
        }

        with patch.object(
            fish_prediction,
            "validate_fish_image",
            return_value={"is_fish": True, "reason": "fish_label_detected"},
        ), patch.object(fish_prediction, "predict_fish", return_value=prediction):
            result = __import__("asyncio").run(fish_prediction.predict_fish_image(upload))

        self.assertTrue(result["success"])
        self.assertEqual(result["predicted_species"], "example_fish")
        self.assertEqual(result["top_predictions"], prediction["top_predictions"])

    def test_empty_image_returns_bad_request(self):
        upload = UploadFile(filename="empty.png", file=BytesIO(b""))

        with self.assertRaises(fish_prediction.HTTPException) as error:
            __import__("asyncio").run(fish_prediction.predict_fish_image(upload))

        self.assertEqual(error.exception.status_code, 400)