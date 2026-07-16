"""
Training stub for the first classification baseline.

Students should replace TODO blocks with real PyTorch dataset, model, metrics and checkpoint code.
"""

from pathlib import Path

import yaml


def main() -> None:
    config_path = Path("ml/configs/classification_baseline.yaml")
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))

    raw_dir = Path(config["data"]["raw_dir"])
    classes = config["data"]["classes"]

    print("Training baseline is not implemented yet.")
    print(f"Expected data directory: {raw_dir}")
    print(f"Configured classes: {classes}")
    print("TODO: add dataset split, dataloaders, model, loss, optimizer and metrics.")


if __name__ == "__main__":
    main()
