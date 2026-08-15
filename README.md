# DeepGuard AI

DeepGuard AI is a final-year project for AI-based deepfake image and video detection. It combines a FastAPI backend, a face-aware computer-vision pipeline, SQLite history tracking, PDF report generation, a React dashboard, and a training/evaluation workspace for public deepfake datasets.

## Project Overview

The system accepts uploaded images and videos, validates them, runs a local inference pipeline, and returns:

- `REAL` or `DEEPFAKE`
- confidence percentage
- explanation text
- processing time
- suspicious video frame metadata
- detection history
- downloadable PDF reports

The application is intentionally honest about model state:

- `trained` mode means a real PyTorch checkpoint was loaded from `models/`
- `baseline` mode means no trained checkpoint was found, so deterministic artifact heuristics are used for development/demo workflows

## Features

- Deepfake image detection with face detection and fallback full-image analysis
- Deepfake video detection with configurable frame sampling
- MediaPipe/OpenCV face detection fallback path
- Modular PyTorch-compatible model loader
- SQLite-backed detection history
- PDF report download endpoint
- Responsive React dashboard with scan statistics and recent activity
- Training and evaluation scripts for datasets such as FaceForensics++, Celeb-DF, and DFDC
- Upload validation for file extension, MIME type, and size
- Docker support for backend deployment

## Architecture

### Backend

- `FastAPI` for REST APIs
- `SQLAlchemy` for SQLite persistence
- `Pydantic` settings and response schemas
- `OpenCV`, `Pillow`, `NumPy`, `MediaPipe` for preprocessing and face detection
- `PyTorch` + `torchvision` for checkpoint-backed inference
- `reportlab` for PDF reports

### Frontend

- `React` + `TypeScript`
- `Vite`
- `Tailwind CSS`
- `Recharts`
- `React Query`

### Detection Pipeline

Image flow:

1. Validate upload
2. Save temporary file
3. Detect face regions
4. Crop and normalize face candidates
5. Run trained classifier or baseline heuristic
6. Aggregate scores
7. Store result in database

Video flow:

1. Validate upload
2. Sample frames at configurable FPS
3. Detect dominant face or fall back to full frame
4. Score each sampled frame
5. Aggregate probabilities
6. Mark suspicious frames above a threshold
7. Store result in database

## Project Structure

```text
backend/
  app/
    api/
    ml/
    services/
  tests/
frontend/
  src/
    components/
    pages/
    services/
    types/
training/
docs/
models/
uploads/
reports/
```

## Installation

### 1. Backend setup

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend URL:

- `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`

### 2. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Frontend URL:

- `http://localhost:5173`

If needed, set `VITE_API_BASE_URL` to match your backend API location.

### 3. Environment configuration

Copy `.env.example` to `.env` and adjust values as needed.

Key variables:

- `DEEPGUARD_MODEL_PATH`
- `DEEPGUARD_MAX_UPLOAD_MB`
- `DEEPGUARD_VIDEO_SAMPLE_FPS`
- `DEEPGUARD_MAX_VIDEO_FRAMES`
- `DEEPGUARD_FRAME_SCORE_THRESHOLD`

## Model Setup

Place a trained `.pt` or `.pth` checkpoint inside `models/`, then point `DEEPGUARD_MODEL_PATH` to it.

Current classifier integration expects an EfficientNet-B0 style binary classifier with a single-logit output head.

If no checkpoint exists:

- the backend does not crash
- the API continues to function
- the returned mode is `baseline`
- the UI should be presented as a demo/development workflow, not benchmarked detection performance

## Dataset and Training

No dataset is downloaded automatically.

Recommended public datasets:

- FaceForensics++
- Celeb-DF
- DFDC

Training workspace:

- `training/train.py`
- `training/evaluate.py`
- `training/dataset.py`
- `training/config.py`

Expected dataset layout example:

```text
data/
  faceforensics/
    real/
    fake/
```

Run training:

```bash
cd training
python train.py
python evaluate.py
```

Evaluation script reports:

- Accuracy
- Precision
- Recall
- F1 Score
- ROC-AUC
- Confusion Matrix

## API Summary

- `GET /api/health`
- `POST /api/detect/image`
- `POST /api/detect/video`
- `GET /api/history`
- `DELETE /api/history/{id}`
- `GET /api/report/{id}`

Detailed endpoint notes are in [docs/api.md](docs/api.md).

## Testing

Backend tests cover:

- health endpoint
- image upload validation
- image detection endpoint
- history retrieval

Frontend includes a starter component test for the upload zone.

Recommended commands after installing dependencies:

```bash
cd backend
python -m pytest tests
```

```bash
cd frontend
npm test
```

## Docker

Backend container workflow:

```bash
docker-compose up --build
```

This currently focuses on the backend service and mounted model/report/upload directories.

## Troubleshooting

- If `npm` is blocked in PowerShell, use `npm.cmd`.
- If no trained checkpoint is available, the app will stay in `baseline` mode.
- If MediaPipe is unavailable on the machine, OpenCV Haar cascades still provide a fallback face detector.
- Large or unsupported files are rejected by backend validation before analysis begins.

## Limitations

- Baseline mode is not a substitute for a trained detector.
- Detection results are probabilistic and sensitive to compression, lighting, blur, and dataset bias.
- The current training scaffold assumes a binary `real` vs `fake` dataset structure.
- The Docker setup currently packages the backend, not the frontend dev server.

## Ethical Considerations

Deepfake detection tools can produce false positives and false negatives. DeepGuard AI should be used for educational demos, research workflows, and screening support rather than as conclusive proof in legal, disciplinary, or safety-critical contexts.

## Disclaimer

DeepGuard AI provides an AI-based prediction and should not be treated as definitive proof that media is authentic or manipulated.
