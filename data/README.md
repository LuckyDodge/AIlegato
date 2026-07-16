# Data

This project is expected to use photos collected by the team.

Recommended local layout:

```text
data/
  raw/
    clean/
    scratch/
    dent/
  processed/
  labels/
    images/
    labels/
```

Rules:

- Do not commit raw photos unless the team explicitly decides to version a tiny sample set.
- Keep train/validation/test split reproducible.
- Start with classification if there are no bounding boxes.
- Move to YOLO only after the team creates or imports bounding-box labels.
