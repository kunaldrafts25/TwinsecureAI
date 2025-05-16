#!/bin/bash
# TwinSecure Setup Script
# This script helps set up the TwinSecure environment

# Default options
WITH_ML=false
DEV_MODE=false
FORCE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --with-ml)
      WITH_ML=true
      shift
      ;;
    --dev-mode)
      DEV_MODE=true
      shift
      ;;
    --force)
      FORCE=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Function to check if Python is installed
check_python() {
  if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo -e "\e[32mFound Python: $(python3 --version)\e[0m"
    return 0
  elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    echo -e "\e[32mFound Python: $(python --version)\e[0m"
    return 0
  else
    echo -e "\e[31mPython is not installed or not in PATH\e[0m"
    return 1
  fi
}

# Function to check if Docker is installed
check_docker() {
  if command -v docker &> /dev/null; then
    echo -e "\e[32mFound Docker: $(docker --version)\e[0m"
    return 0
  else
    echo -e "\e[31mDocker is not installed or not in PATH\e[0m"
    return 1
  fi
}

# Function to create a virtual environment
create_virtualenv() {
  if [ -d "venv" ]; then
    if [ "$FORCE" = true ]; then
      echo -e "\e[33mRemoving existing virtual environment...\e[0m"
      rm -rf venv
    else
      echo -e "\e[33mVirtual environment already exists. Use --force to recreate it.\e[0m"
      return
    fi
  fi
  
  echo -e "\e[33mCreating virtual environment...\e[0m"
  $PYTHON_CMD -m venv venv
  
  if [ $? -ne 0 ]; then
    echo -e "\e[31mFailed to create virtual environment\e[0m"
    exit 1
  fi
  
  echo -e "\e[32mVirtual environment created successfully\e[0m"
}

# Function to install dependencies
install_dependencies() {
  echo -e "\e[33mInstalling dependencies...\e[0m"
  
  # Activate virtual environment
  source venv/bin/activate
  
  # Upgrade pip, setuptools, and wheel
  $PYTHON_CMD -m pip install --upgrade pip setuptools wheel
  
  # Install backend dependencies
  cd backend
  pip install -r requirements.txt
  
  # Install ML dependencies if requested
  if [ "$WITH_ML" = true ]; then
    echo -e "\e[33mInstalling ML dependencies...\e[0m"
    pip install -r requirements-ml.txt
  fi
  
  # Install development dependencies if requested
  if [ "$DEV_MODE" = true ]; then
    echo -e "\e[33mInstalling development dependencies...\e[0m"
    pip install black flake8 isort pytest pytest-asyncio pytest-cov
  fi
  
  cd ..
  
  echo -e "\e[32mDependencies installed successfully\e[0m"
}

# Function to set up the database
setup_database() {
  echo -e "\e[33mSetting up the database...\e[0m"
  
  # Check if PostgreSQL is running in Docker
  PG_CONTAINER=$(docker ps -q -f "name=twinsecure_db")
  
  if [ -z "$PG_CONTAINER" ]; then
    echo -e "\e[33mStarting PostgreSQL container...\e[0m"
    docker-compose up -d db
    
    # Wait for PostgreSQL to start
    echo -e "\e[33mWaiting for PostgreSQL to start...\e[0m"
    sleep 10
  fi
  
  # Run database migrations
  cd backend
  
  # Activate virtual environment
  source ../venv/bin/activate
  
  # Run Alembic migrations
  echo -e "\e[33mRunning database migrations...\e[0m"
  alembic upgrade head
  
  cd ..
  
  echo -e "\e[32mDatabase setup completed successfully\e[0m"
}

# Main script
echo -e "\e[36mTwinSecure Setup Script\e[0m"
echo -e "\e[36m========================\e[0m"

# Check prerequisites
check_python
PYTHON_INSTALLED=$?

check_docker
DOCKER_INSTALLED=$?

if [ $PYTHON_INSTALLED -ne 0 ]; then
  echo -e "\e[31mPlease install Python 3.10+ and try again\e[0m"
  exit 1
fi

if [ $DOCKER_INSTALLED -ne 0 ]; then
  echo -e "\e[33mDocker is not installed. Database setup will be skipped.\e[0m"
  SETUP_DB=false
else
  SETUP_DB=true
fi

# Create virtual environment
create_virtualenv

# Install dependencies
install_dependencies

# Set up database if Docker is available
if [ "$SETUP_DB" = true ]; then
  setup_database
fi

echo -e "\e[32mSetup completed successfully!\e[0m"
echo -e "\e[33mTo activate the virtual environment, run:\e[0m"
echo -e "  source venv/bin/activate"

echo -e "\e[33mTo start the application, run:\e[0m"
echo -e "  docker-compose up"
