#!/bin/bash
# Script to run the health check test with proper environment setup

echo -e "\e[32mSetting up environment for health check test...\e[0m"

# Set PYTHONPATH environment variable
export PYTHONPATH="$PWD"
echo -e "\e[33mPYTHONPATH set to: $PYTHONPATH\e[0m"

# Set environment variables for testing
export DOTENV_FILE=".env.test"
echo -e "\e[33mUsing test environment file: $DOTENV_FILE\e[0m"

# Change to backend directory
cd backend

# Run the health check test
echo -e "\e[33mRunning health check test...\e[0m"
python -m pytest tests/test_health.py -v

# Return to the root directory
cd ..

echo -e "\e[32mHealth check test completed!\e[0m"
