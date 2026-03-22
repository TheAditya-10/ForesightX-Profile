# Profile Database Layer

This directory contains the persistence model for the profile service.

## Files

- `base.py`: SQLAlchemy declarative base
- `models.py`: `users` and `portfolio` table models
- `session.py`: engine, session factory, schema initialization, and demo seeding

## Why This Layer Exists

The service needs a dedicated persistence boundary so business logic does not directly manage engine setup or DDL concerns.
