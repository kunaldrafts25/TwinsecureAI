# TwinSecure Testing Framework

This directory contains the comprehensive testing framework for the TwinSecure backend application.

## Overview

The testing framework uses pytest and provides extensive test coverage for the TwinSecure API endpoints, including:

- Authentication tests
- Alert management tests
- Report management tests
- Honeypot data tests
- System health tests
- Database integration tests
- Data validation tests
- Performance tests
- Security tests
- Load tests
- Code coverage reporting
- CI/CD integration

## Test Structure

- `conftest.py`: Contains pytest fixtures and configuration
- `mock_app.py`: A mock FastAPI application for testing
- `db_test_utils.py`: Utilities for SQLite database testing
- `pg_test_utils.py`: Utilities for PostgreSQL database testing
- `locustfile.py`: Load testing script using Locust

### Test Files

#### Basic API Tests
- `test_api_endpoints.py`: Basic API endpoint tests
- `test_api_endpoints_extended.py`: Extended API endpoint tests
- `test_health.py`: Health check tests

#### Feature-Specific Tests
- `test_auth.py`: Authentication tests
- `test_alerts.py`: Alert management tests
- `test_reports.py`: Report management tests
- `test_honeypot.py`: Honeypot data tests

#### Advanced Tests
- `test_db_integration.py`: Database integration tests
- `test_data_validation.py`: Data validation and edge case tests
- `test_performance.py`: API performance tests
- `test_security.py`: Security vulnerability tests

## Key Features

### Authentication Testing

The framework includes comprehensive authentication testing:
- Login with valid/invalid credentials
- Token validation
- User permission checks
- Superuser access control

### Mock Database

The `mock_app.py` file includes a mock database with test data for:
- Users (regular and admin)
- Alerts
- Reports
- Honeypot events

### Database Integration Testing

The framework includes real database integration tests using both SQLite and PostgreSQL:
- User creation and authentication
- Alert CRUD operations
- Database validation

### Data Validation Testing

Tests for data validation include:
- Input validation for all endpoints
- Edge case handling
- Error responses

### Performance Testing

Performance tests measure:
- API response times
- Endpoint performance under load
- Performance thresholds

### Load Testing

Load tests using Locust simulate:
- Multiple concurrent users
- Different user types (regular and admin)
- Various API endpoints
- Realistic user behavior

### Security Testing

Security tests check for:
- CORS configuration
- Authentication/authorization
- SQL injection protection
- XSS protection
- Brute force protection

### Code Coverage

Code coverage reporting shows:
- Line coverage
- Branch coverage
- Missing coverage areas
- HTML and XML reports

### CI/CD Integration

GitHub Actions workflow includes:
- Automated test runs
- Code coverage reporting
- Linting and formatting checks
- Load testing on main branch

### Test Fixtures

The `conftest.py` file provides fixtures for:
- Test client
- Authentication tokens
- Authentication headers
- Database sessions
- Test users and alerts
- Performance measurement

## Running Tests

### Basic Test Commands

To run all tests:

```bash
python -m pytest
```

To run specific test files:

```bash
python -m pytest tests/test_auth.py
```

To run tests with verbose output:

```bash
python -m pytest -v
```

### Running Tests with Coverage

Use the provided PowerShell script:

```powershell
.\run_tests.ps1 -html -v
```

Or run manually:

```bash
python -m pytest --cov=app --cov-report=html --cov-report=term
```

### Running Load Tests

Use the provided PowerShell script:

```powershell
.\run_load_tests.ps1 -u 20 -r 5 -t 2m
```

Or run manually:

```bash
locust -f tests/locustfile.py -u 20 -r 5 --run-time 2m --headless --host http://localhost:8000
```

For the web interface, omit the `--headless` and `--run-time` options:

```bash
locust -f tests/locustfile.py --host http://localhost:8000
```

### Running Tests in CI/CD

Tests are automatically run on GitHub Actions when:
- Code is pushed to main or develop branches
- Pull requests are created against main or develop branches

## Test Coverage

The current test suite provides comprehensive coverage of:
- Authentication endpoints
- User management endpoints
- Alert management endpoints
- Report management endpoints
- Honeypot data endpoints
- System health endpoints
- Database operations
- Data validation
- API performance
- Security vulnerabilities

## Database Configuration

### SQLite (Default)

SQLite is used by default for quick testing. No configuration is needed.

### PostgreSQL

To use PostgreSQL for testing, set the following environment variables:

```bash
TEST_PG_HOST=localhost
TEST_PG_PORT=5432
TEST_PG_USER=postgres
TEST_PG_PASSWORD=postgres
TEST_PG_DB=test_twinsecure
```

Then import from `pg_test_utils` instead of `db_test_utils`.

## Future Improvements

- Add API contract tests
- Add mutation testing
- Add property-based testing
- Add integration with monitoring systems
- Add performance regression testing
