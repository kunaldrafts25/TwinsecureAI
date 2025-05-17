"""
Script to check PostgreSQL connection and create the database if needed.
"""
import asyncio
import sys
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

def check_and_create_database():
    """Check if the database exists and create it if it doesn't"""
    try:
        # Connect to the default postgres database
        conn = psycopg2.connect(
            host=settings.POSTGRES_SERVER,
            port=settings.POSTGRES_PORT,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        # Create a cursor
        cursor = conn.cursor()

        # Check if the database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{settings.POSTGRES_DB}'")
        exists = cursor.fetchone()

        if not exists:
            print(f"Database '{settings.POSTGRES_DB}' does not exist. Creating...")
            cursor.execute(f'CREATE DATABASE "{settings.POSTGRES_DB}"')
            print(f"Database '{settings.POSTGRES_DB}' created successfully.")
        else:
            print(f"Database '{settings.POSTGRES_DB}' already exists.")

        # Close the connection
        cursor.close()
        conn.close()

        return True
    except Exception as e:
        print(f"Error checking/creating database: {e}")
        return False

def run_alembic_migrations():
    """Run Alembic migrations to create/update the database schema"""
    try:
        print("Running Alembic migrations...")
        # Change to the backend directory
        os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        # Run the migrations
        os.system("alembic upgrade head")
        print("Alembic migrations completed.")
        return True
    except Exception as e:
        print(f"Error running Alembic migrations: {e}")
        return False

def create_admin_user():
    """Create an admin user directly in the database"""
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host=settings.POSTGRES_SERVER,
            port=settings.POSTGRES_PORT,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database=settings.POSTGRES_DB
        )

        # Create a cursor
        cursor = conn.cursor()

        # Check if the users table exists
        cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')")
        table_exists = cursor.fetchone()[0]

        if not table_exists:
            print("The 'users' table does not exist. Run migrations first.")
            cursor.close()
            conn.close()
            return False

        # Check if the admin partition exists
        cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users_admin')")
        admin_partition_exists = cursor.fetchone()[0]

        if not admin_partition_exists:
            print("Creating admin partition...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users_admin PARTITION OF users
                FOR VALUES IN ('ADMIN');
            """)
            print("Admin partition created.")

        # Check if the admin user already exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE email = 'admin@finguard.com'")
        count = cursor.fetchone()[0]

        if count > 0:
            print("Admin user already exists.")
        else:
            # Import the password hashing function
            from app.core.password import get_password_hash
            import uuid

            # Create the admin user
            user_id = uuid.uuid4()
            hashed_password = get_password_hash("123456789")

            cursor.execute("""
                INSERT INTO users (
                    id, email, hashed_password, full_name, role, status,
                    is_active, is_superuser, failed_login_attempts,
                    preferences, notification_settings
                ) VALUES (
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s
                )
            """, (
                user_id, "admin@finguard.com", hashed_password, "Admin User", "ADMIN", "ACTIVE",
                True, True, 0,
                "{}", '{"email": true, "slack": false, "discord": false}'
            ))

            conn.commit()
            print("Admin user created successfully.")

        # Close the connection
        cursor.close()
        conn.close()

        return True
    except Exception as e:
        print(f"Error creating admin user: {e}")
        return False

def main():
    """Main function to run all checks and fixes"""
    print("Starting database checks and fixes...")

    # Check and create database
    if not check_and_create_database():
        print("Failed to check/create database. Exiting.")
        return

    # Run Alembic migrations
    if not run_alembic_migrations():
        print("Failed to run migrations. Exiting.")
        return

    # Create admin user
    if not create_admin_user():
        print("Failed to create admin user. Exiting.")
        return

    print("All operations completed successfully!")

if __name__ == "__main__":
    main()
