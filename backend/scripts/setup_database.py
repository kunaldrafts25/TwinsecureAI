"""
TwinSecure - Advanced Cybersecurity Platform
Copyright © 2024 TwinSecure. All rights reserved.

This file is part of TwinSecure, a proprietary cybersecurity platform.
Unauthorized copying, distribution, modification, or use of this software
is strictly prohibited without explicit written permission.

For licensing inquiries: kunalsingh2514@gmail.com
"""

"""
Script to set up the database, run migrations, and ensure partitions are created.
"""
import asyncio
import sys
import os
import subprocess

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.db.session import engine
from app.core.config import settings

async def check_database_exists():
    """Check if the database exists, and create it if it doesn't"""
    # Connect to the default postgres database to check if our database exists
    connection_string = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD.get_secret_value()}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/postgres"
    
    from sqlalchemy.ext.asyncio import create_async_engine
    temp_engine = create_async_engine(connection_string)
    
    try:
        async with temp_engine.connect() as conn:
            # Check if the database exists
            result = await conn.execute(text(
                f"SELECT 1 FROM pg_database WHERE datname = '{settings.POSTGRES_DB}'"
            ))
            exists = result.scalar()
            
            if not exists:
                print(f"Database '{settings.POSTGRES_DB}' does not exist. Creating...")
                # Need to commit to execute CREATE DATABASE
                await conn.execute(text("COMMIT"))
                await conn.execute(text(f"CREATE DATABASE \"{settings.POSTGRES_DB}\""))
                print(f"Database '{settings.POSTGRES_DB}' created successfully.")
            else:
                print(f"Database '{settings.POSTGRES_DB}' already exists.")
            
            return True
    except Exception as e:
        print(f"Error checking/creating database: {e}")
        return False
    finally:
        await temp_engine.dispose()

def run_alembic_migrations():
    """Run Alembic migrations to create/update the database schema"""
    try:
        print("Running Alembic migrations...")
        # Change to the backend directory
        os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Run the migrations
        result = subprocess.run(["alembic", "upgrade", "head"], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Alembic migrations completed successfully.")
            print(result.stdout)
            return True
        else:
            print(f"Error running Alembic migrations: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error running Alembic migrations: {e}")
        return False

async def ensure_partitions_exist():
    """Ensure all required partitions exist for the users table"""
    try:
        async with engine.connect() as conn:
            # Check if the users table exists
            result = await conn.execute(text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')"
            ))
            users_exists = result.scalar()
            
            if not users_exists:
                print("The 'users' table does not exist. Run migrations first.")
                return False
            
            # Check and create partitions for each role
            roles = ['ADMIN', 'ANALYST', 'VIEWER', 'API_USER']
            
            for role in roles:
                partition_name = f"users_{role.lower()}"
                
                # Check if the partition exists
                result = await conn.execute(text(
                    f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{partition_name}')"
                ))
                partition_exists = result.scalar()
                
                if not partition_exists:
                    print(f"Creating partition for role '{role}'...")
                    await conn.execute(text(f"""
                        CREATE TABLE IF NOT EXISTS {partition_name} PARTITION OF users
                        FOR VALUES IN ('{role}');
                    """))
                    await conn.commit()
                    print(f"Partition '{partition_name}' created successfully.")
                else:
                    print(f"Partition '{partition_name}' already exists.")
            
            return True
    except Exception as e:
        print(f"Error ensuring partitions exist: {e}")
        return False

async def main():
    """Main function to run all database setup steps"""
    print("Starting database setup...")
    
    # Check if the database exists
    if not await check_database_exists():
        print("Failed to check/create database. Exiting.")
        return
    
    # Run Alembic migrations
    if not run_alembic_migrations():
        print("Failed to run migrations. Exiting.")
        return
    
    # Ensure partitions exist
    if not await ensure_partitions_exist():
        print("Failed to ensure partitions exist. Exiting.")
        return
    
    print("Database setup completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
