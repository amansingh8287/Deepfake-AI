from __future__ import annotations

import time
from pathlib import Path

from app.config import get_settings
from app.ml.face_detector import FaceDetector
from app.ml.model import BaseClassifier, load_classifier
from app.ml.preprocessing import load_image_array


DISCLAIMER = (
    "DeepGuard AI provides an AI-based prediction and should not be treated "
    "as definitive proof that media is authentic or manipulated."
)


class DeepfakeInferenceService:

    def __init__(self) -> None:
        self.settings = get_settings()
        self.face_detector = FaceDetector()
        self.classifier: BaseClassifier = load_classifier()

    def _label(self, probability: float) -> str:
        """
        Convert fake probability into final prediction.

        >= 0.70  -> DEEPFAKE
        <  0.70  -> REAL
        """
        return "DEEPFAKE" if probability >= 0.75 else "REAL"

    def analyze_image(self, path: Path) -> dict:

        started = time.perf_counter()

        # --------------------------------------------------
        # Load image
        # --------------------------------------------------

        image = load_image_array(
            str(path)
        )

        # --------------------------------------------------
        # Detect faces
        # --------------------------------------------------

        faces = self.face_detector.detect(
            image
        )

        # --------------------------------------------------
        # No face detected
        # --------------------------------------------------

        if not faces:
            return {
                "prediction": "UNKNOWN",
                "confidence": 0.0,
                "processing_time": round(
                    time.perf_counter() - started,
                    2,
                ),
                "faces_detected": 0,
                "explanation": (
                    "No clear face was detected. "
                    "Please upload a clear image containing "
                    "a visible face."
                ),
                "model_name": self.classifier.model_name,
                "mode": self.classifier.mode,
                "disclaimer": DISCLAIMER,
            }

        # --------------------------------------------------
        # Select largest / main face
        #
        # IMPORTANT:
        # We DO NOT average predictions from all detected
        # regions. False face detections can otherwise affect
        # the final result.
        # --------------------------------------------------

        largest_face = max(
            faces,
            key=lambda face: face.w * face.h,
        )

        # --------------------------------------------------
        # Run model on ONLY the largest face
        # --------------------------------------------------

        result = self.classifier.predict_face(
            largest_face.crop
        )

        # Model's probability that the face is fake
        probability = float(
            result.deepfake_probability
        )

        # --------------------------------------------------
        # Confidence
        #
        # This is confidence in the selected label.
        # It is NOT the same thing as the 0.70 decision
        # threshold.
        # --------------------------------------------------

        confidence = (
            probability * 100
            if probability >= 0.5
            else (1.0 - probability) * 100
        )

        # --------------------------------------------------
        # Explanation
        # --------------------------------------------------

        explanation = self._build_image_explanation(
            result.note,
            len(faces),
            probability,
        )

        # --------------------------------------------------
        # Final response
        # --------------------------------------------------

        return {
            "prediction": self._label(
                probability
            ),
            "confidence": round(
                confidence,
                2,
            ),
            "processing_time": round(
                time.perf_counter() - started,
                2,
            ),
            "faces_detected": len(faces),
            "explanation": explanation,
            "model_name": result.model_name,
            "mode": result.mode,
            "disclaimer": DISCLAIMER,
        }

    def _build_image_explanation(
        self,
        note: str,
        faces_detected: int,
        probability: float,
    ) -> str:

        likelihood = (
            "strong"
            if abs(probability - 0.5) > 0.25
            else "moderate"
        )

        focus = (
            f"{faces_detected} face region(s) were detected; "
            "the largest face region was analyzed."
        )

        return (
            f"{focus} "
            f"{note} "
            f"The model observed "
            f"{likelihood} manipulation signals."
        )


inference_service = DeepfakeInferenceService()