# api-ingestion

FastAPI service for input validation and task creation.

Current stub:

- `GET /health`;
- `POST /v1/predict` accepts an uploaded image;
- creates `task_id`;
- stores task metadata in Redis;
- pushes a task into `inference:queue`;
- `GET /v1/tasks/{task_id}` reads status/result from Redis.

Next research tasks:

- replace Redis metadata with SQLAlchemy repositories;
- store image bytes in MinIO;
- add Alembic migrations;
- add validation for image size and supported formats;
- add tests with pytest.
