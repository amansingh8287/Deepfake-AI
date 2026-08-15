import mimetypes
import os
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.config import get_settings

settings = get_settings()


def validate_upload(upload: UploadFile, media_type: str) -> str:
    filename = upload.filename or "upload.bin"
    suffix = Path(filename).suffix.lower()
    allowed = settings.allowed_image_suffixes if media_type == "image" else settings.allowed_video_suffixes
    if suffix not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported {media_type} extension '{suffix}'. Allowed: {', '.join(allowed)}",
        )

    guessed_type, _ = mimetypes.guess_type(filename)
    if guessed_type and not guessed_type.startswith(media_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Uploaded file MIME type does not match expected {media_type} content.",
        )
    return suffix


async def save_upload(upload: UploadFile, media_type: str) -> Path:
    suffix = validate_upload(upload, media_type)
    target = settings.upload_dir / f"{uuid4().hex}{suffix}"
    size = 0

    with target.open("wb") as buffer:
        while chunk := await upload.read(1024 * 1024):
            size += len(chunk)
            if size > settings.max_upload_bytes:
                buffer.close()
                target.unlink(missing_ok=True)
                raise HTTPException(status_code=413, detail="File too large for configured upload limit.")
            buffer.write(chunk)

    await upload.close()
    return target


def cleanup_file(path: Path) -> None:
    try:
        if path.exists():
            path.unlink()
    except OSError:
        pass


def safe_report_filename(original_filename: str, detection_id: int) -> str:
    stem = Path(original_filename).stem[:80] or "report"
    sanitized = "".join(ch for ch in stem if ch.isalnum() or ch in {"-", "_"})
    return f"{sanitized or 'report'}-{detection_id}.pdf"

