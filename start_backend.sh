#!/bin/bash
# Script to start the backend server for load testing

echo -e "\e[32mStarting TwinSecure backend server for load testing...\e[0m"

# Set PYTHONPATH environment variable
export PYTHONPATH="$PWD"
echo -e "\e[33mPYTHONPATH set to: $PYTHONPATH\e[0m"

# Set environment variables for testing
export DOTENV_FILE=".env.test"
echo -e "\e[33mUsing test environment file: $DOTENV_FILE\e[0m"

# Set database to use SQLite instead of PostgreSQL
export TEST_DB="sqlite"
echo -e "\e[33mUsing SQLite database for testing\e[0m"

# Change to backend directory
cd backend

# Start the server with uvicorn
echo -e "\e[33mStarting uvicorn server on http://localhost:8000...\e[0m"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
