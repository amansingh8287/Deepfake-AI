from __future__ import annotations

import statistics
import time
from pathlib import Path

import cv2

from app.config import get_settings
from app.ml.face_detector import FaceDetector
from app.ml.model import BaseClassifier, load_classifier
from app.schemas import SuspiciousFrame


DISCLAIMER = (
    "DeepGuard AI provides an AI-based prediction and should not be treated "
    "as definitive proof that media is authentic or manipulated."
)


class VideoAnalyzer:

    # Final video decision threshold.
    # Keep this consistent with image detection.
    FINAL_DEEPFAKE_THRESHOLD = 0.70

    # A video should not be called DEEPFAKE just because
    # one sampled frame is suspicious.
    MIN_SUSPICIOUS_RATIO = 0.40

    def __init__(self) -> None:
        self.settings = get_settings()
        self.face_detector = FaceDetector()
        self.classifier: BaseClassifier = load_classifier()

    def analyze(self, path: Path) -> dict:

        started = time.perf_counter()

        capture = cv2.VideoCapture(str(path))

        if not capture.isOpened():
            raise ValueError(
                "Unable to open video for analysis."
            )

        source_fps = (
            capture.get(cv2.CAP_PROP_FPS)
            or 25.0
        )

        frame_interval = max(
            int(
                round(
                    source_fps
                    / max(
                        self.settings.video_sample_fps,
                        0.1,
                    )
                )
            ),
            1,
        )

        frame_index = 0
        analyzed = 0
        face_count = 0

        probabilities: list[float] = []

        suspicious: list[SuspiciousFrame] = []

        last_model_name = "unknown"
        last_mode = "baseline"

        try:

            while analyzed < self.settings.max_video_frames:

                ok, frame = capture.read()

                if not ok:
                    break

                if frame_index % frame_interval != 0:
                    frame_index += 1
                    continue

                # --------------------------------------------------
                # Convert frame to RGB
                # --------------------------------------------------

                rgb = cv2.cvtColor(
                    frame,
                    cv2.COLOR_BGR2RGB,
                )

                # --------------------------------------------------
                # Detect faces
                # --------------------------------------------------

                faces = self.face_detector.detect(
                    rgb
                )

                face_count += len(faces)

                # --------------------------------------------------
                # Analyze ONLY the largest face
                # --------------------------------------------------

                if faces:

                    largest_face = max(
                        faces,
                        key=lambda item: item.w * item.h,
                    )

                    region = largest_face.crop

                else:
                    # No face found in this sampled frame.
                    # Do not classify the entire frame as a face.
                    frame_index += 1
                    continue

                # --------------------------------------------------
                # Model prediction
                # --------------------------------------------------

                prediction = self.classifier.predict_face(
                    region
                )

                probability = float(
                    prediction.deepfake_probability
                )

                last_model_name = (
                    prediction.model_name
                )

                last_mode = (
                    prediction.mode
                )

                probabilities.append(
                    probability
                )

                timestamp = (
                    frame_index
                    / max(source_fps, 1.0)
                )

                # --------------------------------------------------
                # Suspicious frame
                # --------------------------------------------------

                if (
                    probability
                    >= self.settings.frame_score_threshold
                ):

                    suspicious.append(
                        SuspiciousFrame(
                            index=frame_index,
                            timestamp=round(
                                timestamp,
                                2,
                            ),
                            confidence=round(
                                probability * 100,
                                2,
                            ),
                            note=(
                                "Sampled frame showed "
                                "elevated manipulation indicators."
                            ),
                        )
                    )

                analyzed += 1
                frame_index += 1

        finally:

            capture.release()

        # ----------------------------------------------------------
        # No usable frames
        # ----------------------------------------------------------

        if not probabilities:

            raise ValueError(
                "No usable face frames could be sampled "
                "from the uploaded video."
            )

        # ----------------------------------------------------------
        # Aggregate frame probabilities
        #
        # We still calculate the mean because the video needs
        # an overall score, but the final verdict ALSO considers
        # how many frames were suspicious.
        # ----------------------------------------------------------

        overall_probability = float(
            statistics.mean(
                probabilities
            )
        )

        suspicious_count = len(
            suspicious
        )

        suspicious_ratio = (
            suspicious_count / analyzed
            if analyzed > 0
            else 0.0
        )

        # ----------------------------------------------------------
        # Final video decision
        #
        # Requirements:
        #
        # 1. Overall score >= 0.70
        # 2. At least 40% of analyzed frames suspicious
        #
        # This prevents one suspicious frame from making
        # the whole video DEEPFAKE.
        # ----------------------------------------------------------

        is_deepfake = (
            overall_probability
            >= self.FINAL_DEEPFAKE_THRESHOLD
            and suspicious_ratio
            >= self.MIN_SUSPICIOUS_RATIO
        )

        # ----------------------------------------------------------
        # Confidence
        # ----------------------------------------------------------

        if is_deepfake:

            confidence = (
                overall_probability * 100
            )

        else:

            confidence = (
                (1.0 - overall_probability)
                * 100
            )

        # ----------------------------------------------------------
        # Explanation
        # ----------------------------------------------------------

        explanation = self._build_explanation(
            overall_probability,
            analyzed,
            suspicious,
            suspicious_ratio,
        )

        # ----------------------------------------------------------
        # Final response
        # ----------------------------------------------------------

        return {

            "prediction": (
                "DEEPFAKE"
                if is_deepfake
                else "REAL"
            ),

            "confidence": round(
                confidence,
                2,
            ),

            "processing_time": round(
                time.perf_counter()
                - started,
                2,
            ),

            "faces_detected": face_count,

            "frames_analyzed": analyzed,

            "suspicious_frames": suspicious,

            "explanation": explanation,

            "model_name": last_model_name,

            "mode": last_mode,

            "disclaimer": DISCLAIMER,
        }

    def _build_explanation(
        self,
        probability: float,
        frames_analyzed: int,
        suspicious: list[SuspiciousFrame],
        suspicious_ratio: float,
    ) -> str:

        suspicious_count = len(
            suspicious
        )

        if (
            probability
            >= self.FINAL_DEEPFAKE_THRESHOLD
            and suspicious_ratio
            >= self.MIN_SUSPICIOUS_RATIO
        ):

            verdict = (
                "strong manipulation signals"
            )

        elif suspicious_count > 0:

            verdict = (
                "limited or inconsistent "
                "manipulation signals"
            )

        else:

            verdict = (
                "limited manipulation signals"
            )

        return (
            f"{frames_analyzed} sampled frame(s) "
            "were analyzed using configurable "
            "frame sampling. "

            f"{suspicious_count} frame(s) crossed "
            "the suspicious-frame threshold. "

            f"{verdict} were observed."
        )


video_analyzer = VideoAnalyzer()