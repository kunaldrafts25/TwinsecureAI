"""Add user partitions

Revision ID: 2c01dbd33ee9
Revises: 1c01dbd33ee8
Create Date: 2025-05-15 01:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2c01dbd33ee9'
down_revision = '1c01dbd33ee8'
branch_labels = None
depends_on = None


def upgrade():
    # Create partitions for each role
    op.execute("""
    CREATE TABLE users_admin PARTITION OF users
    FOR VALUES IN ('ADMIN');
    """)

    op.execute("""
    CREATE TABLE users_analyst PARTITION OF users
    FOR VALUES IN ('ANALYST');
    """)

    op.execute("""
    CREATE TABLE users_viewer PARTITION OF users
    FOR VALUES IN ('VIEWER');
    """)

    op.execute("""
    CREATE TABLE users_api_user PARTITION OF users
    FOR VALUES IN ('API_USER');
    """)


def downgrade():
    # Drop partitions
    op.execute("DROP TABLE IF EXISTS users_admin;")
    op.execute("DROP TABLE IF EXISTS users_analyst;")
    op.execute("DROP TABLE IF EXISTS users_viewer;")
    op.execute("DROP TABLE IF EXISTS users_api_user;")
