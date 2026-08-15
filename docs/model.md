# Model

DeepGuard AI supports two inference modes:

1. `trained`
   Load a `.pt` or `.pth` checkpoint from `models/` using `DEEPGUARD_MODEL_PATH`.
2. `baseline`
   Use deterministic visual heuristics when no checkpoint is available.

The baseline mode is intentionally labeled as a development/demo fallback and should not be presented as benchmarked detector accuracy.

