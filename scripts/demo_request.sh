#!/usr/bin/env bash
set -euo pipefail

IMAGE_PATH="${1:-}"
if [[ -z "$IMAGE_PATH" ]]; then
  echo "Usage: scripts/demo_request.sh path/to/image.jpg"
  exit 1
fi

curl -sS -X POST "http://localhost:8080/v1/predict" \
  -F "image=@${IMAGE_PATH}"
