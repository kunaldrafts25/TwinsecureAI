# TwinSecure Backend API Documentation

This document provides detailed information about the TwinSecure backend API structure, modules, and usage.

## Directory Structure

- **api/**: API endpoints and routers
  - **api_v1/**: Version 1 of the API
    - **endpoints/**: Individual endpoint modules
    - **api.py**: Main API router
  - **deps.py**: Dependency injection functions

- **core/**: Core functionality and configuration
  - **config.py**: Application configuration
  - **security.py**: Security utilities (JWT, password hashing)
  - **logging.py**: Logging configuration

- **db/**: Database models and utilities
  - **base.py**: Base models and metadata
  - **session.py**: Database session management
  - **init_db.py**: Database initialization
  - **models/**: SQLAlchemy models

- **middleware/**: Custom middleware
  - **logging_middleware.py**: Request/response logging
  - **error_handling.py**: Global error handling

- **ml/**: Machine learning models and utilities
  - **models/**: ML model definitions
  - **training/**: Training scripts
  - **prediction/**: Prediction utilities

- **schemas/**: Pydantic schemas for request/response validation
  - **users.py**: User-related schemas
  - **alerts.py**: Alert-related schemas
  - **reports.py**: Report-related schemas

- **services/**: Business logic services
  - **alerting/**: Alert generation and notification
  - **enrichment/**: Data enrichment services
  - **reporting/**: Report generation

## API Endpoints

### Authentication

- **POST /api/v1/auth/login**: User login
  - Request: `{ "email": "user@example.com", "password": "password" }`
  - Response: `{ "access_token": "token", "token_type": "bearer" }`

- **POST /api/v1/auth/refresh**: Refresh access token
  - Request: `{ "refresh_token": "token" }`
  - Response: `{ "access_token": "token", "token_type": "bearer" }`

### Users

- **GET /api/v1/users/me**: Get current user
  - Response: User object

- **GET /api/v1/users/{user_id}**: Get user by ID
  - Response: User object

- **POST /api/v1/users/**: Create new user
  - Request: User creation object
  - Response: Created user object

- **PUT /api/v1/users/{user_id}**: Update user
  - Request: User update object
  - Response: Updated user object

### Alerts

- **GET /api/v1/alerts/**: Get all alerts
  - Query params: `skip`, `limit`, `severity`, `status`
  - Response: List of alert objects

- **GET /api/v1/alerts/{alert_id}**: Get alert by ID
  - Response: Alert object

- **POST /api/v1/alerts/**: Create new alert
  - Request: Alert creation object
  - Response: Created alert object

- **PUT /api/v1/alerts/{alert_id}**: Update alert
  - Request: Alert update object
  - Response: Updated alert object

### Reports

- **GET /api/v1/reports/**: Get all reports
  - Query params: `skip`, `limit`, `type`, `date_range`
  - Response: List of report objects

- **GET /api/v1/reports/{report_id}**: Get report by ID
  - Response: Report object

- **POST /api/v1/reports/generate**: Generate new report
  - Request: Report generation parameters
  - Response: Generated report object

### System Health

- **GET /api/v1/health**: Get system health status
  - Response: Health status object

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. To access protected endpoints:

1. Obtain a token via the login endpoint
2. Include the token in the Authorization header: `Authorization: Bearer {token}`

## Error Handling

All API endpoints return standard error responses:

```json
{
  "detail": "Error message",
  "status_code": 400,
  "error_code": "ERROR_CODE"
}
```

Common error codes:
- `AUTHENTICATION_ERROR`: Authentication failed
- `PERMISSION_DENIED`: Insufficient permissions
- `RESOURCE_NOT_FOUND`: Requested resource not found
- `VALIDATION_ERROR`: Request validation failed
- `INTERNAL_ERROR`: Internal server error

## Database Models

The application uses SQLAlchemy ORM with the following main models:

- **User**: User accounts and authentication
- **Alert**: Security alerts and notifications
- **Report**: Generated security reports
- **Honeypot**: Honeypot data and events
- **DigitalTwin**: Digital twin configuration and status

## Services

### Alerting Service

Handles alert generation, enrichment, and notification:
- Alert creation from security events
- Alert enrichment with context data
- Alert notification via multiple channels (email, Slack, etc.)

### Reporting Service

Handles report generation and delivery:
- Security posture reports
- Compliance reports
- Threat intelligence reports
- PDF and HTML report formats

### Enrichment Service

Provides data enrichment for alerts and reports:
- GeoIP lookup
- Threat intelligence integration
- WHOIS data
- Historical context

## Configuration

The application is configured via environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Secret key for JWT token generation
- `ENVIRONMENT`: Application environment (development, staging, production)
- `LOG_LEVEL`: Logging level
- `CORS_ORIGINS`: Allowed CORS origins

See `.env.example` for a complete list of configuration options.
