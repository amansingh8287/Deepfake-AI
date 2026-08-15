from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class DetectedFace:
    x: int
    y: int
    w: int
    h: int
    crop: np.ndarray


class FaceDetector:

    def __init__(self) -> None:

        cascade_path = (
            cv2.data.haarcascades
            + "haarcascade_frontalface_default.xml"
        )

        self.haar = cv2.CascadeClassifier(
            cascade_path
        )

        if self.haar.empty():
            raise RuntimeError(
                "Could not load OpenCV Haar Cascade."
            )

    def detect(
        self,
        image: np.ndarray
    ) -> list[DetectedFace]:

        # Image is RGB
        gray = cv2.cvtColor(
            image,
            cv2.COLOR_RGB2GRAY
        )

        faces = self.haar.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=6,
            minSize=(65, 65),
        )

        detected = []

        image_h, image_w = image.shape[:2]

        for x, y, w, h in faces:

            # SAME padding used during training
            pad_x = int(w * 0.20)
            pad_y = int(h * 0.20)

            x1 = max(
                0,
                x - pad_x
            )

            y1 = max(
                0,
                y - pad_y
            )

            x2 = min(
                image_w,
                x + w + pad_x
            )

            y2 = min(
                image_h,
                y + h + pad_y
            )

            crop = image[
                y1:y2,
                x1:x2
            ]

            if crop.size == 0:
                continue

            detected.append(
                DetectedFace(
                    x=int(x1),
                    y=int(y1),
                    w=int(x2 - x1),
                    h=int(y2 - y1),
                    crop=crop,
                )
            )

        # Largest face first
        detected.sort(
            key=lambda f: f.w * f.h,
            reverse=True
        )

        return detected