from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class TaskStatus(StrEnum):
    queued = "queued"
    processing = "processing"
    success = "success"
    failed = "failed"


class PredictAccepted(BaseModel):
    task_id: str
    status: TaskStatus = TaskStatus.queued


class Prediction(BaseModel):
    class_name: str = Field(alias="class")
    confidence: float


class Detection(BaseModel):
    class_name: str = Field(alias="class")
    confidence: float
    bbox: tuple[int, int, int, int]


class TaskResult(BaseModel):
    task_id: str
    status: TaskStatus
    model_id: str | None = None
    result_type: Literal["classification", "detection"] | None = None
    prediction: Prediction | None = None
    detections: list[Detection] | None = None
    error: str | None = None
