# ForesightX Profile Service

This service owns user-specific financial context.

## Responsibilities

- store users and portfolio holdings in PostgreSQL
- compute total portfolio value
- fetch current prices from the data service
- expose user risk level
- apply portfolio updates for buy and sell actions

## API

- `GET /portfolio/{user_id}`
- `POST /api/v1/profile/create`
- `POST /portfolio/update`
- `GET /risk/{user_id}`
- `GET /health`

## Internal Layout

- `app/db/`: async SQLAlchemy models and session setup
- `alembic/`: schema migrations
- `app/controllers/`: HTTP error mapping
- `app/services/`: portfolio operations and data-service client
- `scripts/`: DB-related helper assets

## Configuration

This service is independently configured from `ForesightX-profile/.env`.

Key variables:

- `DATABASE_URL`: point this to the profile service's dedicated Neon database
- `DATA_SERVICE_URL`
- `SEED_DEMO_DATA=false` by default

Run the schema before starting the API:

```bash
alembic upgrade head
```

Demo seeding is now opt-in. Startup no longer injects sample users unless you explicitly enable it, and startup no longer uses `create_all`.
