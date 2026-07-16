from typing import Any


class FakeModelRunner:
    model_id = "ailegato-fake-classifier-v0"

    def predict(self, task: dict[str, Any]) -> dict[str, Any]:
        # Deterministic fake result for the first end-to-end backend milestone.
        return {
            "task_id": task["task_id"],
            "status": "success",
            "model_id": self.model_id,
            "result_type": "classification",
            "prediction": {
                "class": "scratch",
                "confidence": 0.73,
            },
        }


class OnnxModelRunner:
    def __init__(self, model_path: str) -> None:
        self.model_path = model_path

    def predict(self, task: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("Connect ONNX Runtime after best.onnx is exported")
