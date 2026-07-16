import json
import os
import uuid
from typing import Annotated

from fastapi import FastAPI, File, HTTPException, Response, UploadFile
from redis import Redis

from app.schemas import PredictAccepted, TaskResult, TaskStatus

app = FastAPI(title="api-ingestion", version="0.1.0")

redis_client = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "api-ingestion"}


@app.get("/metrics")
def metrics() -> Response:
    return Response("api_ingestion_stub_info 1\n", media_type="text/plain; version=0.0.4")


@app.post("/v1/predict", response_model=PredictAccepted)
async def predict(image: Annotated[UploadFile, File()]) -> PredictAccepted:
    if image.content_type is None or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image uploads are supported")

    task_id = str(uuid.uuid4())
    image_bytes = await image.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Image is empty")

    task_payload = {
        "task_id": task_id,
        "filename": image.filename,
        "content_type": image.content_type,
        "image_size": len(image_bytes),
    }

    # Stub storage: keep metadata in Redis until Postgres and MinIO repositories are implemented.
    redis_client.hset(f"task:{task_id}", mapping={"status": TaskStatus.queued.value, "payload": json.dumps(task_payload)})
    redis_client.lpush("inference:queue", json.dumps(task_payload))

    return PredictAccepted(task_id=task_id)


@app.get("/v1/tasks/{task_id}", response_model=TaskResult)
def get_task(task_id: str) -> TaskResult:
    raw = redis_client.hgetall(f"task:{task_id}")
    if not raw:
        raise HTTPException(status_code=404, detail="Task not found")

    status = TaskStatus(raw.get("status", TaskStatus.queued.value))
    result = raw.get("result")
    if result:
        return TaskResult.model_validate(json.loads(result))

    return TaskResult(task_id=task_id, status=status)
