from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from app.config import get_settings

try:
    import torch
    from torchvision import models, transforms
except Exception:
    torch = None
    models = None
    transforms = None


@dataclass
class PredictionResult:
    deepfake_probability: float
    note: str
    mode: str
    model_name: str


class BaseClassifier:
    def predict_face(
        self,
        face: np.ndarray
    ) -> PredictionResult:
        raise NotImplementedError


class TorchDeepfakeClassifier(BaseClassifier):

    def __init__(
        self,
        model_path: Path,
        model_name: str
    ) -> None:

        if (
            torch is None
            or models is None
            or transforms is None
        ):
            raise RuntimeError(
                "PyTorch dependencies are not available."
            )

        self.model_path = model_path
        self.model_name = model_name

        self.device = torch.device(
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        print(
            f"[DeepGuard] Loading model: "
            f"{model_path}"
        )

        print(
            f"[DeepGuard] Device: "
            f"{self.device}"
        )

        # ----------------------------------------------------
        # Same preprocessing used during training
        # ----------------------------------------------------

        self.transform = transforms.Compose([
            transforms.ToPILImage(),

            transforms.Resize(
                (224, 224)
            ),

            transforms.ToTensor(),

            transforms.Normalize(
                mean=[
                    0.485,
                    0.456,
                    0.406
                ],
                std=[
                    0.229,
                    0.224,
                    0.225
                ],
            ),
        ])

        # ----------------------------------------------------
        # Same architecture used during training
        # ----------------------------------------------------

        self.model = models.efficientnet_b0(
            weights=None
        )

        in_features = (
            self.model
            .classifier[1]
            .in_features
        )

        # IMPORTANT:
        # Training used 2 output classes.
        self.model.classifier[1] = (
            torch.nn.Linear(
                in_features,
                2
            )
        )

        # ----------------------------------------------------
        # Load checkpoint
        # ----------------------------------------------------

        checkpoint = torch.load(
            model_path,
            map_location=self.device
        )

        if (
            isinstance(checkpoint, dict)
            and "model_state_dict"
            in checkpoint
        ):

            state_dict = (
                checkpoint[
                    "model_state_dict"
                ]
            )

            checkpoint_class_to_idx = (
                checkpoint.get(
                    "class_to_idx"
                )
            )

            if checkpoint_class_to_idx:
                self.class_to_idx = (
                    checkpoint_class_to_idx
                )
            else:
                self.class_to_idx = {
                    "fake": 0,
                    "real": 1,
                }

        else:

            state_dict = checkpoint

            self.class_to_idx = {
                "fake": 0,
                "real": 1,
            }

        print(
            f"[DeepGuard] class_to_idx: "
            f"{self.class_to_idx}"
        )

        # ----------------------------------------------------
        # Find FAKE class index
        # ----------------------------------------------------

        if "fake" not in self.class_to_idx:
            raise RuntimeError(
                "Checkpoint does not contain "
                "'fake' class."
            )

        self.fake_index = int(
            self.class_to_idx["fake"]
        )

        self.real_index = int(
            self.class_to_idx["real"]
        )

        # ----------------------------------------------------
        # Load weights
        # ----------------------------------------------------

        self.model.load_state_dict(
            state_dict
        )

        self.model.to(
            self.device
        )

        self.model.eval()

        print(
            "[DeepGuard] Trained model "
            "loaded successfully."
        )

    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    def predict_face(
        self,
        face: np.ndarray
    ) -> PredictionResult:

        tensor = (
            self.transform(face)
            .unsqueeze(0)
            .to(self.device)
        )

        with torch.no_grad():

            logits = self.model(
                tensor
            )

            probabilities = torch.softmax(
                logits,
                dim=1
            )

            fake_probability = (
                probabilities[
                    0,
                    self.fake_index
                ]
                .item()
            )

        fake_probability = float(
            np.clip(
                fake_probability,
                0.0,
                1.0
            )
        )

        return PredictionResult(
            deepfake_probability=fake_probability,
            note=(
                "Trained EfficientNet-B0 "
                "checkpoint inference completed "
                "successfully."
            ),
            mode="trained",
            model_name=self.model_name,
        )


def load_classifier() -> BaseClassifier:

    settings = get_settings()

    model_path = settings.model_path

    print(
        f"[DeepGuard] Configured model path: "
        f"{model_path}"
    )

    if not model_path.exists():

        raise FileNotFoundError(
            "Trained DeepGuard model was not found:\n"
            f"{model_path}\n\n"
            "Check model_path in your .env/config."
        )

    return TorchDeepfakeClassifier(
        model_path,
        settings.model_name
    )