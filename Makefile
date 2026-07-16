.PHONY: up down logs fmt

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

fmt:
	gofmt -w services/traffic-gateway
	python -m compileall services/api-ingestion services/inference-worker ml
