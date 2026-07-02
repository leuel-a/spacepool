# Spacepool

A booking platform for shared resources — desks, meeting rooms, and equipment — built for co-working spaces and small offices that need to manage who's using what, and when.

Admins define spaces and resources; members book time slots, manage credits, and get notified when bookings are confirmed, conflict, or auto-expire.

## Stack

**Backend**
- FastAPI
- SQLAlchemy 2.0 (async) + Alembic for migrations
- PostgreSQL
- Pydantic v2 for schemas/validation
- JWT auth (OAuth2PasswordBearer) with refresh tokens
- APScheduler (or FastAPI `BackgroundTasks`) for auto-expiring unconfirmed bookings
- Redis (optional) for slot-locking during booking to prevent double-booking race conditions

**Frontend**
- React + TypeScript
- Vite
- TanStack Query for server state
- Tailwind CSS + shadcn/ui
- React Hook Form + Zod for booking/resource forms
- A custom weekly/daily calendar grid component for slot selection (no external calendar lib — this is the core UI challenge of the project)

**Infra**
- Docker Compose (api, web, postgres, redis)
- pnpm or npm workspaces if monorepo; otherwise two standalone repos/folders

## Why this project

The core complexity isn't CRUD — it's **correctness under contention**. Two members can try to book the same desk in the same slot at the same time, and the system has to handle that cleanly instead of silently letting both succeed. That, plus role-based access, a credits system, and scheduled cleanup jobs, makes this comparable in scope to a typical event-management platform, but the hard parts are different: concurrency and time-range logic instead of payment integration and content CRUD.

## Core features

### Auth & roles
- Email/password signup and login, JWT access + refresh tokens
- Two roles: `admin` (manages spaces, resources, members) and `member` (books resources)
- Admins can invite members to their organization/space

### Spaces & resources
- An **organization** owns one or more **spaces** (e.g. "Downtown Office")
- A space contains **resources** (desks, rooms, equipment) with attributes like capacity, type, and availability windows (e.g. closed on weekends)

### Booking
- Members view a resource's calendar as a grid of time slots
- Selecting a slot opens a booking form; submitting checks for overlap server-side before committing
- Overlap checks use either a DB-level exclusion constraint (Postgres `tstzrange` + `EXCLUDE USING gist`) or a short-lived Redis lock during the check-then-insert window
- Bookings can be cancelled up until a configurable cutoff (e.g. 1 hour before start)

### Credits
- Each member has a monthly credit allowance
- Booking a resource deducts credits based on resource type and duration
- Cancelling within the allowed window refunds credits
- Admins can adjust member balances manually

### Background jobs
- Unconfirmed bookings (if you add a confirmation step) auto-expire after N minutes, releasing the slot
- Daily/weekly digest job (optional) summarizing upcoming bookings per member

### Notifications
- In-app notifications (polled or via a simple SSE endpoint) for booking confirmed, booking cancelled, slot conflict
- Optional email via SMTP or a transactional provider

## Data model (high level)

```
User (id, email, hashed_password, role, org_id, credits_balance)
Organization (id, name)
Space (id, org_id, name, timezone)
Resource (id, space_id, name, type, capacity, credit_cost_per_hour)
Booking (id, resource_id, user_id, start_time, end_time, status, created_at)
Notification (id, user_id, type, payload, read_at)
```

`Booking.status`: `confirmed | cancelled | expired`

## API surface (sketch)

```
POST   /auth/signup
POST   /auth/login
POST   /auth/refresh

GET    /spaces
POST   /spaces                  (admin)
GET    /spaces/{id}/resources
POST   /spaces/{id}/resources   (admin)

GET    /resources/{id}/availability?from=&to=
POST   /bookings                # validates overlap server-side
DELETE /bookings/{id}
GET    /bookings/me

GET    /notifications
POST   /notifications/{id}/read
```

## Project structure

```
spacepool/
├── apps/
│   ├── api/
│   │   ├── app/
│   │   │   ├── models/
│   │   │   ├── schemas/
│   │   │   ├── routers/
│   │   │   ├── services/        # booking conflict logic, credit logic
│   │   │   ├── jobs/             # APScheduler jobs
│   │   │   └── main.py
│   │   ├── alembic/
│   │   └── tests/
│   └── web/
│       ├── src/
│       │   ├── components/
│       │   │   └── calendar/     # the custom slot-grid component
│       │   ├── pages/
│       │   ├── hooks/
│       │   └── lib/
│       └── vite.config.ts
├── docker-compose.yml
└── README.md
```

## Getting started

```bash
# backend
cd apps/api
cp .env.example .env
docker compose up -d postgres redis
alembic upgrade head
uvicorn app.main:app --reload

# frontend
cd apps/web
npm install
npm run dev
```

## Stretch goals

- Recurring bookings (e.g. "every Monday 9–11am")
- Waitlist for fully-booked resources
- Usage analytics dashboard per space (peak hours, most-booked resources)
- iCal export for personal calendars
