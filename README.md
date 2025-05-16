# TwinSecure

<p align="center">
  <img src="https://via.placeholder.com/200x200?text=TwinSecure" alt="TwinSecure Logo" width="200" height="200">
</p>

<p align="center">
  <strong>Advanced Cybersecurity Platform with Digital Twin Technology</strong>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#development">Development</a> •
  <a href="#testing">Testing</a> •
  <a href="#deployment">Deployment</a> •
  <a href="#monitoring">Monitoring</a> •
  <a href="#license">License</a>
</p>

---

## Overview

TwinSecure is a comprehensive cybersecurity platform that leverages digital twin technology and AI-driven honeypots to protect enterprises from cyber threats. The platform provides real-time monitoring, threat detection, and automated response capabilities through an intuitive dashboard.

## Features

- **Real-time Security Monitoring**: Monitor your network and systems in real-time
- **Threat Detection and Alerting**: AI-powered threat detection with customizable alerts
- **Digital Twin Security Management**: Secure digital representations of physical systems
- **User Authentication and Authorization**: Role-based access control system
- **Comprehensive Reporting**: Detailed security reports and analytics
- **Honeypot Integration**: Advanced threat intelligence through honeypot data
- **API-first Architecture**: Extensible API for integration with other systems
- **Interactive Dashboard**: Real-time visualization of security metrics

## Architecture

TwinSecure follows a modern microservices architecture:

- **Frontend**: React-based SPA with Vite, TypeScript, and Tailwind CSS
- **Backend**: FastAPI (Python) RESTful API with async support
- **Database**: PostgreSQL with table partitioning for performance
- **Monitoring**: Prometheus and Grafana for metrics and visualization
- **Logging**: Elasticsearch for centralized logging
- **Containerization**: Docker and Docker Compose for development and deployment

## Installation

### Prerequisites

- Docker and Docker Compose
- Git
- Node.js 20+ (for local frontend development)
- Python 3.11+ (for local backend development)
- PostgreSQL 15+ (for local database development)

### Quick Start with Docker

1. Clone the repository:
   ```bash
   git clone https://github.com/kunaldrafts25/TwinsecureAI.git
   cd TwinsecureAI
   ```

2. Start the application stack:
   ```bash
   docker-compose up -d
   ```

3. Access the application:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000/api/v1
   - API Documentation: http://localhost:8000/docs
   - PgAdmin: http://localhost:5050 (Email: admin@example.com, Password: admin)
   - Grafana: http://localhost:3001 (Username: admin, Password: admin)

### Manual Setup

#### Backend

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables (copy from .env.example):
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Run the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

#### Frontend

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install --legacy-peer-deps
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

## Usage

### Authentication

1. Default admin credentials:
   - Email: admin@finguard.com
   - Password: 123456789

2. After login, you'll be redirected to the dashboard.

### Dashboard

The dashboard provides:
- Security overview with key metrics
- Real-time alerts and notifications
- System health status
- Digital twin visualization
- Threat intelligence reports

### API Access

The API is accessible at `http://localhost:8000/api/v1` with comprehensive documentation available at `http://localhost:8000/docs`.

## Development

### Project Structure

```
twinsecure/
├── backend/               # FastAPI backend
│   ├── app/               # Application code
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Core functionality
│   │   ├── db/            # Database models and session
│   │   ├── models/        # Pydantic models
│   │   ├── schemas/       # Request/response schemas
│   │   ├── services/      # Business logic
│   │   └── main.py        # Application entry point
│   ├── alembic/           # Database migrations
│   ├── scripts/           # Utility scripts
│   ├── tests/             # Backend tests
│   └── requirements.txt   # Python dependencies
├── frontend/              # React frontend
│   ├── public/            # Static assets
│   ├── src/               # Source code
│   │   ├── components/    # React components
│   │   ├── features/      # Feature modules
│   │   ├── layouts/       # Page layouts
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   ├── store/         # State management
│   │   ├── utils/         # Utility functions
│   │   ├── App.tsx        # Main application component
│   │   └── main.tsx       # Entry point
│   ├── package.json       # Node.js dependencies
│   └── vite.config.ts     # Vite configuration
├── docker-compose.yml     # Docker Compose configuration
├── .env                   # Environment variables
└── README.md              # Project documentation
```

### Backend Development

- API endpoints are defined in `backend/app/api/`
- Database models are defined in `backend/app/models/`
- Business logic is implemented in `backend/app/services/`

### Frontend Development

- Components are organized by feature in `frontend/src/features/`
- Global state is managed with Zustand in `frontend/src/store/`
- API services are defined in `frontend/src/services/`

## Testing

### Backend Tests

```bash
cd backend
python -m pytest
```

For coverage report:
```bash
python -m pytest --cov=app --cov-report=html --cov-report=term
```

### Frontend Tests

```bash
cd frontend
npx vitest run
```

For specific test suites:
```bash
npx vitest run src/utils
npx vitest run src/components
```

## Deployment

### Docker Deployment

The recommended deployment method is using Docker Compose:

```bash
docker-compose -f docker-compose.yml up -d
```

### Production Considerations

For production deployment:
1. Use proper secrets management
2. Configure HTTPS with a reverse proxy (Nginx/Traefik)
3. Set up proper database backups
4. Configure monitoring alerts

## Monitoring

TwinSecure includes a comprehensive monitoring stack:

- **Prometheus**: Metrics collection at http://localhost:9090
- **Grafana**: Metrics visualization at http://localhost:3001
- **Elasticsearch**: Log aggregation at http://localhost:9200

## License

[MIT License](LICENSE)

---

<p align="center">
  Made with ❤️ by Your Team
</p>