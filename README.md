# DeepGuard AI

DeepGuard AI is a full-stack deepfake detection application for analyzing suspicious **images and videos**. It provides a web dashboard for uploading media, running model inference, viewing confidence and detection details, reviewing scan history, and downloading reports.

> **Important:** DeepGuard AI provides an AI-based prediction and should not be treated as definitive proof that media is authentic or manipulated.

## 📸 Application Screenshots

### Dashboard

The dashboard gives an overview of total scans, image scans, video scans, deepfakes flagged, recent scan severity, and recent detections.

![DeepGuard AI Dashboard]
<img width="1877" height="1030" alt="Screenshot 2026-08-15 101928" src="https://github.com/user-attachments/assets/25a81931-59e2-47e3-8cb4-dd01993ef45c" />


### Image Detection — Real Result

The image detection page detects the face, analyzes the largest detected face region, and displays the model prediction, confidence, processing time, and detected-face count.

![Image Detection Real Result]
<img width="1779" height="952" alt="Screenshot 2026-08-15 102019" src="https://github.com/user-attachments/assets/ede4a920-16e3-464c-9941-889c1a7a6bf0" />

### Image Detection — Deepfake Result

Example of a suspicious image being classified as `DEEPFAKE` with a high confidence score.

![Image Detection Deepfake Result]
<img width="1865" height="885" alt="Screenshot 2026-08-15 102202" src="https://github.com/user-attachments/assets/3989a9a4-aeac-44e9-a856-b4c81c4c2e48" />


### Video Detection — Real Result

The video analyzer samples frames, detects faces in sampled frames, classifies the largest face in each sampled frame, and reports the aggregate result.

![Video Detection Real Result]
<img width="1841" height="1019" alt="Screenshot 2026-08-15 105718" src="https://github.com/user-attachments/assets/9047ddda-2a23-4c69-a4ac-e5e0e8b833b8" />


### Detection History

The history page records previous image/video detections with prediction, confidence, date, report, and delete actions.

![Detection History]
<img width="1897" height="1026" alt="Screenshot 2026-08-15 101717" src="https://github.com/user-attachments/assets/ec55a094-b568-4f16-852a-190f46b75e67" />


---

## ✨ Features

### Image Detection
- Upload an image from the dashboard.
- Detect faces before classification.
- Analyze the largest detected face region.
- Return prediction (`REAL` / `DEEPFAKE`), confidence, processing time, faces detected, model name, mode, and explanation.
- If no clear face is detected, return `UNKNOWN` instead of classifying the full image as a face crop.

### Video Detection
- Upload a video for frame-based analysis.
- Configurable frame sampling.
- Face detection on sampled frames.
- Largest detected face is used for each sampled frame.
- Reports overall prediction, confidence, frames analyzed, suspicious frames, faces detected, and processing time.
- Suspicious frames include frame index, timestamp, confidence, and a note.

### Dashboard
The dashboard shows:
- Total scans
- Image scans
- Video scans
- Deepfakes flagged
- Recent scan severity/confidence trend
- Recent scan results

### History & Reports
- Review previous detections.
- View file name, type, prediction, confidence, and date.
- Download reports.
- Delete history records.

## 🧠 Machine Learning

DeepGuard AI uses a trained **EfficientNet-B0** checkpoint.

```text
models/deepguard_efficientnet_b0.pth
```

Model name:

```text
deepguard_efficientnet_b0
```

Class mapping:

```text
fake = 0
real = 1
```

### Training dataset

The prepared dataset used:

```text
TRAIN: REAL=2779 | FAKE=2727 | TOTAL=5506
VAL  : REAL= 599 | FAKE= 588 | TOTAL=1187
TEST : REAL= 594 | FAKE= 576 | TOTAL=1170

TOTAL FACE IMAGES: 7863
```

### Final test metrics

```text
Accuracy : 0.7821
Precision: 0.7783
Recall   : 0.7980
F1 Score : 0.7880
ROC-AUC  : 0.8713
```

Confusion matrix:

```text
[[441 135]
 [120 474]]
```

Rows are actual `[real, fake]`; columns are predicted `[real, fake]`.

