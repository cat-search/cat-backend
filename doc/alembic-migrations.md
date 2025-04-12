# Alembic migrations

```shell
# Init alembic
alembic init -t generic  src/migrations
```

```shell
# Generate a migration with name new_migration
alembic revision --autogenerate -m new_migration
# Check migration
alembic upgrade head --sql
# Apply migrations from current to latest
alembic upgrade head
# List migrations
alembic history
```