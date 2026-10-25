"""Run against a real Postgres: readiness and ORM <-> migration drift."""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import Connection, inspect
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.core.config import Settings
from app.main import create_app
from app.models import AppMeta, Base

pytestmark = pytest.mark.integration


async def test_ready_succeeds_against_real_database(migrated_url: str) -> None:
    settings = Settings(
        _env_file=None,  # type: ignore[call-arg]
        env="test",
        database_url=migrated_url,  # type: ignore[arg-type]
        secret_key="test-secret",  # type: ignore[arg-type]
    )
    application = create_app(settings)
    async with application.router.lifespan_context(application):
        transport = ASGITransport(app=application)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


async def test_orm_can_round_trip_a_row(engine: AsyncEngine) -> None:
    async with AsyncSession(engine) as session:
        session.add(AppMeta(key="schema", value="v1"))
        await session.commit()
        stored = await session.get(AppMeta, "schema")
        assert stored is not None
        assert stored.value == "v1"
        assert stored.created_at is not None
        await session.delete(stored)
        await session.commit()


def _diff_schema(connection: Connection) -> list[str]:
    """Return human-readable differences between the ORM metadata and the database."""
    inspector = inspect(connection)
    dialect = postgresql.dialect()
    problems: list[str] = []
    db_tables = set(inspector.get_table_names())
    orm_tables = set(Base.metadata.tables)
    problems += [f"table only in DB: {name}" for name in sorted(db_tables - orm_tables)]
    problems += [
        f"table only in ORM: {name}" for name in sorted(orm_tables - db_tables)
    ]
    for name in sorted(orm_tables & db_tables):
        table = Base.metadata.tables[name]
        db_cols = {col["name"]: col for col in inspector.get_columns(name)}
        for column in table.columns:
            if column.name not in db_cols:
                problems.append(f"{name}.{column.name}: only in ORM")
                continue
            db_col = db_cols[column.name]
            if column.nullable != db_col["nullable"]:
                problems.append(f"{name}.{column.name}: nullable differs")
            orm_type = column.type.compile(dialect=dialect).lower()
            db_type = db_col["type"].compile(dialect=dialect).lower()
            if orm_type != db_type:
                problems.append(f"{name}.{column.name}: {orm_type} != {db_type}")
        problems += [
            f"{name}.{col}: only in DB"
            for col in sorted(set(db_cols) - set(table.c.keys()))
        ]
        orm_pk = sorted(col.name for col in table.primary_key.columns)
        db_pk = sorted(inspector.get_pk_constraint(name)["constrained_columns"])
        if orm_pk != db_pk:
            problems.append(f"{name}: primary key {orm_pk} != {db_pk}")
    return problems


async def test_orm_matches_migrated_schema(engine: AsyncEngine) -> None:
    async with engine.connect() as connection:
        problems = await connection.run_sync(_diff_schema)
    assert (
        problems == []
    ), "ORM models and Flyway migrations have drifted:\n" + "\n".join(problems)
