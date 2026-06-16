import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context
from app.core.config import settings
from app.db.database import Base
from app.db.models import user  # import all models so alembic sees them

config = context.config
fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Use DIRECT_URL for migrations (session mode, no pgbouncer)
MIGRATION_URL = settings.DIRECT_URL.replace(
    "postgresql://", "postgresql+asyncpg://"
)


def run_migrations_offline():
    context.configure(
        url=MIGRATION_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    connectable = create_async_engine(MIGRATION_URL, poolclass=pool.NullPool)

    async with connectable.connect() as connection:
        await connection.run_sync(
            lambda conn: context.configure(
                connection=conn,
                target_metadata=target_metadata,
            )
        )
        async with connection.begin():
            await connection.run_sync(lambda conn: context.run_migrations())

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())