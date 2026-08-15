from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    app: str
    model_mode: str


class SuspiciousFrame(BaseModel):
    index: int
    timestamp: float
    confidence: float
    note: str


class DetectionBaseResponse(BaseModel):
    prediction: Literal["REAL", "DEEPFAKE"]
    confidence: float = Field(ge=0, le=100)
    processing_time: float
    faces_detected: int = 0
    explanation: str
    model_name: str
    mode: str
    disclaimer: str


class ImageDetectionResponse(DetectionBaseResponse):
    pass


class VideoDetectionResponse(DetectionBaseResponse):
    frames_analyzed: int
    suspicious_frames: list[SuspiciousFrame]


class DetectionHistoryItem(BaseModel):
    id: int
    filename: str
    media_type: str
    prediction: str
    confidence: float
    processing_time: float
    faces_detected: int
    frames_analyzed: int
    suspicious_frames: list[SuspiciousFrame]
    explanation: str
    model_name: str
    mode: str
    created_at: datetime

    class Config:
        from_attributes = True


class HistorySummary(BaseModel):
    total_scans: int
    image_scans: int
    video_scans: int
    deepfakes_detected: int


class HistoryResponse(BaseModel):
    summary: HistorySummary
    items: list[DetectionHistoryItem]

