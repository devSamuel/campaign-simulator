.PHONY: up down build migrate test lint

up:
	docker compose up --build -d

down:
	docker compose down -v

build:
	docker compose build

migrate:
	docker compose run --rm api alembic upgrade head

test:
	docker compose run --rm api pytest tests/unit/ -v 2>&1

test-integration:
	docker compose run --rm api pytest tests/integration/ -v 2>&1

lint:
	ruff check backend/src/ backend/tests/
	mypy backend/src/ --ignore-missing-imports

shell:
	docker compose exec api bash

logs:
	docker compose logs -f api worker

worker-logs:
	docker compose logs -f worker

	
