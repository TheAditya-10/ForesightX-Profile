# Profile Services

Business logic for user financial context lives here.

## Modules

- `market_client.py`: calls the data service for live prices
- `profile_service.py`: computes portfolio totals, validates trades, and updates holdings

## Design Note

The service pulls live prices at read time so orchestration gets current exposure numbers instead of stale book values.
