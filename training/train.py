from pathlib import Path
import json
import time

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)


# ============================================================
# DeepGuard - EfficientNet-B0 Training
# ============================================================

PROJECT_ROOT = Path(r"D:\deep fake model")

DATA_ROOT = PROJECT_ROOT / "dataset" / "faces"
MODEL_ROOT = PROJECT_ROOT / "models"
MODEL_ROOT.mkdir(parents=True, exist_ok=True)

BEST_MODEL = MODEL_ROOT / "deepguard_efficientnet_b0.pth"
METRICS_FILE = MODEL_ROOT / "training_metrics.json"

IMAGE_SIZE = 224
BATCH_SIZE = 16
EPOCHS = 12

LEARNING_RATE = 1e-4
WEIGHT_DECAY = 1e-4

NUM_WORKERS = 0
PATIENCE = 3

SEED = 42


# ============================================================
# Reproducibility
# ============================================================

torch.manual_seed(SEED)

if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)


# ============================================================
# Device
# ============================================================

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("=" * 70)
print("DeepGuard - EfficientNet-B0 Training")
print("=" * 70)

print(f"\nDevice: {device}")

if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(
        f"VRAM: "
        f"{torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB"
    )

print(f"PyTorch: {torch.__version__}")


# ============================================================
# Transforms
# ============================================================

train_transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),

    transforms.RandomHorizontalFlip(
        p=0.5
    ),

    transforms.RandomRotation(
        degrees=8
    ),

    transforms.ColorJitter(
        brightness=0.15,
        contrast=0.15,
        saturation=0.10,
    ),

    transforms.ToTensor(),

    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    ),
])


eval_transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),

    transforms.ToTensor(),

    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    ),
])


# ============================================================
# Dataset
# ============================================================

train_dir = DATA_ROOT / "train"
val_dir = DATA_ROOT / "val"
test_dir = DATA_ROOT / "test"

for folder in [
    train_dir,
    val_dir,
    test_dir,
]:
    if not folder.exists():
        raise FileNotFoundError(
            f"Dataset folder not found:\n{folder}"
        )


train_dataset = datasets.ImageFolder(
    train_dir,
    transform=train_transform,
)

val_dataset = datasets.ImageFolder(
    val_dir,
    transform=eval_transform,
)

test_dataset = datasets.ImageFolder(
    test_dir,
    transform=eval_transform,
)


print("\nClass mapping:")
print(train_dataset.class_to_idx)

print("\nDataset sizes:")
print(f"Train: {len(train_dataset)}")
print(f"Val  : {len(val_dataset)}")
print(f"Test : {len(test_dataset)}")


# ============================================================
# DataLoaders
# ============================================================

train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True,
    num_workers=NUM_WORKERS,
    pin_memory=torch.cuda.is_available(),
)

val_loader = DataLoader(
    val_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=NUM_WORKERS,
    pin_memory=torch.cuda.is_available(),
)

test_loader = DataLoader(
    test_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=NUM_WORKERS,
    pin_memory=torch.cuda.is_available(),
)


# ============================================================
# Model
# ============================================================

print("\nLoading EfficientNet-B0...")

weights = models.EfficientNet_B0_Weights.DEFAULT

model = models.efficientnet_b0(
    weights=weights
)

# Replace classifier
in_features = model.classifier[1].in_features

model.classifier[1] = nn.Linear(
    in_features,
    2,
)

model = model.to(device)


# ============================================================
# Loss / Optimizer
# ============================================================

criterion = nn.CrossEntropyLoss()

optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=LEARNING_RATE,
    weight_decay=WEIGHT_DECAY,
)

scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
    optimizer,
    mode="min",
    factor=0.5,
    patience=1,
)


# ============================================================
# Mixed Precision
# ============================================================

use_amp = device.type == "cuda"

scaler = torch.amp.GradScaler(
    "cuda",
    enabled=use_amp,
)


# ============================================================
# Training
# ============================================================

def train_one_epoch():

    model.train()

    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels in train_loader:

        images = images.to(
            device,
            non_blocking=True
        )

        labels = labels.to(
            device,
            non_blocking=True
        )

        optimizer.zero_grad(
            set_to_none=True
        )

        with torch.amp.autocast(
            "cuda",
            enabled=use_amp
        ):

            outputs = model(images)

            loss = criterion(
                outputs,
                labels
            )

        scaler.scale(loss).backward()

        scaler.step(optimizer)

        scaler.update()

        running_loss += (
            loss.item() * images.size(0)
        )

        predictions = outputs.argmax(
            dim=1
        )

        correct += (
            predictions == labels
        ).sum().item()

        total += labels.size(0)

    epoch_loss = running_loss / total
    epoch_accuracy = correct / total

    return epoch_loss, epoch_accuracy


# ============================================================
# Evaluation
# ============================================================

@torch.no_grad()
def evaluate(loader):

    model.eval()

    running_loss = 0.0

    all_labels = []
    all_predictions = []
    all_probabilities = []

    for images, labels in loader:

        images = images.to(
            device,
            non_blocking=True
        )

        labels = labels.to(
            device,
            non_blocking=True
        )

        outputs = model(images)

        loss = criterion(
            outputs,
            labels
        )

        probabilities = torch.softmax(
            outputs,
            dim=1
        )

        predictions = outputs.argmax(
            dim=1
        )

        running_loss += (
            loss.item() * images.size(0)
        )

        all_labels.extend(
            labels.cpu().numpy()
        )

        all_predictions.extend(
            predictions.cpu().numpy()
        )

        # class 1 = fake
        all_probabilities.extend(
            probabilities[:, 1]
            .cpu()
            .numpy()
        )

    total = len(all_labels)

    loss = running_loss / total

    accuracy = accuracy_score(
        all_labels,
        all_predictions
    )

    precision = precision_score(
        all_labels,
        all_predictions,
        zero_division=0
    )

    recall = recall_score(
        all_labels,
        all_predictions,
        zero_division=0
    )

    f1 = f1_score(
        all_labels,
        all_predictions,
        zero_division=0
    )

    try:
        auc = roc_auc_score(
            all_labels,
            all_probabilities
        )
    except ValueError:
        auc = 0.0

    return {
        "loss": loss,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "roc_auc": auc,
        "labels": all_labels,
        "predictions": all_predictions,
        "probabilities": all_probabilities,
    }


