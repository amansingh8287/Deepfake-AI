from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Detection
from app.services.report_service import build_report

router = APIRouter(prefix="/report", tags=["reports"])


@router.get("/{detection_id}")
def download_report(detection_id: int, db: Session = Depends(get_db)) -> FileResponse:
    detection = db.get(Detection, detection_id)
    if detection is None:
        raise HTTPException(status_code=404, detail="Detection record not found.")

    report_path = Path(detection.report_path) if detection.report_path else None
    if report_path is None or not report_path.exists():
        report_path = build_report(detection)
        detection.report_path = str(report_path)
        db.add(detection)
        db.commit()

    return FileResponse(path=report_path, filename=report_path.name, media_type="application/pdf")

