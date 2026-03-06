# Marketing Automation Platform

A full-stack marketing campaign automation platform built with Domain-Driven Design (DDD). It lets you create campaigns, attach creatives and audience segments, define performance rules, and run simulations that stream results in real time.

## Tech Stack

### Backend
| Layer | Technology |
|---|---|
| API | FastAPI (Python 3.11+) |
| Task queue | Celery 5 + RabbitMQ broker |
| Streaming | Redis pub/sub + Server-Sent Events |
| Database | PostgreSQL 16 + SQLAlchemy 2 (async) |
| Migrations | Alembic |
| Validation | Pydantic v2 |

### Frontend
| Layer | Technology |
|---|---|
| Framework | Next.js 15 (App Router) |
| UI | React 19 + Tailwind CSS |
| Data fetching | TanStack Query v5 |
| Charts | Recharts |

### Infrastructure
| Component | Technology |
|---|---|
| Container orchestration | Docker Compose |
| Reverse proxy | Nginx |
| Message broker | RabbitMQ 3.13 |
| Cache / pub-sub | Redis 7 |

---

## Architecture

The backend follows **Domain-Driven Design** with a single bounded context: `campaign`.

```
backend/
  src/
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
        commands/      # CQRS command handlers (create campaign, run simulation)
        queries/       # get_campaign, list_campaigns
        dtos/          # Pydantic DTOs for API layer
      infrastructure/
        persistence/   # SQLAlchemy models + PostgresCampaignRepository
        messaging/     # SimulationEventPublisher (Redis pub/sub)
        tasks/         # simulate_campaign_task (Celery)
    api/
      v1/
        campaigns.py   # Campaign CRUD (create, list, get)
        simulations.py # POST to trigger simulation, GET to poll result
        sse.py         # GET /{campaign_id}/simulate/{job_id}/stream — SSE stream
  tests/
    unit/domain/       # Pure domain tests, no DB/infra dependencies
    integration/       # httpx tests against live stack
  alembic/             # Database migrations
  Dockerfile
  pyproject.toml

frontend/
  src/
    app/               # Next.js App Router pages
    components/        # UI components (builder, simulation, campaigns)
    hooks/             # TanStack Query hooks for API interaction
    lib/               # API client, query keys, types
```

### Campaign lifecycle

```
DRAFT --> SIMULATING --> ACTIVE
                     --> PAUSED  (rule triggered)
```

### Simulation flow

1. `POST /api/v1/campaigns/{id}/simulate` creates a `SimulationJob` (status=PENDING) and dispatches a Celery task.
2. The Celery worker runs `SimulationEngine.run()` — 24 hourly steps, seeded by campaign UUID for reproducibility.
3. Each step is evaluated by `RuleEvaluatorService` and published to Redis pub/sub (`sim:{job_id}`).
4. On completion the rule action is applied (`PAUSE_CAMPAIGN`, `REDUCE_BUDGET 20%`, or `SEND_ALERT`), and the result is cached in Redis (TTL 1 h).
5. The frontend consumes steps in real time via SSE: `GET /api/v1/campaigns/{id}/simulate/{job_id}/stream`.

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose v2
- Node.js 20+ (only needed for local frontend development outside Docker)

---

## Quick Start

### 1. Clone the repo

```bash
git clone <repo-url>
cd marketing_automation
```

### 2. Bootstrap

```bash
make setup
```

This single command copies `.env.example` → `.env`, builds and starts all services (PostgreSQL, RabbitMQ, Redis, FastAPI, Celery worker, Nginx, Next.js), and runs database migrations.

The platform is now running. Open `http://localhost:3000` in your browser.

---

## Available Commands

```bash
make setup            # First-time setup: copy .env, start services, run migrations
make up               # Build and start all services (detached)
make down             # Stop and remove all containers + volumes
make build            # Build images without starting
make migrate          # Run Alembic migrations (upgrade head)
make test             # Run unit tests (no running services required)
make test-integration # Run integration tests (requires running stack)
make lint             # Ruff + mypy
make logs             # Tail API and worker logs
make shell            # Open a bash shell inside the API container
```

---

## API Reference

Interactive docs are available at `http://localhost:8000/docs` (Swagger UI) when the stack is running.

### Campaigns

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/campaigns` | List all campaigns |
| `POST` | `/api/v1/campaigns` | Create a campaign (with creatives, audience, and rule in one request) |
| `GET` | `/api/v1/campaigns/{id}` | Get campaign detail |

### Simulations

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/campaigns/{id}/simulate` | Trigger a simulation |
| `GET` | `/api/v1/campaigns/{id}/simulate/{job_id}` | Poll simulation result |
| `GET` | `/api/v1/campaigns/{id}/simulate/{job_id}/stream` | SSE stream of simulation steps |

---

## Testing

```bash
# Unit tests (no running services required)
make test

# Integration tests (requires running docker-compose stack)
make test-integration

# Single file inside the container
docker compose run --rm api pytest tests/unit/domain/test_campaign_aggregate.py -v
```

Unit tests cover pure domain logic and have no database or infrastructure dependencies. Integration tests use `httpx` against the live stack.

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | PostgreSQL async DSN | `postgresql+asyncpg://marketing:marketing_secret@localhost:5432/marketing_automation` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
| `CELERY_BROKER_URL` | RabbitMQ AMQP URL | `amqp://guest:guest@localhost:5672//` |
| `CELERY_RESULT_BACKEND` | Celery result store (Redis) | `redis://localhost:6379/1` |
| `APP_ENV` | `development` / `production` | `development` |
| `APP_DEBUG` | Enable debug mode | `true` |
| `APP_PORT` | API server port | `8000` |

