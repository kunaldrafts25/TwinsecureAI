"""
Check PostgreSQL availability for tests.
This script checks if PostgreSQL is available for testing and sets environment variables accordingly.
"""

import asyncio
import logging
import os
import socket
import sys
from typing import Dict, Optional, Tuple

import asyncpg

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Default PostgreSQL connection parameters
DEFAULT_PG_HOST = "localhost"
DEFAULT_PG_PORT = 5432
DEFAULT_PG_USER = "postgres"
DEFAULT_PG_PASSWORD = "postgres"
DEFAULT_PG_DB = "test_twinsecure"


def is_port_open(host: str, port: int, timeout: float = 1.0) -> bool:
    """Check if a port is open on a host."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        logger.warning(f"Error checking port {port} on {host}: {e}")
        return False


async def check_postgres_connection(
    host: str = DEFAULT_PG_HOST,
    port: int = DEFAULT_PG_PORT,
    user: str = DEFAULT_PG_USER,
    password: str = DEFAULT_PG_PASSWORD,
    database: str = DEFAULT_PG_DB,
    timeout: float = 3.0,
) -> Tuple[bool, Optional[str]]:
    """
    Check if PostgreSQL is available and can be connected to.

    Returns:
        Tuple[bool, Optional[str]]: (success, error_message)
    """
    # First check if the port is open
    if not is_port_open(host, port):
        return False, f"PostgreSQL port {port} is not open on {host}"

    # Try to connect to PostgreSQL
    try:
        conn_str = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        conn = await asyncpg.connect(conn_str, timeout=timeout)
        await conn.execute("SELECT 1")  # Simple query to verify connection
        await conn.close()
        return True, None
    except Exception as e:
        return False, f"Failed to connect to PostgreSQL: {str(e)}"


async def create_test_database(
    host: str = DEFAULT_PG_HOST,
    port: int = DEFAULT_PG_PORT,
    user: str = DEFAULT_PG_USER,
    password: str = DEFAULT_PG_PASSWORD,
    database: str = DEFAULT_PG_DB,
) -> Tuple[bool, Optional[str]]:
    """
    Create a test database if it doesn't exist.

    Returns:
        Tuple[bool, Optional[str]]: (success, error_message)
    """
    try:
        # Connect to the default database
        conn_str = f"postgresql://{user}:{password}@{host}:{port}/postgres"
        conn = await asyncpg.connect(conn_str)

        # Check if the test database exists
        exists = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM pg_database WHERE datname = $1)", database
        )

        if not exists:
            # Create the test database
            await conn.execute(f"CREATE DATABASE {database}")
            logger.info(f"Created test database: {database}")

        await conn.close()
        return True, None
    except Exception as e:
        return False, f"Failed to create test database: {str(e)}"


def get_postgres_env() -> Dict[str, str]:
    """
    Get PostgreSQL environment variables.

    Returns:
        Dict[str, str]: Dictionary of environment variables
    """
    return {
        "TEST_PG_HOST": os.getenv("TEST_PG_HOST", DEFAULT_PG_HOST),
        "TEST_PG_PORT": os.getenv("TEST_PG_PORT", str(DEFAULT_PG_PORT)),
        "TEST_PG_USER": os.getenv("TEST_PG_USER", DEFAULT_PG_USER),
        "TEST_PG_PASSWORD": os.getenv("TEST_PG_PASSWORD", DEFAULT_PG_PASSWORD),
        "TEST_PG_DB": os.getenv("TEST_PG_DB", DEFAULT_PG_DB),
    }


async def main():
    """Main function to check PostgreSQL availability."""
    # Get PostgreSQL environment variables
    pg_env = get_postgres_env()

    # Check if PostgreSQL is available
    success, error = await check_postgres_connection(
        host=pg_env["TEST_PG_HOST"],
        port=int(pg_env["TEST_PG_PORT"]),
        user=pg_env["TEST_PG_USER"],
        password=pg_env["TEST_PG_PASSWORD"],
        database="postgres",  # First connect to default database
    )

    if success:
        logger.info("PostgreSQL is available")

        # Create test database if it doesn't exist
        db_success, db_error = await create_test_database(
            host=pg_env["TEST_PG_HOST"],
            port=int(pg_env["TEST_PG_PORT"]),
            user=pg_env["TEST_PG_USER"],
            password=pg_env["TEST_PG_PASSWORD"],
            database=pg_env["TEST_PG_DB"],
        )

        if db_success:
            logger.info(f"Test database '{pg_env['TEST_PG_DB']}' is ready")
            # Set environment variable to indicate PostgreSQL is available
            os.environ["USE_POSTGRES_FOR_TESTS"] = "true"
            return True
        else:
            logger.warning(db_error)
    else:
        logger.warning(f"PostgreSQL is not available: {error}")
        logger.info("Tests will use SQLite instead")
        # Set environment variable to indicate PostgreSQL is not available
        os.environ["USE_POSTGRES_FOR_TESTS"] = "false"

    return False


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
