#!/bin/bash
# Script to run tests with proper PYTHONPATH and coverage

# Default options
ALL=false
HEALTH=false
AUTH=false
COVERAGE=false
VERBOSE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --all)
      ALL=true
      shift
      ;;
    --health)
      HEALTH=true
      shift
      ;;
    --auth)
      AUTH=true
      shift
      ;;
    --coverage)
      COVERAGE=true
      shift
      ;;
    --verbose)
      VERBOSE=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

echo -e "\e[33mSetting up environment for tests...\e[0m"

# Set PYTHONPATH environment variable
export PYTHONPATH="$PWD"
echo -e "\e[33mPYTHONPATH set to: $PYTHONPATH\e[0m"

# Change to backend directory
cd backend

# Build the test command
TEST_COMMAND="python -m pytest"

# Add test targets
if [ "$HEALTH" = true ]; then
  TEST_COMMAND="$TEST_COMMAND tests/test_health.py"
elif [ "$AUTH" = true ]; then
  TEST_COMMAND="$TEST_COMMAND tests/test_api_auth.py"
elif [ "$ALL" = true ]; then
  TEST_COMMAND="$TEST_COMMAND tests/"
else
  # Default to health test if no specific test is specified
  TEST_COMMAND="$TEST_COMMAND tests/test_health.py"
fi

# Add verbose flag if requested
if [ "$VERBOSE" = true ]; then
  TEST_COMMAND="$TEST_COMMAND -v"
fi

# Add coverage flags if requested
if [ "$COVERAGE" = true ]; then
  TEST_COMMAND="$TEST_COMMAND --cov=app --cov-report=xml --cov-report=term"
fi

# Run the tests
echo -e "\e[32mRunning tests with command: $TEST_COMMAND\e[0m"
eval "$TEST_COMMAND"

# Return to the root directory
cd ..

echo -e "\e[32mTests completed!\e[0m"
