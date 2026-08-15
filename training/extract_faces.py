from pathlib import Path
import cv2
import shutil

# ============================================================
# DeepGuard - FAST Face Extraction
# Video -> sampled frames -> face crop -> 224x224 JPG
# ============================================================

PROJECT_ROOT = Path(r"D:\deep fake model")

INPUT_ROOT = PROJECT_ROOT / "dataset"
OUTPUT_ROOT = PROJECT_ROOT / "dataset" / "faces"

FRAMES_PER_VIDEO = 4
IMAGE_SIZE = 224
FACE_PADDING = 0.20

VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv"}

# OpenCV built-in Haar Cascade
CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"


def get_videos(folder):
    return sorted(
        p for p in folder.rglob("*")
        if p.is_file() and p.suffix.lower() in VIDEO_EXTENSIONS
    )


def detect_largest_face(frame, detector):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = detector.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(60, 60),
    )

    if len(faces) == 0:
        return None

    # Largest face
    x, y, w, h = max(
        faces,
        key=lambda box: box[2] * box[3]
    )

    return x, y, w, h


def crop_face(frame, box):
    x, y, w, h = box

    height, width = frame.shape[:2]

    pad_x = int(w * FACE_PADDING)
    pad_y = int(h * FACE_PADDING)

    x1 = max(0, x - pad_x)
    y1 = max(0, y - pad_y)
    x2 = min(width, x + w + pad_x)
    y2 = min(height, y + h + pad_y)

    face = frame[y1:y2, x1:x2]

    if face.size == 0:
        return None

    return cv2.resize(
        face,
        (IMAGE_SIZE, IMAGE_SIZE),
        interpolation=cv2.INTER_AREA,
    )


def get_sample_positions(total_frames):
    if total_frames <= 0:
        return []

    if total_frames <= FRAMES_PER_VIDEO:
        return set(range(total_frames))

    # 4 approximately equally spaced positions
    positions = []

    for i in range(FRAMES_PER_VIDEO):
        pos = int(
            i * (total_frames - 1)
            / (FRAMES_PER_VIDEO - 1)
        )
        positions.append(pos)

    return set(positions)


def process_video(video_path, output_dir, detector):
    cap = cv2.VideoCapture(str(video_path))

    if not cap.isOpened():
        return 0, "cannot_open"

    total_frames = int(
        cap.get(cv2.CAP_PROP_FRAME_COUNT)
    )

    if total_frames <= 0:
        cap.release()
        return 0, "no_frames"

    sample_positions = get_sample_positions(total_frames)

    saved = 0
    frame_number = 0

    video_id = video_path.stem

    while True:
        success, frame = cap.read()

        if not success:
            break

        if frame_number in sample_positions:

            box = detect_largest_face(
                frame,
                detector
            )

            if box is not None:

                face = crop_face(
                    frame,
                    box
                )

                if face is not None:

                    filename = (
                        f"{video_id}"
                        f"_frame_{frame_number:06d}.jpg"
                    )

                    output_path = (
                        output_dir / filename
                    )

                    ok = cv2.imwrite(
                        str(output_path),
                        face,
                        [
                            cv2.IMWRITE_JPEG_QUALITY,
                            95,
                        ],
                    )

                    if ok:
                        saved += 1

        frame_number += 1

        # Once all required positions are processed,
        # no need to continue reading the video.
       
        if frame_number > max(sample_positions):
            break

    cap.release()

    if saved == 0:
        return 0, "no_face"

    return saved, None


def clean_output():
    if OUTPUT_ROOT.exists():
        print(
            f"Removing previous face dataset:\n"
            f"{OUTPUT_ROOT}"
        )
        shutil.rmtree(OUTPUT_ROOT)

    OUTPUT_ROOT.mkdir(
        parents=True,
        exist_ok=True
    )


def process_split(split, detector):

    print("\n" + "=" * 60)
    print(f"PROCESSING {split.upper()}")
    print("=" * 60)

    split_total = 0
    split_faces = 0
    split_failed = 0

    for label in ["real", "fake"]:

        input_dir = (
            INPUT_ROOT
            / split
            / label
        )

        output_dir = (
            OUTPUT_ROOT
            / split
            / label
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        videos = get_videos(input_dir)

        print(
            f"\n{split}/{label}: "
            f"{len(videos)} videos"
        )

        for index, video_path in enumerate(
            videos,
            start=1
        ):

            saved, error = process_video(
                video_path,
                output_dir,
                detector
            )

            split_total += 1
            split_faces += saved

            if error is not None:
                split_failed += 1

            if (
                index % 25 == 0
                or index == len(videos)
            ):
                print(
                    f"  {index}/{len(videos)} "
                    f"| faces saved: {saved}"
                )

    return (
        split_total,
        split_faces,
        split_failed
    )


def count_images(folder):

    if not folder.exists():
        return 0

    return len(
        list(folder.rglob("*.jpg"))
    )


def main():

    print("=" * 60)
    print("DeepGuard - FAST Face Extraction")
    print("=" * 60)

    print(f"\nInput : {INPUT_ROOT}")
    print(f"Output: {OUTPUT_ROOT}")

    print(
        f"\nFrames per video: "
        f"{FRAMES_PER_VIDEO}"
    )

    print(
        f"Image size: "
        f"{IMAGE_SIZE}x{IMAGE_SIZE}"
    )

    # Check dataset
    for split in [
        "train",
        "val",
        "test"
    ]:
        for label in [
            "real",
            "fake"
        ]:

            folder = (
                INPUT_ROOT
                / split
                / label
            )

            if not folder.exists():
                raise FileNotFoundError(
                    f"Dataset folder missing:\n"
                    f"{folder}"
                )

    # Fresh output
    clean_output()

    # OpenCV detector
    print("\nLoading OpenCV face detector...")

    detector = cv2.CascadeClassifier(
        CASCADE_PATH
    )

    if detector.empty():
        raise RuntimeError(
            "Could not load OpenCV Haar Cascade."
        )

    print("Face detector ready.")

    # Process
    for split in [
        "train",
        "val",
        "test"
    ]:

        process_split(
            split,
            detector
        )

    # Final summary
    print("\n" + "=" * 60)
    print("FACE EXTRACTION COMPLETE")
    print("=" * 60)

    grand_total = 0

    for split in [
        "train",
        "val",
        "test"
    ]:

        real_count = count_images(
            OUTPUT_ROOT
            / split
            / "real"
        )

        fake_count = count_images(
            OUTPUT_ROOT
            / split
            / "fake"
        )

        total = real_count + fake_count

        grand_total += total

        print(
            f"{split.upper():5s}: "
            f"REAL={real_count:5d} | "
            f"FAKE={fake_count:5d} | "
            f"TOTAL={total:5d}"
        )

    print(
        f"\nTOTAL FACE IMAGES: "
        f"{grand_total}"
    )

    print(
        f"\nSaved to:\n"
        f"{OUTPUT_ROOT}"
    )

    print("\nOriginal videos were NOT modified.")


if __name__ == "__main__":
    main()