# AIlegato

Учебный микросервисный проект для обнаружения дефектов на фото стальных пластин.

Цель репозитория - дать каждому участнику отдельную зону исследования и разработки: Go traffic gateway, Go core backend, Python inference/ML pipeline и инфраструктура вокруг модели.

## Архитектура

```text
client
  -> traffic-gateway
  -> api-ingestion
  -> redis queue
  -> inference-worker
  -> postgres/minio/model-registry
```
