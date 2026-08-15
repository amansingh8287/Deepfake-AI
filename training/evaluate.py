from __future__ import annotations

from pathlib import Path

import torch
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from torch.utils.data import DataLoader
from torchvision import models

from config import TrainingConfig
from dataset import DeepfakeDataset
from train import collect_items


def main() -> None:
    config = TrainingConfig()
    items = collect_items(config.dataset_root)
    test_loader = DataLoader(DeepfakeDataset(items, config.image_size), batch_size=config.batch_size)

    model = models.efficientnet_b0(weights=None)
    model.classifier[1] = torch.nn.Linear(model.classifier[1].in_features, 1)
    checkpoint = torch.load(config.output_model_path, map_location="cpu")
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    y_true: list[int] = []
    y_prob: list[float] = []

    with torch.no_grad():
        for images, labels in test_loader:
            logits = model(images)
            probs = torch.sigmoid(logits).squeeze(1)
            y_true.extend(labels.tolist())
            y_prob.extend(probs.tolist())

    y_pred = [1 if item >= 0.5 else 0 for item in y_prob]
    print("Accuracy:", accuracy_score(y_true, y_pred))
    print("Precision:", precision_score(y_true, y_pred, zero_division=0))
    print("Recall:", recall_score(y_true, y_pred, zero_division=0))
    print("F1:", f1_score(y_true, y_pred, zero_division=0))
    print("ROC-AUC:", roc_auc_score(y_true, y_prob))
    print("Confusion Matrix:\n", confusion_matrix(y_true, y_pred))


if __name__ == "__main__":
    main()

