# AIlegato

Учебный микросервисный проект для обнаружения дефектов на фото стальных пластин.

Цель репозитория - дать каждому участнику отдельную зону исследования и разработки: Go traffic gateway, Go core backend, Python inference/ML pipeline и инфраструктура вокруг модели. На первом этапе система должна проходить end-to-end с fake-result, без реальной нейросети. После этого fake inference заменяется на ONNX-модель, обученную на собственных фотографиях и разметке команды.

## Архитектура

```text
client
  -> traffic-gateway
  -> api-ingestion
  -> redis queue
  -> inference-worker
  -> postgres/minio/model-registry
```

Основной сценарий:

1. Клиент отправляет изображение на `POST /v1/predict`.
2. `traffic-gateway` добавляет `X-Request-ID`, логирует запрос и проксирует его в `api-ingestion`.
3. `api-ingestion` валидирует файл, создает `task_id`, сохраняет metadata и ставит задачу в очередь.
4. `inference-worker` забирает задачу и пока возвращает fake-result.
5. Клиент проверяет результат через `GET /v1/tasks/{task_id}`.

## Быстрый старт

```bash
cp .env.example .env
docker compose up --build
```

Проверки после запуска:

```bash
curl http://localhost:8080/health
curl http://localhost:8000/health
curl http://localhost:9101/health
```

## Роли

- Участник A, Go traffic backend: `services/traffic-gateway`, gateway DB migrations, replay, logs, Prometheus metrics.
- Участник B, Go core backend: целевой `api-ingestion` на Go, task status API, PostgreSQL, MinIO, queue publisher, backend tests.
- Участник C, Python inference and ML: `services/inference-worker`, `ml`, `model-registry`, preprocessing/postprocessing, training reports, ONNX export.

## Этапы

- Этап 0: пустая система запускается, у каждого сервиса есть `/health`.
- Этап 1: end-to-end с fake-result.
- Этап 2: обучение baseline-модели на собственных фото и экспорт в ONNX.
- Этап 3: production-like детали: replay, timeouts, metrics, logs, demo-сценарий.

Подробности контрактов лежат в `docs/api-contracts.md`, ML-план - в `docs/ml-research.md`.
