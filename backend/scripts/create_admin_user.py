# -*- coding: utf-8 -*-
"""
TwinSecure - Advanced Cybersecurity Platform

Copyright (c) 2024 TwinSecure. All rights reserved.

Script to create an admin user directly in the database.
Useful for initial setup or troubleshooting login issues.

Usage:
    export ADMIN_USER_PASSWORD="your_secure_password"
    python scripts/create_admin_user.py
"""

import asyncio
import os
import sys
import uuid
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text

from app.core.config import logger, settings
from app.core.password import get_password_hash
from app.db.session import AsyncSessionLocal, engine


async def check_database_connection() -> bool:
    """Check if database connection is working."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            print("*** Database connection successful")
            return True
    
    except Exception as e:
        print(f"*** Database connection failed: {e}")
        return False


async def check_users_table() -> bool:
    """Check if users table exists with proper structure."""
    try:
        db_url = str(settings.database.DATABASE_URL)
        is_sqlite = db_url.startswith("sqlite")
        
        async with engine.connect() as conn:
            # Check if users table exists (different syntax for SQLite vs PostgreSQL)
            if is_sqlite:
                # SQLite uses sqlite_master - use a clean, separate query
                users_query = text(
                    "SELECT EXISTS ("
                    "SELECT 1 FROM sqlite_master "
                    "WHERE type='table' AND name='users'"
                    ")"
                )
                result = await conn.execute(users_query)
            else:
                # PostgreSQL uses information_schema - use a clean, separate query
                users_query = text(
                    "SELECT EXISTS ("
                    "SELECT 1 FROM information_schema.tables "
                    "WHERE table_schema = 'public' AND table_name = 'users'"
                    ")"
                )
                result = await conn.execute(users_query)
            
            users_exists = result.scalar()
            
            if not users_exists:
                print("*** The 'users' table does not exist!")
                print("  Run 'python scripts/setup_database.py' first")
                return False
            
            # Check if users_admin partition exists (PostgreSQL only)
            # Use a separate, explicit check to avoid query concatenation issues
            if not is_sqlite:
                # PostgreSQL partition check - use a completely separate query
                partition_query = text(
                    "SELECT EXISTS ("
                    "SELECT 1 FROM information_schema.tables "
                    "WHERE table_schema = 'public' AND table_name = 'users_admin'"
                    ")"
                )
                partition_result = await conn.execute(partition_query)
                partition_exists = partition_result.scalar()
                
                if not partition_exists:
                    print("*** The 'users_admin' partition does not exist")
                    return False
                print("*** Users table and admin partition exist")
            else:
                print("*** Users table exists (SQLite - no partitions needed)")
            
            return True
    
    except Exception as e:
        print(f"*** Error checking users table: {e}")
        logger.error(f"Error checking users table: {e}", exc_info=True)
        return False


async def create_admin_partition() -> bool:
    """Create the admin partition if it doesn't exist (PostgreSQL only)."""
    db_url = settings.database.DATABASE_URL
    
    # SQLite doesn't support table partitioning
    if db_url.startswith("sqlite"):
        print("*** SQLite doesn't support partitions - skipping")
        return True
    
    try:
        async with engine.begin() as conn:
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS users_admin PARTITION OF users
                FOR VALUES IN ('ADMIN');
            """))
            
            print("*** Admin partition created or already exists")
            return True
    
    except Exception as e:
        print(f"*** Error creating admin partition: {e}")
        return False


async def create_admin_user() -> bool:
    """Create an admin user in the database."""
    try:
        # Get admin password from environment
        admin_password = os.getenv("ADMIN_USER_PASSWORD")
        
        if not admin_password:
            print("\n*** ERROR: ADMIN_USER_PASSWORD environment variable not set!")
            print("\nUsage:")
            print("  export ADMIN_USER_PASSWORD='your_secure_password'")
            print("  python scripts/create_admin_user.py")
            return False

        if len(admin_password.encode("utf-8")) > 72:
            print("*** WARNING: ADMIN_USER_PASSWORD longer than 72 bytes. Truncating for bcrypt compatibility.")
            admin_password = admin_password.encode("utf-8")[:72].decode("utf-8", errors="ignore")
        
        async with AsyncSessionLocal() as session:
            # Check if admin user already exists
            result = await session.execute(text(
                "SELECT id FROM users WHERE email = 'admin@twinsecure.local'"
            ))
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print("*** Admin user already exists!")
                print(f"  User ID: {existing_user}")
                return True
            
            # Create new admin user
            user_id = uuid.uuid4()
            hashed_password = get_password_hash(admin_password)
            
            # Insert admin user
            await session.execute(text("""
                INSERT INTO users (
                    id, email, hashed_password, full_name, role, status,
                    is_active, is_superuser, created_at
                ) VALUES (
                    :id, :email, :hashed_password, :full_name, :role, :status,
                    :is_active, :is_superuser, datetime('now')
                )
            """), {
                "id": str(user_id),
                "email": "admin@twinsecure.local",
                "hashed_password": hashed_password,
                "full_name": "System Administrator",
                "role": "ADMIN",
                "status": "ACTIVE",
                "is_active": True,
                "is_superuser": True
            })
            
            await session.commit()
            
            print(f"\n*** Admin user created successfully!")
            print(f"  Email: admin@twinsecure.local")
            print(f"  User ID: {user_id}")
            return True
    
    except Exception as e:
        print(f"*** Error creating admin user: {e}")
        logger.error(f"Admin user creation failed: {e}", exc_info=True)
        return False


async def main():
    """Main function to run all setup steps."""
    print("\n" + "="*60)
    print("TwinSecure Admin User Creation Script")
    print("="*60 + "\n")
    
    # Step 1: Check database connection
    if not await check_database_connection():
        print("\n*** Setup failed: Cannot connect to database")
        return
    
    # Step 2: Check users table exists
    table_exists = await check_users_table()
    
    # Step 3: Create admin partition if needed (PostgreSQL only)
    db_url = settings.database.DATABASE_URL
    if db_url.startswith("sqlite"):
        # SQLite doesn't need partitions
        if not table_exists:
            print("\n*** Setup failed: Users table does not exist")
            return
    else:
        # PostgreSQL needs partitions
        if not table_exists or not await create_admin_partition():
            print("\n*** Setup failed: Could not ensure admin partition exists")
            return
    
    # Step 4: Create admin user
    if not await create_admin_user():
        print("\n*** Setup failed: Could not create admin user")
        return
    
    print("\n" + "="*60)
    print("*** All operations completed successfully!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())

