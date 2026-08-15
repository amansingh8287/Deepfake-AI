from __future__ import annotations

from pathlib import Path

from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms


class DeepfakeDataset(Dataset):
    def __init__(self, items: list[tuple[Path, int]], image_size: int = 224) -> None:
        self.items = items
        self.transform = transforms.Compose(
            [
                transforms.Resize((image_size, image_size)),
                transforms.RandomHorizontalFlip(),
                transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.1),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ]
        )

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int):
        path, label = self.items[index]
        image = Image.open(path).convert("RGB")
        return self.transform(image), label