---

## Project Structure (top level)

```
.
├── backend/              # Python API, Celery worker, domain logic
│   ├── src/              # Application source code
│   ├── tests/            # Unit + integration tests
│   ├── alembic/          # Database migrations
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/             # Next.js frontend
│   └── src/
├── nginx/                # Nginx reverse proxy config
├── docker-compose.yml
├── Makefile
└── .env.example
```

---

## Engineering Notes

### Why this stack and architecture

**DDD + CQRS**
Business rules — budget validation, performance rule evaluation, simulation logic — live entirely in the domain layer, with no dependency on HTTP or the database. Swapping FastAPI for gRPC, or PostgreSQL for another database, requires zero changes to domain code. Separate command and query handlers (CQRS) keep writes and reads independently testable and independently scalable.

**FastAPI + Pydantic v2**
The API is async-native (asyncio + asyncpg), so it never blocks a thread on I/O. This matters most for SSE, where hundreds of open connections can be held with minimal resource cost. Pydantic v2 validates every request body and auto-generates the OpenAPI schema at zero extra effort.

**Celery + RabbitMQ**
Simulations are long-running. Offloading them to Celery means the API returns immediately with a `job_id` (202 Accepted) — users never wait on a slow HTTP response. RabbitMQ provides durable, acknowledged delivery: tasks survive API restarts and are never silently dropped.

**Redis — two roles**
- **Pub/sub** (`sim:{job_id}`): the Celery worker publishes each simulation step here; the API subscribes and fans it out to all SSE clients watching that job — no DB polling required.
- **Result cache** (`sim_result:{job_id}`, TTL 1 h): clients that connect after the simulation finishes can still retrieve the full result without touching PostgreSQL.

**SSE instead of WebSockets**
Simulation output is strictly server → client. SSE works over plain HTTP/1.1 through any reverse proxy or CDN without upgrade negotiation, and is natively supported by every modern browser via `EventSource`. WebSockets would add complexity for no benefit here.

**Next.js 15 + TanStack Query**
TanStack Query handles request deduplication, caching, stale-while-revalidate, and loading/error states out of the box — no custom global state or Redux needed. Next.js App Router enables server-side rendering for the campaign list and detail pages, improving initial load and SEO.

---

### Frontend → Backend communication

Two channels are used, each for a different purpose.

**REST over HTTP (CRUD + triggering simulations)**

```
Browser → Nginx (:80) → FastAPI (:8000) → PostgreSQL
```

1. `NEXT_PUBLIC_API_URL` (e.g. `http://localhost:8000/api/v1`) is the base URL baked into the Next.js build.
2. [`frontend/src/lib/api.ts`](frontend/src/lib/api.ts) — `apiFetch<T>()` sets `Content-Type: application/json`, throws on non-2xx, and deserializes the response. Every API call (`listCampaigns`, `createCampaign`, `runSimulation`, …) is a thin wrapper around it.
3. [`frontend/src/hooks/`](frontend/src/hooks/) — TanStack Query hooks wrap those functions, providing caching, background refetch, and automatic cache invalidation after mutations (e.g. `useRunSimulation` invalidates the campaign query on success).

**Server-Sent Events (real-time simulation steps)**

```
Browser EventSource → Nginx → FastAPI SSE endpoint → Redis pub/sub ← Celery worker
```

1. [`frontend/src/hooks/useSimulationStream.ts`](frontend/src/hooks/useSimulationStream.ts) opens a native `EventSource` to `/api/v1/campaigns/{id}/simulate/{jobId}/stream`.
2. It listens for three named events:
   - `connected` — confirms the SSE connection is live.
   - `step` — one of 24 hourly data payloads; each is appended to a state array that drives the Recharts chart in real time.
   - `completed` — signals the simulation is done; the `EventSource` is closed.
3. On network error or `completed`, the cleanup function in `useEffect` closes the connection automatically.

---

### What i woull add if i had more time and in Production roadmap

| Area | Current (dev) | What to add in production |
|---|---|---|
| **Authentication** | None | JWT issued on login (FastAPI Users or Auth0). All `/api/v1/*` routes protected with `Depends(get_current_user)`. Bearer token sent from the frontend. Campaigns scoped to `owner_id`. |
| **HTTPS / TLS** | HTTP on `:80` | TLS termination at Nginx (Let's Encrypt or ACM). HTTP → HTTPS redirect enforced. |
| **Secrets** | `.env` file | AWS Secrets Manager / Vault / Doppler. No credentials in version control. |
| **CI/CD** | Manual `make` commands | GitHub Actions: lint → unit tests → build & push Docker images → deploy. Integration tests run against an ephemeral DB in the pipeline. |
| **Testing** | Unit + basic integration | Playwright e2e tests for the campaign builder UI. Property-based tests (Hypothesis) on domain value objects. Load tests (k6 / Locust) against the simulation endpoint. ≥80% coverage gate in CI. |
| **Scalability** | 1 API container, 1 worker | N API replicas behind a load balancer (ECS / Kubernetes). Celery workers scaled independently by queue depth. PostgreSQL read replica for query handlers. PgBouncer for connection pooling. Redis Cluster for pub/sub at scale. |
| **Observability** | Container stdout logs | Structured JSON logging (structlog). Distributed tracing (OpenTelemetry → Jaeger / Datadog). Metrics (Prometheus + Grafana). Celery monitoring via Flower or Datadog APM. |
| **Database** | Single Postgres instance | Managed service (RDS / Cloud SQL) with point-in-time recovery. Migrations run and verified in CI before every deploy. |
