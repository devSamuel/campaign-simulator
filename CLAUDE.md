# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Start all services (PostgreSQL, RabbitMQ, Redis, API, Celery worker, Nginx)
make up

# Stop and remove volumes
make down

# Run database migrations
make migrate

# Run tests
make test

# Run a single test file
pytest tests/unit/domain/test_campaign_aggregate.py -v

# Lint (ruff + mypy)
make lint

# View API + worker logs
make logs

# Open a shell in the running API container
make shell
```

Copy `.env.example` to `.env` before first run. Default credentials match the docker-compose service definitions.

## Architecture

This is a **Domain-Driven Design (DDD)** application with a single bounded context: `campaign`.

### Layer structure (inside `src/`)

```
shared/
  domain/          # Base classes: Entity, AggregateRoot, ValueObject, DomainEvent
  infrastructure/  # Settings, DB engine, Redis client, Celery app

campaign/
  domain/
    entities/      # Campaign (aggregate root), Creativity, AudienceSegment
    value_objects/ # Budget, CampaignStatus, PerformanceRule, MetricType
    services/      # SimulationEngine (24-step random-walk), RuleEvaluatorService
    events/        # CampaignCreated, RuleDefined, SimulationStarted
    repositories/  # ICampaignRepository interface
  application/
    commands/      # CQRS command handlers (create, add creativity, set segment, define rule, run simulation)
    queries/       # get_campaign, list_campaigns
    dtos/          # Pydantic DTOs for API layer
  infrastructure/
    persistence/   # SQLAlchemy models + PostgresCampaignRepository
    messaging/     # SimulationEventPublisher (Redis pub/sub)
    tasks/         # simulate_campaign_task (Celery)

api/
  v1/
    campaigns.py   # CRUD + subresource endpoints
    simulations.py # POST to trigger simulation, GET to poll result
    sse.py         # GET /{campaign_id}/simulate/{job_id}/stream — SSE stream
```

### Key flows

**Campaign lifecycle:** DRAFT → SIMULATING → ACTIVE or PAUSED (rule triggered)

**Simulation flow:**
1. `POST /api/v1/campaigns/{id}/simulate` → `RunSimulationHandler` creates a `SimulationJobModel` (status=PENDING), calls `campaign.start_simulation()`, dispatches `simulate_campaign_task` via Celery.
2. Celery worker runs `SimulationEngine.run()` (24 hourly steps, seeded by campaign UUID for reproducibility), evaluates `PerformanceRule` each step via `RuleEvaluatorService`.
3. Each step is streamed to clients via **Redis pub/sub** (channel `sim:{job_id}`).
4. On completion, `campaign.complete_simulation()` applies the rule action (PAUSE_CAMPAIGN, REDUCE_BUDGET 20%, or SEND_ALERT), persists campaign state, caches result in Redis (`sim_result:{job_id}`, TTL=1h).
5. Clients consume via SSE: `GET /api/v1/campaigns/{id}/simulate/{job_id}/stream`.

**Domain events** are collected on the aggregate (`pull_events()`) but not yet dispatched to an external bus — the `SimulationEventPublisher` publishes directly to Redis pub/sub instead.

### Infrastructure

- **Database:** PostgreSQL + SQLAlchemy async (asyncpg driver). Migrations via Alembic (`alembic/versions/`).
- **Task queue:** Celery with RabbitMQ broker, Redis result backend.
- **Streaming:** Redis pub/sub → Server-Sent Events.
- **API:** FastAPI mounted at `/api/v1`, plus `/health`. Nginx reverse-proxies port 80 → 8000.
- **Settings:** `src/shared/infrastructure/settings.py` via `pydantic-settings`; reads from `.env`.

### Testing

- `tests/unit/domain/` — pure domain tests, no DB/infra dependencies.
- `tests/integration/` — uses `httpx` + live services (requires running docker-compose).
- `asyncio_mode = "auto"` is set in `pyproject.toml`, so `async def test_*` works without decorators.
