# inference-worker

Python worker that consumes inference tasks and writes task results.

Current stub:

- starts a small FastAPI health server on `9101`;
- consumes Redis list `inference:queue`;
- writes fake classification results into Redis.

Next research tasks:

- load active model from `model-registry/models.yaml`;
- add ONNX Runtime runner;
- implement preprocessing and postprocessing;
- support CPU/GPU fallback;
- persist final results in Postgres.
