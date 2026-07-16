# traffic-gateway

Go service that is the public entry point for the system.

Current stub:

- `GET /health`;
- `POST /v1/predict` reverse proxy to `api-ingestion`;
- `GET /v1/tasks/{task_id}` reverse proxy to `api-ingestion`;
- `POST /v1/replay/{request_id}` placeholder.

Next research tasks:

- add `pgx` repository for request history;
- add goose migrations runner;
- persist request and response metadata;
- expose Prometheus metrics;
- implement replay from stored request body/reference.
