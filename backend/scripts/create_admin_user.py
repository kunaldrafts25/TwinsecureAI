"""
Script to create an admin user directly in the database.
This bypasses the normal application flow to help troubleshoot login issues.
"""
import asyncio
import sys
import os

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.db.session import engine, AsyncSessionLocal
from app.core.password import get_password_hash
from app.core.config import settings
from app.core.enums import UserRole, UserStatus
import uuid

async def check_database_connection():
    """Check if we can connect to the database"""
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("Database connection successful!")
            return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

async def check_users_table():
    """Check if the users table exists and has the expected structure"""
    try:
        async with engine.connect() as conn:
            # Check if the users table exists
            result = await conn.execute(text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')"
            ))
            exists = result.scalar()
            if not exists:
                print("The 'users' table does not exist!")
                return False
            
            # Check if the users_admin partition exists
            result = await conn.execute(text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users_admin')"
            ))
            admin_partition_exists = result.scalar()
            if not admin_partition_exists:
                print("The 'users_admin' partition does not exist!")
                return False
                
            print("Users table and admin partition exist.")
            return True
    except Exception as e:
        print(f"Error checking users table: {e}")
        return False

async def create_admin_partition():
    """Create the admin partition if it doesn't exist"""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS users_admin PARTITION OF users
                FOR VALUES IN ('ADMIN');
            """))
            await conn.commit()
            print("Admin partition created or already exists.")
            return True
    except Exception as e:
        print(f"Error creating admin partition: {e}")
        return False

async def create_admin_user():
    """Create an admin user directly in the database"""
    try:
        # First check if the user already exists
        async with AsyncSessionLocal() as session:
            result = await session.execute(text(
                "SELECT COUNT(*) FROM users WHERE email = :email"
            ), {"email": "admin@finguard.com"})
            count = result.scalar()
            
            if count > 0:
                print(f"User with email admin@finguard.com already exists.")
                return True
            
            # Create the user
            user_id = uuid.uuid4()
            hashed_password = get_password_hash("123456789")
            
            await session.execute(text("""
                INSERT INTO users (
                    id, email, hashed_password, full_name, role, status, 
                    is_active, is_superuser, failed_login_attempts, 
                    preferences, notification_settings
                ) VALUES (
                    :id, :email, :hashed_password, :full_name, :role, :status,
                    :is_active, :is_superuser, :failed_login_attempts,
                    :preferences, :notification_settings
                )
            """), {
                "id": user_id,
                "email": "admin@finguard.com",
                "hashed_password": hashed_password,
                "full_name": "Admin User",
                "role": "ADMIN",
                "status": "ACTIVE",
                "is_active": True,
                "is_superuser": True,
                "failed_login_attempts": 0,
                "preferences": "{}",
                "notification_settings": '{"email": true, "slack": false, "discord": false}'
            })
            
            await session.commit()
            print(f"Admin user created successfully with email: admin@finguard.com")
            print(f"Password: 123456789")
            return True
    except Exception as e:
        print(f"Error creating admin user: {e}")
        return False

async def main():
    """Main function to run all checks and fixes"""
    print("Starting database checks and admin user creation...")
    
    # Check database connection
    if not await check_database_connection():
        return
    
    # Check users table
    table_exists = await check_users_table()
    
    # Create admin partition if needed
    if not table_exists or not await create_admin_partition():
        print("Could not ensure admin partition exists.")
        return
    
    # Create admin user
    if not await create_admin_user():
        print("Failed to create admin user.")
        return
    
    print("All operations completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
