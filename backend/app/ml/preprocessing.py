from __future__ import annotations

import cv2
import numpy as np
from PIL import Image


def load_image_array(path: str) -> np.ndarray:
    image = Image.open(path).convert("RGB")
    return np.array(image)


def bgr_to_rgb(frame: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


def normalize_face(face: np.ndarray, size: int = 224) -> np.ndarray:
    resized = cv2.resize(face, (size, size), interpolation=cv2.INTER_AREA)
    return resized.astype(np.float32) / 255.0


def laplacian_variance(image: np.ndarray) -> float:
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def edge_density(image: np.ndarray) -> float:
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 80, 180)
    return float(np.count_nonzero(edges) / edges.size)


def jpeg_artifact_score(image: np.ndarray) -> float:
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    small = cv2.resize(gray, (64, 64), interpolation=cv2.INTER_AREA)
    block_diff = np.abs(np.diff(small, axis=0)).mean() + np.abs(np.diff(small, axis=1)).mean()
    return float(block_diff / 255.0)


def frequency_energy_ratio(image: np.ndarray) -> float:
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY).astype(np.float32)
    fft = np.fft.fftshift(np.fft.fft2(gray))
    magnitude = np.log1p(np.abs(fft))
    center = magnitude[16:-16, 16:-16] if min(magnitude.shape) > 32 else magnitude
    high = magnitude.mean()
    low = center.mean() if center.size else high
    return float(max(high - low, 0.0) / (high + 1e-6))