# ============================================================
# Main training loop
# ============================================================

history = []

best_val_loss = float("inf")
best_val_f1 = 0.0

epochs_without_improvement = 0

print("\nStarting training...\n")

for epoch in range(
    1,
    EPOCHS + 1
):

    start_time = time.time()

    train_loss, train_accuracy = (
        train_one_epoch()
    )

    val_metrics = evaluate(
        val_loader
    )

    scheduler.step(
        val_metrics["loss"]
    )

    elapsed = (
        time.time() - start_time
    )

    current_lr = optimizer.param_groups[0]["lr"]

    print(
        f"Epoch {epoch:02d}/{EPOCHS} | "
        f"Time {elapsed:.1f}s | "
        f"LR {current_lr:.2e}"
    )

    print(
        f"  Train Loss: {train_loss:.4f} | "
        f"Train Acc: {train_accuracy:.4f}"
    )

    print(
        f"  Val Loss: {val_metrics['loss']:.4f} | "
        f"Val Acc: {val_metrics['accuracy']:.4f} | "
        f"Val F1: {val_metrics['f1']:.4f} | "
        f"Val AUC: {val_metrics['roc_auc']:.4f}"
    )

    epoch_record = {
        "epoch": epoch,
        "train_loss": train_loss,
        "train_accuracy": train_accuracy,
        "val_loss": val_metrics["loss"],
        "val_accuracy": val_metrics["accuracy"],
        "val_precision": val_metrics["precision"],
        "val_recall": val_metrics["recall"],
        "val_f1": val_metrics["f1"],
        "val_roc_auc": val_metrics["roc_auc"],
    }

    history.append(epoch_record)

    # --------------------------------------------------------
    # Save best model
    # --------------------------------------------------------

    improved = (
        val_metrics["f1"] > best_val_f1
        or (
            val_metrics["f1"] == best_val_f1
            and val_metrics["loss"] < best_val_loss
        )
    )

    if improved:

        best_val_f1 = val_metrics["f1"]
        best_val_loss = val_metrics["loss"]

        epochs_without_improvement = 0

        torch.save(
            {
                "model_state_dict": model.state_dict(),
                "class_to_idx": train_dataset.class_to_idx,
                "image_size": IMAGE_SIZE,
                "architecture": "efficientnet_b0",
                "best_val_f1": best_val_f1,
                "best_val_loss": best_val_loss,
            },
            BEST_MODEL,
        )

        print(
            f"  ✓ Best model saved: "
            f"{BEST_MODEL}"
        )

    else:

        epochs_without_improvement += 1

        print(
            f"  No improvement "
            f"({epochs_without_improvement}/{PATIENCE})"
        )

    if epochs_without_improvement >= PATIENCE:

        print("\nEarly stopping triggered.")

        break


# ============================================================
# Load best model
# ============================================================

print("\nLoading best model...")

checkpoint = torch.load(
    BEST_MODEL,
    map_location=device,
)

model.load_state_dict(
    checkpoint["model_state_dict"]
)


# ============================================================
# Final test evaluation
# ============================================================

print("\n" + "=" * 70)
print("FINAL TEST EVALUATION")
print("=" * 70)

test_metrics = evaluate(
    test_loader
)

print(
    f"\nAccuracy : "
    f"{test_metrics['accuracy']:.4f}"
)

print(
    f"Precision: "
    f"{test_metrics['precision']:.4f}"
)

print(
    f"Recall   : "
    f"{test_metrics['recall']:.4f}"
)

print(
    f"F1 Score : "
    f"{test_metrics['f1']:.4f}"
)

print(
    f"ROC-AUC  : "
    f"{test_metrics['roc_auc']:.4f}"
)


# ============================================================
# Confusion Matrix
# ============================================================

cm = confusion_matrix(
    test_metrics["labels"],
    test_metrics["predictions"]
)

print("\nConfusion Matrix:")
print(cm)

print(
    "\nRows = actual "
    "[real, fake]"
)

print(
    "Columns = predicted "
    "[real, fake]"
)


# ============================================================
# Save metrics
# ============================================================

output_metrics = {
    "architecture": "EfficientNet-B0",
    "image_size": IMAGE_SIZE,
    "batch_size": BATCH_SIZE,
    "epochs_requested": EPOCHS,
    "learning_rate": LEARNING_RATE,
    "weight_decay": WEIGHT_DECAY,
    "dataset": {
        "train": len(train_dataset),
        "val": len(val_dataset),
        "test": len(test_dataset),
    },
    "class_to_idx": train_dataset.class_to_idx,
    "history": history,
    "test": {
        "accuracy": test_metrics["accuracy"],
        "precision": test_metrics["precision"],
        "recall": test_metrics["recall"],
        "f1": test_metrics["f1"],
        "roc_auc": test_metrics["roc_auc"],
        "confusion_matrix": cm.tolist(),
    },
}


with open(
    METRICS_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        output_metrics,
        f,
        indent=2
    )


print("\n" + "=" * 70)
print("TRAINING COMPLETE")
print("=" * 70)

print(
    f"\nBest model:\n{BEST_MODEL}"
)

print(
    f"\nMetrics:\n{METRICS_FILE}"
)