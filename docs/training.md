# Training

Recommended public datasets:

- FaceForensics++
- Celeb-DF
- DFDC

Suggested workflow:

1. Extract face crops or aligned facial frames.
2. Split into train/validation/test sets.
3. Train EfficientNet or Xception-based classifiers.
4. Evaluate using accuracy, precision, recall, F1, ROC-AUC, and confusion matrix.
5. Save the best checkpoint into `models/`.

