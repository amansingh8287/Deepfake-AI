from pathlib import Path
import random
import shutil

# ============================================================
# DeepGuard - Prepare balanced video dataset
# ============================================================

SEED = 42

PROJECT_ROOT = Path(r"D:\deep fake model")
SOURCE_ROOT = (
    PROJECT_ROOT
    / "dataset"
    / "ffpp_c23"
    / "FaceForensics++_C23"
)

OUTPUT_ROOT = PROJECT_ROOT / "dataset"

TOTAL_REAL = 1000
TOTAL_FAKE = 1000

TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

FAKE_CATEGORIES = [
    "DeepFakeDetection",
    "Deepfakes",
    "Face2Face",
    "FaceShifter",
    "FaceSwap",
    "NeuralTextures",
]

VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv"}


def get_videos(folder: Path):
    """Return all video files recursively."""
    if not folder.exists():
        raise FileNotFoundError(f"Folder not found: {folder}")

    return sorted(
        p for p in folder.rglob("*")
        if p.is_file() and p.suffix.lower() in VIDEO_EXTENSIONS
    )


def split_items(items):
    """Deterministic 70/15/15 split."""
    items = list(items)
    random.shuffle(items)

    n = len(items)

    train_end = int(n * TRAIN_RATIO)
    val_end = train_end + int(n * VAL_RATIO)

    train = items[:train_end]
    val = items[train_end:val_end]
    test = items[val_end:]

    return train, val, test


def create_output_dirs():
    for split in ["train", "val", "test"]:
        for label in ["real", "fake"]:
            folder = OUTPUT_ROOT / split / label
            folder.mkdir(parents=True, exist_ok=True)


def clean_output():
    """
    Remove previously generated train/val/test files.
    This does NOT touch the original FF++ dataset.
    """
    print("\nCleaning previous prepared dataset...")

    for split in ["train", "val", "test"]:
        for label in ["real", "fake"]:
            folder = OUTPUT_ROOT / split / label

            if folder.exists():
                for item in folder.iterdir():
                    if item.is_file() or item.is_symlink():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)


def copy_files(files, destination: Path):
    destination.mkdir(parents=True, exist_ok=True)

    for index, src in enumerate(files, start=1):
        # Prefix avoids collisions between different fake categories.
        new_name = f"{index:04d}_{src.name}"

        target = destination / new_name

        shutil.copy2(src, target)

        if index % 100 == 0 or index == len(files):
            print(
                f"  Copied {index}/{len(files)} -> "
                f"{destination.relative_to(PROJECT_ROOT)}"
            )


def main():
    random.seed(SEED)

    print("=" * 65)
    print("DeepGuard - Dataset Preparation")
    print("=" * 65)

    print(f"\nSource:")
    print(SOURCE_ROOT)

    print(f"\nOutput:")
    print(OUTPUT_ROOT)

    # --------------------------------------------------------
    # Check source
    # --------------------------------------------------------

    real_root = SOURCE_ROOT / "real"
    fake_root = SOURCE_ROOT / "fake"

    print("\nScanning REAL videos...")
    real_videos = get_videos(real_root)

    print(f"REAL videos found: {len(real_videos)}")

    if len(real_videos) < TOTAL_REAL:
        raise RuntimeError(
            f"Need {TOTAL_REAL} real videos, "
            f"but only {len(real_videos)} found."
        )

    # --------------------------------------------------------
    # Collect fake videos by manipulation type
    # --------------------------------------------------------

    fake_by_category = {}

    print("\nScanning FAKE categories...")

    for category in FAKE_CATEGORIES:
        category_root = fake_root / category
        videos = get_videos(category_root)

        fake_by_category[category] = videos

        print(f"{category:20s}: {len(videos)}")

        if len(videos) == 0:
            raise RuntimeError(
                f"No videos found in fake category: {category}"
            )

    # --------------------------------------------------------
    # Select REAL
    # --------------------------------------------------------

    random.shuffle(real_videos)
    selected_real = real_videos[:TOTAL_REAL]

    # --------------------------------------------------------
    # Select balanced FAKE
    # --------------------------------------------------------

    base_count = TOTAL_FAKE // len(FAKE_CATEGORIES)
    remainder = TOTAL_FAKE % len(FAKE_CATEGORIES)

    selected_fake = []

    print("\nSelecting fake videos:")

    for index, category in enumerate(FAKE_CATEGORIES):
        count = base_count + (1 if index < remainder else 0)

        available = fake_by_category[category]

        if len(available) < count:
            raise RuntimeError(
                f"{category} has only {len(available)} videos, "
                f"but {count} are required."
            )

        random.shuffle(available)

        selected = available[:count]
        selected_fake.extend(selected)

        print(f"{category:20s}: {len(selected)}")

    # --------------------------------------------------------
    # Shuffle selected datasets
    # --------------------------------------------------------

    random.shuffle(selected_real)
    random.shuffle(selected_fake)

    # --------------------------------------------------------
    # Split at VIDEO level
    # --------------------------------------------------------

    real_train, real_val, real_test = split_items(selected_real)
    fake_train, fake_val, fake_test = split_items(selected_fake)

    print("\n" + "=" * 65)
    print("VIDEO-LEVEL SPLIT")
    print("=" * 65)

    print(
        f"\nREAL: train={len(real_train)}, "
        f"val={len(real_val)}, test={len(real_test)}"
    )

    print(
        f"FAKE: train={len(fake_train)}, "
        f"val={len(fake_val)}, test={len(fake_test)}"
    )

    # --------------------------------------------------------
    # Create folders
    # --------------------------------------------------------

    create_output_dirs()

    # --------------------------------------------------------
    # Clean previous generated dataset
    # --------------------------------------------------------

    clean_output()

    # --------------------------------------------------------
    # Copy REAL
    # --------------------------------------------------------

    print("\nCopying REAL training videos...")
    copy_files(real_train, OUTPUT_ROOT / "train" / "real")

    print("\nCopying REAL validation videos...")
    copy_files(real_val, OUTPUT_ROOT / "val" / "real")

    print("\nCopying REAL test videos...")
    copy_files(real_test, OUTPUT_ROOT / "test" / "real")

    # --------------------------------------------------------
    # Copy FAKE
    # --------------------------------------------------------

    print("\nCopying FAKE training videos...")
    copy_files(fake_train, OUTPUT_ROOT / "train" / "fake")

    print("\nCopying FAKE validation videos...")
    copy_files(fake_val, OUTPUT_ROOT / "val" / "fake")

    print("\nCopying FAKE test videos...")
    copy_files(fake_test, OUTPUT_ROOT / "test" / "fake")

    # --------------------------------------------------------
    # Final summary
    # --------------------------------------------------------

    print("\n" + "=" * 65)
    print("DATASET PREPARATION COMPLETE")
    print("=" * 65)

    for split in ["train", "val", "test"]:
        real_count = len(get_videos(OUTPUT_ROOT / split / "real"))
        fake_count = len(get_videos(OUTPUT_ROOT / split / "fake"))

        print(
            f"{split.upper():5s}: "
            f"REAL={real_count:4d} | "
            f"FAKE={fake_count:4d} | "
            f"TOTAL={real_count + fake_count:4d}"
        )

    print("\nOriginal dataset was NOT modified.")
    print(f"Random seed: {SEED}")


if __name__ == "__main__":
    main()