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

### Quick Start with Setup Script

1. Clone the repository:
   ```bash
   git clone https://github.com/kunaldrafts25/TwinsecureAI.git
   cd TwinsecureAI
   ```

2. Run the setup script:

   **Windows (PowerShell):**
   ```powershell
   .\setup.ps1
   ```

   **Linux/macOS:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

   Options:
   - `--with-ml` or `-WithML`: Install ML dependencies
   - `--dev-mode` or `-DevMode`: Install development dependencies
   - `--force` or `-Force`: Force recreation of virtual environment

3. Start the application stack:
   ```bash
   docker-compose up -d
   ```

4. Access the application:
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
   # Install core dependencies
   pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt

   # Optional: Install ML dependencies
   pip install -r requirements-ml.txt
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

You can use the provided test scripts to run tests with the correct environment setup:

**Quick Health Check Test:**

This is the simplest way to verify that the basic functionality is working:

**Windows (PowerShell):**
```powershell
# Run health check test
.\run_health_test.ps1
```

**Linux/macOS:**
```bash
# Make the script executable
chmod +x run_health_test.sh

# Run health check test
./run_health_test.sh
```

**Full Test Suite:**

For running the complete test suite or specific tests:

**Windows (PowerShell):**
```powershell
# Run health check tests
.\run_tests.ps1 -Health -Verbose

# Run auth tests
.\run_tests.ps1 -Auth -Verbose

# Run all tests with coverage
.\run_tests.ps1 -All -Coverage -Verbose
```

**Linux/macOS:**
```bash
# Make the script executable
chmod +x run_tests.sh

# Run health check tests
./run_tests.sh --health --verbose

# Run auth tests
./run_tests.sh --auth --verbose

# Run all tests with coverage
./run_tests.sh --all --coverage --verbose
```

**Manual Testing:**
```bash
cd backend
# Set PYTHONPATH to include the current directory
export PYTHONPATH=$PYTHONPATH:$(pwd)  # On Windows: $env:PYTHONPATH = "$env:PYTHONPATH;$(pwd)"

# Use test environment
export DOTENV_FILE=".env.test"  # On Windows: $env:DOTENV_FILE = ".env.test"

# Run all tests
python -m pytest

# Generate coverage report
python -m pytest --cov=app --cov-report=html --cov-report=term

# Run specific tests
python -m pytest tests/test_health.py -v
python -m pytest tests/test_api_auth.py -v
```

**Database Testing:**

For tests that require a PostgreSQL database:

1. Make sure PostgreSQL is running
2. Set the following environment variables:
   ```bash
   export TEST_DB=postgres
   export TEST_PG_HOST=localhost
   export TEST_PG_PORT=5432
   export TEST_PG_USER=postgres
   export TEST_PG_PASSWORD=kUNAL@#$12345
   export TEST_PG_DB=test_twinsecure
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

## Load Testing

TwinSecure includes tools for load testing the backend API:

### Running Load Tests Locally

**Prerequisites:**
- Python 3.10+ with pip
- Locust (`pip install locust`)

**Windows (PowerShell):**
```powershell
# Start the backend server in one terminal
.\start_backend.ps1

# Run load tests in another terminal
.\run_load_test.ps1 -Users 10 -Duration 30
```

**Linux/macOS:**
```bash
# Make the scripts executable
chmod +x start_backend.sh run_load_test.sh

# Start the backend server in one terminal
./start_backend.sh

# Run load tests in another terminal
./run_load_test.sh --users=10 --duration=30
```

### Running Load Tests with Docker Compose

```bash
# Create the locustfile.py if it doesn't exist
touch locustfile.py

# Start the backend and Locust
docker-compose -f docker-compose.load-test.yml up -d

# Access the Locust web interface
# Open http://localhost:8089 in your browser
```

### Interpreting Load Test Results

The load tests generate CSV files with the results:
- `load_test_results_stats.csv`: Overall statistics
- `load_test_results_stats_history.csv`: Statistics over time
- `load_test_results_failures.csv`: Failed requests

You can visualize these results using tools like Excel, Python with Pandas/Matplotlib, or import them into Grafana.

## License

[MIT License](LICENSE)

---

<p align="center">
  Made with ❤️ by Our Team
</p>