import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Detection
from app.schemas import DetectionHistoryItem, HistoryResponse, HistorySummary, SuspiciousFrame

router = APIRouter(prefix="/history", tags=["history"])


@router.get("", response_model=HistoryResponse)
def list_history(db: Session = Depends(get_db)) -> HistoryResponse:
    detections = db.execute(select(Detection).order_by(Detection.created_at.desc())).scalars().all()
    items = [
        DetectionHistoryItem(
            id=item.id,
            filename=item.filename,
            media_type=item.media_type,
            prediction=item.prediction,
            confidence=item.confidence,
            processing_time=item.processing_time,
            faces_detected=item.faces_detected,
            frames_analyzed=item.frames_analyzed,
            suspicious_frames=[SuspiciousFrame(**frame) for frame in json.loads(item.suspicious_frames or "[]")],
            explanation=item.explanation,
            model_name=item.model_name,
            mode=item.mode,
            created_at=item.created_at,
        )
        for item in detections
    ]
    total_scans = len(items)
    return HistoryResponse(
        summary=HistorySummary(
            total_scans=total_scans,
            image_scans=sum(1 for item in items if item.media_type == "image"),
            video_scans=sum(1 for item in items if item.media_type == "video"),
            deepfakes_detected=sum(1 for item in items if item.prediction == "DEEPFAKE"),
        ),
        items=items,
    )


@router.delete("/{detection_id}")
def delete_history(detection_id: int, db: Session = Depends(get_db)) -> dict:
    detection = db.get(Detection, detection_id)
    if detection is None:
        raise HTTPException(status_code=404, detail="History item not found.")
    db.delete(detection)
    db.commit()
    return {"status": "deleted", "id": detection_id}

