# TwinSecure Login Troubleshooting Guide

This guide provides solutions for fixing login issues with the TwinSecure application.

## Common Issues

1. **Database Partitioning Issue**: The users table is partitioned by role, but the partition for the 'ADMIN' role might be missing.
2. **Database Connection Issues**: Case sensitivity with the database name or connection parameters.
3. **User Creation Issues**: The superuser might not be created correctly.

## Solution Steps

### 1. Set Up the Database Properly

Run the database setup script to ensure the database exists, migrations are applied, and partitions are created:

```bash
cd backend
python -m scripts.setup_database
```

This script will:
- Check if the database exists and create it if needed
- Run Alembic migrations to create the schema
- Ensure all required partitions exist for the users table

### 2. Create the Admin User

Run the admin user creation script to ensure the admin user exists:

```bash
cd backend
python -m scripts.create_admin_user
```

This script will:
- Check database connection
- Verify the users table and admin partition exist
- Create the admin user if it doesn't exist

### 3. Bypass Login (Development Only)

If you still can't log in, you can use the bypass login feature we've added to the login page:

1. Go to the login page
2. Scroll to the bottom
3. Click the "Bypass Login (Dev Only)" button

This will create a fake session without contacting the backend and take you directly to the dashboard.

## Detailed Explanation of the Issues

### Database Partitioning

The users table is partitioned by role using PostgreSQL's table partitioning feature. Each role (ADMIN, ANALYST, VIEWER, API_USER) should have its own partition table. The error logs showed:

```
Error creating superuser: no partition of relation "users" found for row
DETAIL: Partition key of the failing row contains (role) = (ADMIN).
```

This means the ADMIN partition was missing, so the system couldn't create the admin user.

### Database Case Sensitivity

PostgreSQL is case-sensitive for identifiers unless they're quoted. The error logs showed:

```
database "Twinsecure" does not exist
```

This suggests a case mismatch between the configured database name and the actual database name.

### Password Validation

The system uses bcrypt for password hashing, which is secure. However, there might be issues with password validation if the password doesn't meet the requirements or if the hashed password is not being stored correctly.

## Preventive Measures

To prevent these issues in the future:

1. **Database Initialization**: Ensure the database initialization script creates all required partitions.
2. **Case Consistency**: Use consistent casing for database names and other identifiers.
3. **Error Handling**: Improve error handling to provide more specific error messages.
4. **Logging**: Enhance logging to capture more details about authentication failures.

## Contact Support

If you continue to experience issues, please contact the TwinSecure support team at support@twinsecure.ai.
