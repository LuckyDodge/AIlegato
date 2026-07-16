import json
import os
import threading
import time

import uvicorn
from fastapi import FastAPI, Response
from redis import Redis

from app.model_runner import FakeModelRunner

app = FastAPI(title="inference-worker", version="0.1.0")
redis_client = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True)
runner = FakeModelRunner()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "inference-worker", "model_id": runner.model_id}


@app.get("/metrics")
def metrics() -> Response:
    return Response("inference_worker_stub_info 1\n", media_type="text/plain; version=0.0.4")


def worker_loop() -> None:
    while True:
        item = redis_client.brpop("inference:queue", timeout=5)
        if item is None:
            continue

        _, raw_payload = item
        task = json.loads(raw_payload)
        task_key = f"task:{task['task_id']}"
        redis_client.hset(task_key, "status", "processing")

        try:
            result = runner.predict(task)
            redis_client.hset(task_key, mapping={"status": "success", "result": json.dumps(result)})
        except Exception as exc:
            failed_result = {"task_id": task["task_id"], "status": "failed", "error": str(exc)}
            redis_client.hset(task_key, mapping={"status": "failed", "result": json.dumps(failed_result)})


def main() -> None:
    thread = threading.Thread(target=worker_loop, daemon=True)
    thread.start()
    time.sleep(0.1)
    uvicorn.run(app, host="0.0.0.0", port=9101)


if __name__ == "__main__":
    main()
