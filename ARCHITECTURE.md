# Architecture

## 1. System Overview

```mermaid
graph TD
    Browser["Browser / Client"]

    subgraph Docker Compose
        Nginx["Nginx\n:80"]
        Frontend["Next.js Frontend\n:3000"]
        API["FastAPI\n:8000"]
        Worker["Celery Worker"]
        PG["PostgreSQL\n:5432"]
        RMQ["RabbitMQ\n:5672"]
        Redis["Redis\n:6379"]
    end

    Browser -->|HTTP| Nginx
    Browser -->|SSE stream| Nginx
    Nginx -->|reverse proxy| API
    Nginx -->|static / SSR| Frontend
    Frontend -->|REST + SSE| API

    API -->|async SQL| PG
    API -->|publish task| RMQ
    API -->|pub/sub & cache| Redis

    Worker -->|consume task| RMQ
    Worker -->|async SQL| PG
    Worker -->|publish steps| Redis
```

---

## 2. Backend Layer Structure — `backend/src/` (DDD)

```mermaid
graph TD
    subgraph API Layer
        EP["FastAPI Endpoints\ncampaigns · simulations · sse"]
    end

    subgraph Application Layer
        CMD["Command Handlers\nCreateCampaignHandler\nRunSimulationHandler"]
        QRY["Query Handlers\nGetCampaignHandler\nListCampaignsHandler"]
        DTO["DTOs\nCampaignDTO · SimulationResultDTO"]
    end

    subgraph Domain Layer
        AGG["Campaign (Aggregate Root)"]
        ENT["Entities\nCreativity · AudienceSegment"]
        VO["Value Objects\nBudget · CampaignStatus\nPerformanceRule · MetricType"]
        SVC["Domain Services\nSimulationEngine\nRuleEvaluatorService"]
        EVT["Domain Events\nCampaignCreated · RuleDefined\nSimulationStarted"]
        REPO["Repository Interface\nICampaignRepository"]
    end

    subgraph Infrastructure Layer
        PG_REPO["PostgresCampaignRepository\n(SQLAlchemy async)"]
        TASKS["Celery Task\nsimulate_campaign_task"]
        PUB["SimulationEventPublisher\n(Redis pub/sub)"]
    end

    EP --> CMD
    EP --> QRY
    EP --> DTO
    CMD --> AGG
    QRY --> REPO
    AGG --> ENT
    AGG --> VO
    AGG --> EVT
    CMD --> SVC
    REPO --> PG_REPO
    CMD --> TASKS
    TASKS --> PUB
```

---

## 3. Campaign Lifecycle

```mermaid
stateDiagram-v2
    [*] --> DRAFT : POST /campaigns

    DRAFT --> SIMULATING : POST /campaigns/{id}/simulate

    SIMULATING --> ACTIVE : simulation completes\n(rule not triggered)
    SIMULATING --> PAUSED : simulation completes\n(rule triggered → PAUSE_CAMPAIGN)
    SIMULATING --> ACTIVE : rule triggered → SEND_ALERT\nor REDUCE_BUDGET
```

---

## 4. Simulation Flow

```mermaid
sequenceDiagram
    actor Client
    participant API
    participant DB as PostgreSQL
    participant RMQ as RabbitMQ
    participant Worker as Celery Worker
    participant Redis

    Client->>API: POST /campaigns/{id}/simulate
    API->>DB: INSERT SimulationJob (PENDING)
    API->>DB: campaign.start_simulation()
    API->>RMQ: dispatch simulate_campaign_task
    API-->>Client: 202 { job_id, stream_url, poll_url }

    Client->>API: GET /campaigns/{id}/simulate/{job_id}/stream (SSE)
    API->>Redis: SUBSCRIBE sim:{job_id}

    loop 24 hourly steps
        Worker->>Worker: SimulationEngine.run() step N
        Worker->>Worker: RuleEvaluatorService.evaluate()
        Worker->>Redis: PUBLISH sim:{job_id} step data
        Redis-->>API: push step event
        API-->>Client: SSE event (step N)
    end

    Worker->>DB: apply rule action\n(PAUSE / REDUCE_BUDGET / SEND_ALERT)
    Worker->>DB: UPDATE campaign status
    Worker->>Redis: SET sim_result:{job_id} (TTL 1h)
    Worker->>Redis: PUBLISH sim:{job_id} DONE

    API-->>Client: SSE event (done)
```

---

## 5. Request Flow — Create Campaign

```mermaid
sequenceDiagram
    actor Client
    participant API as FastAPI
    participant CMD as CreateCampaignHandler
    participant Domain as Campaign Aggregate
    participant DB as PostgreSQL

    Client->>API: POST /api/v1/campaigns\n{ name, budget, creativities, audience, rule }
    API->>CMD: CreateCampaignCommand
    CMD->>Domain: Campaign.create()\n+ add creativities\n+ set audience\n+ define rule
    Domain-->>CMD: Campaign + domain events
    CMD->>DB: INSERT campaign, creativities,\naudienceSegment, performanceRule
    CMD-->>API: Campaign entity
    API-->>Client: 201 CampaignDTO
```

---

## 6. Data Model

```mermaid
erDiagram
    campaigns {
        uuid id PK
        varchar name
        varchar status
        numeric budget_amount
        varchar budget_currency
        timestamp created_at
        timestamp updated_at
    }

    creativities {
        uuid id PK
        uuid campaign_id FK
        varchar name
        varchar type
        text asset_url
    }

    audience_segments {
        uuid id PK
        uuid campaign_id FK
        varchar name
        int age_min
        int age_max
        text[] locations
        text[] interests
        text[] device_types
    }

    performance_rules {
        uuid id PK
        uuid campaign_id FK
        varchar metric
        varchar operator
        float threshold
        varchar action
    }

    simulation_jobs {
        uuid id PK
        uuid campaign_id FK
        varchar status
        timestamp created_at
        timestamp updated_at
    }

    campaigns ||--o{ creativities : "has"
    campaigns ||--o| audience_segments : "has"
    campaigns ||--o| performance_rules : "has"
    campaigns ||--o{ simulation_jobs : "has"
```
