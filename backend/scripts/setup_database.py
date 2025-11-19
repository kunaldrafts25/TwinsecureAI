#!/usr/bin/env python
"""
TwinSecure - Advanced Cybersecurity Platform

Copyright *� 2024 TwinSecure. All rights reserved.

Script to set up the database, run migrations, and ensure partitions are created.

Usage:
    python scripts/setup_database.py
"""

import asyncio
import os
import subprocess
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import logger, settings
from app.db.session import engine


async def check_database_exists() -> bool:
    """Check if the database exists, and create it if it doesn't."""
    db_url = settings.database.DATABASE_URL
    
    # SQLite doesn't need database creation - file is created automatically
    if db_url.startswith("sqlite"):
        db_path = settings.database.SQLITE_DB_PATH
        db_file = Path(db_path)
        
        if db_file.exists():
            print(f"SQLite database '{db_path}' already exists")
        else:
            print(f"SQLite database '{db_path}' will be created on first connection")
        
        return True
    
    # PostgreSQL: Connect to the default postgres database to check if our database exists
    if not settings.database.POSTGRES_PASSWORD:
        print("*** POSTGRES_PASSWORD is required when using PostgreSQL")
        return False
    
    connection_string = (
        f"postgresql+asyncpg://{settings.database.POSTGRES_USER}:"
        f"{settings.database.POSTGRES_PASSWORD.get_secret_value()}@"
        f"{settings.database.POSTGRES_SERVER}:{settings.database.POSTGRES_PORT}/postgres"
    )
    
    temp_engine = create_async_engine(connection_string, isolation_level="AUTOCOMMIT")
    
    try:
        async with temp_engine.connect() as conn:
            # Check if the database exists
            result = await conn.execute(text(
                f"SELECT 1 FROM pg_database WHERE datname = '{settings.database.POSTGRES_DB}'"
            ))
            
            exists = result.scalar()
            
            if not exists:
                print(f"*** Database '{settings.database.POSTGRES_DB}' does not exist. Creating...")
                
                # Create database (AUTOCOMMIT isolation level allows this)
                await conn.execute(text(
                    f'CREATE DATABASE "{settings.database.POSTGRES_DB}"'
                ))
                
                print(f"*** Database '{settings.database.POSTGRES_DB}' created successfully")
            else:
                print(f"*** Database '{settings.database.POSTGRES_DB}' already exists")
            
            return True
    
    except Exception as e:
        print(f"*** Error checking/creating database: {e}")
        logger.error(f"Database check/creation failed: {e}", exc_info=True)
        return False
    
    finally:
        await temp_engine.dispose()


def run_alembic_migrations() -> bool:
    """Run Alembic migrations to create/update the database schema."""
    try:
        print("\nRunning Alembic migrations...")
        
        # Change to the backend directory
        backend_dir = Path(__file__).parent.parent
        os.chdir(backend_dir)
        
        # Run the migrations
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout
        )
        
        if result.returncode == 0:
            print("*** Alembic migrations completed successfully")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"*** Error running Alembic migrations:")
            print(result.stderr)
            return False
    
    except FileNotFoundError:
        print("*** Alembic not found. Install with: pip install alembic")
        return False
    
    except subprocess.TimeoutExpired:
        print("*** Alembic migration timed out after 60 seconds")
        return False
    
    except Exception as e:
        print(f"*** Error running Alembic migrations: {e}")
        logger.error(f"Alembic migration failed: {e}", exc_info=True)
        return False


async def ensure_partitions_exist() -> bool:
    """Ensure all required partitions exist for the users table (PostgreSQL only)."""
    db_url = str(settings.database.DATABASE_URL)
    
    # SQLite doesn't support table partitioning
    if db_url.startswith("sqlite"):
        print("Table partitioning is not supported in SQLite (PostgreSQL feature)")
        return True
    
    try:
        print("\nChecking user role partitions...")
        
        async with engine.begin() as conn:
            # Check if the users table exists - use explicit query with schema
            users_check_query = text(
                "SELECT EXISTS ("
                "SELECT 1 FROM information_schema.tables "
                "WHERE table_schema = 'public' AND table_name = 'users'"
                ")"
            )
            result = await conn.execute(users_check_query)
            users_exists = result.scalar()
            
            if not users_exists:
                print("*** The 'users' table does not exist. Run migrations first.")
                return False
            
            # Check and create partitions for each role
            roles = ["ADMIN", "ANALYST", "VIEWER", "API_USER"]
            
            for role in roles:
                partition_name = f"users_{role.lower()}"
                
                # Check if the partition exists - use explicit query with schema
                partition_check_query = text(
                    "SELECT EXISTS ("
                    "SELECT 1 FROM information_schema.tables "
                    "WHERE table_schema = 'public' AND table_name = :partition_name"
                    ")"
                )
                result = await conn.execute(
                    partition_check_query,
                    {"partition_name": partition_name}
                )
                partition_exists = result.scalar()
                
                if not partition_exists:
                    print(f"  Creating partition for role '{role}'...")
                    
                    # Create partition - role value is safe as it comes from a controlled list
                    create_partition_query = text(
                        f"CREATE TABLE IF NOT EXISTS {partition_name} "
                        f"PARTITION OF users FOR VALUES IN ('{role}')"
                    )
                    await conn.execute(create_partition_query)
                    
                    print(f"  *** Partition '{partition_name}' created successfully")
                else:
                    print(f"  *** Partition '{partition_name}' already exists")
        
        print("*** All role partitions verified")
        return True
    
    except Exception as e:
        print(f"*** Error ensuring partitions exist: {e}")
        logger.error(f"Partition creation failed: {e}", exc_info=True)
        return False


async def main():
    """Main function to run all database setup steps."""
    print("\n" + "="*60)
    print("TwinSecure Database Setup Script")
    print("="*60 + "\n")
    
    # Step 1: Check if the database exists
    print("Step 1: Checking database...")
    if not await check_database_exists():
        print("\n*** Setup failed: Could not check/create database")
        return
    
    # Step 2: Run Alembic migrations
    print("\nStep 2: Running migrations...")
    if not run_alembic_migrations():
        print("\n*** Setup failed: Could not run migrations")
        return
    
    # Step 3: Ensure partitions exist
    print("\nStep 3: Setting up partitions...")
    if not await ensure_partitions_exist():
        print("\n*** Setup failed: Could not ensure partitions exist")
        return
    
    print("\n" + "="*60)
    print("*** Database setup completed successfully!")
    print("="*60 + "\n")


if __name__ == "__main__":
    """Run the script directly."""
    asyncio.run(main())
