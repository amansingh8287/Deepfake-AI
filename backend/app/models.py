from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Detection(Base):
    __tablename__ = "detections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    media_type: Mapped[str] = mapped_column(String(32), nullable=False)
    prediction: Mapped[str] = mapped_column(String(32), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    processing_time: Mapped[float] = mapped_column(Float, nullable=False)
    faces_detected: Mapped[int] = mapped_column(Integer, default=0)
    frames_analyzed: Mapped[int] = mapped_column(Integer, default=0)
    suspicious_frames: Mapped[str] = mapped_column(Text, default="[]")
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    model_name: Mapped[str] = mapped_column(String(128), nullable=False)
    mode: Mapped[str] = mapped_column(String(32), default="baseline")
    report_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

