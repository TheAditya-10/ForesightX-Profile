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
- `POST /portfolio/update`
- `GET /risk/{user_id}`
- `GET /health`

## Internal Layout

- `app/db/`: async SQLAlchemy models and session setup
- `app/controllers/`: HTTP error mapping
- `app/services/`: portfolio operations and data-service client
- `scripts/`: DB-related helper assets
