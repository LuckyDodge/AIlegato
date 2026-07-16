# ML Workspace

This folder is for dataset checks, training experiments, metrics and ONNX export.

Suggested order:

1. Collect photos into `data/raw`.
2. Decide class names and write them into `ml/configs/classification_baseline.yaml`.
3. Split data into train/validation/test.
4. Train a simple classification baseline.
5. Export `best.onnx`.
6. Update `model-registry/models.yaml`.
7. Replace fake runner in `services/inference-worker`.

YOLO/detection should be a second step unless bounding-box labels already exist.
