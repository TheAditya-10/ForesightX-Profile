# Profile App Package

This package contains the runtime code for the profile service.

The flow is:

1. route receives validated input
2. controller handles HTTP translation
3. service mutates or reads portfolio state
4. DB layer persists user and position records
