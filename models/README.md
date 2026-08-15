# Models

Place trained PyTorch checkpoints in this directory.

Supported naming examples:

- `deepguard_efficientnet.pt`
- `deepguard_xception.pth`

Update `DEEPGUARD_MODEL_PATH` in `.env` to point to the checkpoint you want the backend to load.

If no checkpoint is present, DeepGuard AI runs in clearly labeled `baseline/demo` mode using deterministic computer-vision heuristics plus optional face-aware scoring.

