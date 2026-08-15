# Architecture

DeepGuard AI uses a FastAPI backend, SQLite persistence, a face-aware deepfake inference pipeline, and a React dashboard frontend.

Core backend flow:

1. Validate upload metadata and file size.
2. Save to a temporary uploads directory.
3. Detect face regions using MediaPipe or OpenCV Haar cascades.
4. Run either a trained PyTorch model or a deterministic baseline heuristic.
5. Aggregate scores, save the detection record, and generate PDF reports on demand.

Video flow uses configurable frame sampling instead of full-frame exhaustive analysis.

