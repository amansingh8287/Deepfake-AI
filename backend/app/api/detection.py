import json

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Detection
from app.schemas import ImageDetectionResponse, VideoDetectionResponse
from app.services.file_service import cleanup_file, save_upload
from app.ml.inference import inference_service
from app.ml.video_analyzer import video_analyzer

router = APIRouter(prefix="/detect", tags=["detection"])


@router.post("/image", response_model=ImageDetectionResponse)
async def detect_image(file: UploadFile = File(...), db: Session = Depends(get_db)) -> ImageDetectionResponse:
    path = await save_upload(file, "image")
    try:
        result = inference_service.analyze_image(path)
        record = Detection(
            filename=file.filename or path.name,
            media_type="image",
            prediction=result["prediction"],
            confidence=result["confidence"],
            processing_time=result["processing_time"],
            faces_detected=result["faces_detected"],
            frames_analyzed=0,
            suspicious_frames="[]",
            explanation=result["explanation"],
            model_name=result["model_name"],
            mode=result["mode"],
        )
        db.add(record)
        db.commit()
        return ImageDetectionResponse(**result)
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        cleanup_file(path)


@router.post("/video", response_model=VideoDetectionResponse)
async def detect_video(file: UploadFile = File(...), db: Session = Depends(get_db)) -> VideoDetectionResponse:
    path = await save_upload(file, "video")
    try:
        result = video_analyzer.analyze(path)
        record = Detection(
            filename=file.filename or path.name,
            media_type="video",
            prediction=result["prediction"],
            confidence=result["confidence"],
            processing_time=result["processing_time"],
            faces_detected=result["faces_detected"],
            frames_analyzed=result["frames_analyzed"],
            suspicious_frames=json.dumps([frame.model_dump() for frame in result["suspicious_frames"]]),
            explanation=result["explanation"],
            model_name=result["model_name"],
            mode=result["mode"],
        )
        db.add(record)
        db.commit()
        return VideoDetectionResponse(**result)
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        cleanup_file(path)

