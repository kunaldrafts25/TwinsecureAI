import asyncio # Import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
# Import create_async_engine instead of create_engine
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# --- START TwinSecure Configuration ---
import os
import sys
from app.core.config import settings # Import your application settings
from app.db.base import Base # Import your Base model from your app structure

# Add the project root directory to the Python path
# This allows Alembic to find your app modules (like models, base)
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

target_metadata = Base.metadata # Use the metadata from your Base

# Use DATABASE_URL from your application settings
# Instead of setting it in the config, we'll use it directly in the engine creation
db_url = settings.DATABASE_URL
if not db_url:
    raise ValueError("DATABASE_URL environment variable is not set for Alembic.")

# Print the database URL for debugging
print(f"Database URL: {db_url}")

# --- END TwinSecure Configuration ---


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # Use the db_url directly instead of getting it from config
    context.configure(
        url=db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True, # Compare column types during autogenerate
    )

    with context.begin_transaction():
        context.run_migrations()


# --- START Async Configuration ---
def do_run_migrations(connection: Connection) -> None:
    """Helper function to run migrations using a synchronous connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True, # Compare column types during autogenerate
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Create an async engine using the db_url directly
    connectable = create_async_engine(
        db_url,
        poolclass=pool.NullPool, # Use NullPool for migrations
    )

    # Acquire an async connection
    async with connectable.connect() as connection:
        # Run the migrations within the transaction context of the async connection
        await connection.run_sync(do_run_migrations)

    # Dispose of the engine
    await connectable.dispose()
# --- END Async Configuration ---


if context.is_offline_mode():
    run_migrations_offline()
else:
    # Run the async online migration function using asyncio.run
    asyncio.run(run_migrations_online())


