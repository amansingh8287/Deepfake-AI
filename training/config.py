from pathlib import Path

from pydantic import BaseModel


class TrainingConfig(BaseModel):
    dataset_root: Path = Path("data/faceforensics")
    train_split: float = 0.7
    val_split: float = 0.15
    test_split: float = 0.15
    batch_size: int = 16
    epochs: int = 10
    learning_rate: float = 1e-4
    num_workers: int = 2
    image_size: int = 224
    output_model_path: Path = Path("../models/deepguard_efficientnet.pt")

