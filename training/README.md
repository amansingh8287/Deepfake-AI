# Training

This directory provides a real training/evaluation pipeline shell for public datasets such as FaceForensics++, Celeb-DF, and DFDC.

Expected layout example:

```text
data/
  faceforensics/
    real/
      sample1.jpg
    fake/
      sample2.jpg
```

Run:

```bash
python train.py
python evaluate.py
```

Do not automatically download datasets. Prepare them manually according to licensing terms.

