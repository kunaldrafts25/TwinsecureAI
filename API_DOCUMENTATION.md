# TwinSecure API Documentation

## Overview

The TwinSecure API provides a comprehensive set of endpoints for managing digital twin security, alerts, reports, and user management. This RESTful API uses JSON for request and response bodies and JWT for authentication.

## Base URL

```
http://localhost:8000/api/v1
```

For production deployments, use your domain with HTTPS.

## Authentication

### Obtain Access Token

```
POST /auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Refresh Access Token

```
POST /auth/refresh
```

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Using Authentication

Include the access token in the Authorization header for all protected endpoints:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Users

### Get Current User

```
GET /users/me
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "ADMIN",
  "is_active": true,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

### Get User by ID

```
GET /users/{user_id}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "ADMIN",
  "is_active": true,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

### Create User

```
POST /users
```

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "password": "password123",
  "full_name": "New User",
  "role": "USER"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "email": "newuser@example.com",
  "full_name": "New User",
  "role": "USER",
  "is_active": true,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

### Update User

```
PUT /users/{user_id}
```

**Request Body:**
```json
{
  "full_name": "Updated Name",
  "role": "ADMIN"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "Updated Name",
  "role": "ADMIN",
  "is_active": true,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-02T00:00:00Z"
}
```

## Alerts

### Get Alerts

```
GET /alerts
```

**Query Parameters:**
- `skip` (integer): Number of items to skip (default: 0)
- `limit` (integer): Maximum number of items to return (default: 100)
- `severity` (string): Filter by severity (LOW, MEDIUM, HIGH, CRITICAL)
- `status` (string): Filter by status (NEW, ACKNOWLEDGED, RESOLVED)

**Response:**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "title": "Suspicious Login Attempt",
      "description": "Multiple failed login attempts detected",
      "severity": "HIGH",
      "status": "NEW",
      "source": "Authentication Service",
      "target": "User Authentication",
      "created_at": "2023-01-01T00:00:00Z",
      "updated_at": "2023-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

### Get Alert by ID

```
GET /alerts/{alert_id}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "title": "Suspicious Login Attempt",
  "description": "Multiple failed login attempts detected",
  "severity": "HIGH",
  "status": "NEW",
  "source": "Authentication Service",
  "target": "User Authentication",
  "details": {
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0...",
    "attempts": 5
  },
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

### Create Alert

```
POST /alerts
```

**Request Body:**
```json
{
  "title": "New Security Alert",
  "description": "Potential security breach detected",
  "severity": "CRITICAL",
  "source": "Firewall",
  "target": "Network",
  "details": {
    "ip_address": "10.0.0.1",
    "port": 22,
    "protocol": "SSH"
  }
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440003",
  "title": "New Security Alert",
  "description": "Potential security breach detected",
  "severity": "CRITICAL",
  "status": "NEW",
  "source": "Firewall",
  "target": "Network",
  "details": {
    "ip_address": "10.0.0.1",
    "port": 22,
    "protocol": "SSH"
  },
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

### Update Alert

```
PUT /alerts/{alert_id}
```

**Request Body:**
```json
{
  "status": "ACKNOWLEDGED",
  "notes": "Investigating the issue"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "title": "Suspicious Login Attempt",
  "description": "Multiple failed login attempts detected",
  "severity": "HIGH",
  "status": "ACKNOWLEDGED",
  "source": "Authentication Service",
  "target": "User Authentication",
  "notes": "Investigating the issue",
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-02T00:00:00Z"
}
```

## Reports

### Get Reports

```
GET /reports
```

**Query Parameters:**
- `skip` (integer): Number of items to skip (default: 0)
- `limit` (integer): Maximum number of items to return (default: 100)
- `type` (string): Filter by report type
- `start_date` (string): Filter by start date (ISO format)
- `end_date` (string): Filter by end date (ISO format)

**Response:**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440004",
      "title": "Monthly Security Report",
      "type": "SECURITY",
      "format": "PDF",
      "status": "COMPLETED",
      "created_at": "2023-01-01T00:00:00Z",
      "updated_at": "2023-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

### Get Report by ID

```
GET /reports/{report_id}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440004",
  "title": "Monthly Security Report",
  "description": "Security report for January 2023",
  "type": "SECURITY",
  "format": "PDF",
  "status": "COMPLETED",
  "url": "https://example.com/reports/550e8400-e29b-41d4-a716-446655440004.pdf",
  "parameters": {
    "start_date": "2023-01-01",
    "end_date": "2023-01-31"
  },
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

### Generate Report

```
POST /reports/generate
```

**Request Body:**
```json
{
  "title": "Custom Security Report",
  "description": "Custom security report for specific timeframe",
  "type": "SECURITY",
  "format": "PDF",
  "parameters": {
    "start_date": "2023-01-01",
    "end_date": "2023-01-15",
    "include_alerts": true,
    "include_events": true
  }
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440005",
  "title": "Custom Security Report",
  "description": "Custom security report for specific timeframe",
  "type": "SECURITY",
  "format": "PDF",
  "status": "PENDING",
  "parameters": {
    "start_date": "2023-01-01",
    "end_date": "2023-01-15",
    "include_alerts": true,
    "include_events": true
  },
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

## Digital Twins

### Get Digital Twins

```
GET /digital-twins
```

**Query Parameters:**
- `skip` (integer): Number of items to skip (default: 0)
- `limit` (integer): Maximum number of items to return (default: 100)
- `status` (string): Filter by status (ACTIVE, INACTIVE)

**Response:**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440006",
      "name": "Production Server",
      "description": "Production web server",
      "type": "SERVER",
      "status": "ACTIVE",
      "created_at": "2023-01-01T00:00:00Z",
      "updated_at": "2023-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

### Get Digital Twin by ID

```
GET /digital-twins/{twin_id}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440006",
  "name": "Production Server",
  "description": "Production web server",
  "type": "SERVER",
  "status": "ACTIVE",
  "configuration": {
    "os": "Linux",
    "version": "Ubuntu 22.04",
    "services": ["nginx", "postgresql"]
  },
  "metrics": {
    "cpu_usage": 45.2,
    "memory_usage": 60.8,
    "disk_usage": 32.5
  },
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

## System Health

### Get Health Status

```
GET /health
```

**Response:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "timestamp": 1672531200,
  "components": {
    "database": "ok",
    "cache": "ok",
    "storage": "ok"
  }
}
```

## Error Responses

All API endpoints return standard error responses:

```json
{
  "detail": "Error message",
  "status_code": 400,
  "error_code": "ERROR_CODE"
}
```

### Common HTTP Status Codes

- `200 OK`: Request succeeded
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error
