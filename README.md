# KAD Arbitr Monitor — MVP scaffold

Telegram bot scaffold for tracking arbitration cases by INN.

## Included
- aiogram 3 polling bot: `/start`, `/add`, `/remove`, `/list`, `/settings`
- PostgreSQL + SQLAlchemy 2 async models
- Alembic initial migration
- Celery worker + Redis broker
- Russian INN checksum validation (10 and 12 digits), with tests
- `KadClient` interface and a deliberately disabled adapter
- Docker Compose for local development

## Important: KAD integration is intentionally disabled
This project does **not** call undocumented KAD endpoints, emulate private APIs,
bypass CAPTCHA, rotate proxies, or spoof sessions. `DisabledKadClient` raises
`ProviderNotConfigured`. Enable a real provider only after obtaining written
permission and documented access conditions, or use a licensed data provider.
The current worker logs this condition and does not pretend that a search ran.

## Quick start
1. Copy `.env.example` to `.env` and set `BOT_TOKEN`.
2. Run `docker compose up --build`.
3. In another terminal, apply migrations:
   `docker compose exec bot alembic upgrade head`
4. Open the bot and send `/start`.

The bot needs a valid Telegram bot token. PostgreSQL and Redis are started by
Compose. The bot stores one user's INNs separately from other users.

## Commands
- `/start` — consent notice and start
- `/add 7707083893` — add INN (10 or 12 digits)
- `/remove 7707083893` — remove INN
- `/list` — show your tracked INNs
- `/settings` — show notification schedule settings

Maximum: 50 INNs per Telegram user. Default schedule is 09:00 Europe/Moscow.
The scheduler/worker is a scaffold; until a permitted provider is configured,
no real KAD queries or case notifications are performed.

## Local tests
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
```

## Railway
Create a **new Railway project**, separate from the existing SOZD bot. Add:
- PostgreSQL
- Redis
- `bot` service from this repository, start command `python -m app.bot`
- `worker` service from this repository, start command `celery -A app.celery_app worker -l INFO`
- `beat` service from this repository, start command `celery -A app.celery_app beat -l INFO`

Set `BOT_TOKEN`, `DATABASE_URL`, and `REDIS_URL` in each service as applicable.
For Railway Postgres, use the private/internal connection string if supported.
Set `DATABASE_URL` in SQLAlchemy async format, e.g. `postgresql+asyncpg://...`.
Set `REDIS_URL` to the Railway Redis connection URL.

Do not put real 12-digit INNs or Telegram user data into a deployment until
the applicable Russian personal-data requirements (including localization),
provider terms, retention, deletion, and access controls have been reviewed.
Use synthetic data for initial Railway smoke tests.

## Before production
- obtain written confirmation for the permitted KAD access method, rate limits,
  and server-side automation terms, or integrate a licensed provider
- implement actual provider adapter against its published documentation
- complete case/event/document persistence and notification outbox
- implement user timezone editing, `/delete_me`, consent versioning, audit/retention
- add transactional idempotency and operational monitoring
- review 152-FZ/data localization and hosting location
