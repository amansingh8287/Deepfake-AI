from functools import lru_cache
from pathlib import Path

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="DeepGuard AI", alias="DEEPGUARD_APP_NAME")
    api_prefix: str = Field(default="/api", alias="DEEPGUARD_API_PREFIX")
    database_url: str = Field(default="sqlite:///./deepguard.db", alias="DEEPGUARD_DATABASE_URL")
    upload_dir: Path = Field(default=Path("uploads"), alias="DEEPGUARD_UPLOAD_DIR")
    report_dir: Path = Field(default=Path("reports"), alias="DEEPGUARD_REPORT_DIR")
    model_dir: Path = Field(default=Path("models"), alias="DEEPGUARD_MODEL_DIR")
    model_path: Path = Field(default=Path("models/deepguard_baseline.pt"), alias="DEEPGUARD_MODEL_PATH")
    model_name: str = Field(default="efficientnet_b0_baseline", alias="DEEPGUARD_MODEL_NAME")
    max_upload_mb: int = Field(default=150, alias="DEEPGUARD_MAX_UPLOAD_MB")
    allowed_image_extensions: str = Field(default="jpg,jpeg,png,webp", alias="DEEPGUARD_ALLOWED_IMAGE_EXTENSIONS")
    allowed_video_extensions: str = Field(default="mp4,mov,avi,mkv,webm", alias="DEEPGUARD_ALLOWED_VIDEO_EXTENSIONS")
    video_sample_fps: float = Field(default=2.0, alias="DEEPGUARD_VIDEO_SAMPLE_FPS")
    max_video_frames: int = Field(default=48, alias="DEEPGUARD_MAX_VIDEO_FRAMES")
    frame_score_threshold: float = Field(default=0.62, alias="DEEPGUARD_FRAME_SCORE_THRESHOLD")
    cors_origins: str = Field(default="http://localhost:5173,http://127.0.0.1:5173", alias="DEEPGUARD_CORS_ORIGINS")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @computed_field
    @property
    def allowed_image_suffixes(self) -> tuple[str, ...]:
        return tuple(f".{item.strip().lower().lstrip('.')}" for item in self.allowed_image_extensions.split(",") if item.strip())

    @computed_field
    @property
    def allowed_video_suffixes(self) -> tuple[str, ...]:
        return tuple(f".{item.strip().lower().lstrip('.')}" for item in self.allowed_video_extensions.split(",") if item.strip())

    @computed_field
    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024

    @computed_field
    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.report_dir.mkdir(parents=True, exist_ok=True)
    settings.model_dir.mkdir(parents=True, exist_ok=True)
    return settings