These are results on the project's test split and do not guarantee the same performance on unseen real-world media.

## 🔍 Inference Pipeline

### Image

```text
Upload image
    ↓
Load image as RGB
    ↓
Detect faces
    ↓
No face → UNKNOWN
    ↓
Select largest detected face
    ↓
EfficientNet-B0 prediction
    ↓
Deepfake probability
    ↓
REAL / DEEPFAKE
```

The classifier uses the largest detected face rather than averaging predictions across all detected face regions.

### Video

```text
Upload video
    ↓
Open with OpenCV
    ↓
Sample configurable frames
    ↓
Detect faces in each sampled frame
    ↓
Select largest face in each frame
    ↓
Classify sampled face
    ↓
Aggregate frame probabilities
    ↓
Overall REAL / DEEPFAKE
```

Suspicious frames are stored separately with their frame index, timestamp, confidence, and note.

## 🏗️ Project Structure

```text
Deep fake model/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── ml/
│   │   └── services/
│   ├── tests/
│   └── .venv/
├── frontend/
├── models/
│   └── deepguard_efficientnet_b0.pth
├── training/
├── dataset/
├── docs/
│   └── screenshots/
├── reports/
├── uploads/
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## ⚙️ Configuration

Important settings include:

```text
DEEPGUARD_MODEL_DIR
DEEPGUARD_MODEL_PATH
DEEPGUARD_MODEL_NAME
DEEPGUARD_UPLOAD_DIR
DEEPGUARD_REPORT_DIR
DEEPGUARD_VIDEO_SAMPLE_FPS
DEEPGUARD_MAX_VIDEO_FRAMES
DEEPGUARD_FRAME_SCORE_THRESHOLD
```

## 🚀 Run the Backend

```powershell
cd "D:\deep fake model\backend"
& ".\.venv\Scripts\Activate.ps1"
python -m uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

## 🌐 API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Health check |
| POST | `/api/detect/image` | Analyze an image |
| POST | `/api/detect/video` | Analyze a video |
| GET | `/api/history` | List detection history |
| DELETE | `/api/history/{detection_id}` | Delete history |
| GET | `/api/report/{detection_id}` | Download a report |

## 🧪 Verification

Check the configured model:

```powershell
python -c "from app.config import get_settings; s=get_settings(); print('MODEL PATH =', s.model_path); print('EXISTS =', s.model_path.exists()); print('MODEL NAME =', s.model_name)"
```

Expected:

```text
EXISTS = True
MODEL NAME = deepguard_efficientnet_b0
```

## 🐳 Docker

The repository contains:

```text
Dockerfile
docker-compose.yml
```

These provide a basis for containerized deployment. GPU support and model/data mounting should be configured for the target environment.

## ⚠️ Limitations

DeepGuard AI is an experimental AI-based detection system.

- A prediction is not definitive proof of manipulation or authenticity.
- The checkpoint was evaluated on the project's test split and may not generalize to every real-world source.
- AI-generated artwork, stylized images, heavy compression, screenshots, social-media recompression, and unseen manipulation methods may behave differently from the training data.
- Face detection quality affects face-based classification.
- Video analysis uses sampled frames rather than every frame.
- Confidence is the model's output score, not a guarantee of truth.

Use results as decision-support signals and combine them with appropriate human review for important decisions.

## 🔐 Repository Hygiene

Do not commit:

```text
.venv/
.env
uploads/
private/generated reports
large private datasets
temporary files
```

Before pushing to GitHub:

```powershell
git status
git check-ignore .env
git check-ignore backend/.venv
```

## 📌 Current Status

The project currently includes:

- Trained EfficientNet-B0 checkpoint
- Face-based image inference
- Frame-based video inference
- REAL/DEEPFAKE classification
- Confidence scoring
- Suspicious-frame reporting
- FastAPI backend
- Dashboard frontend
- Detection history
- Downloadable reports
- CUDA inference support
- Swagger API documentation
- Dataset preparation pipeline
- Face extraction pipeline

## 📜 Disclaimer

DeepGuard AI provides an AI-based prediction and should not be treated as definitive proof that media is authentic or manipulated.

Use the system responsibly and combine automated results with appropriate human review when making important decisions.
