"""
ONNX export stub.

Use this after a PyTorch checkpoint exists. The inference-worker should consume the exported model.
"""

from pathlib import Path


def main() -> None:
    output_path = Path("models/ailegato-classifier-baseline-v1/best.onnx")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    print("ONNX export is not implemented yet.")
    print(f"Expected output path: {output_path}")
    print("TODO: load checkpoint, create dummy input and call torch.onnx.export.")


if __name__ == "__main__":
    main()
