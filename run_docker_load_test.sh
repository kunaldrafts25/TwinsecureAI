#!/bin/bash
# Script to run load tests using Docker Compose

# Default values
HEADLESS=false
USERS=10
SPAWN_RATE=1
DURATION=30

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --headless)
      HEADLESS=true
      shift
      ;;
    --users=*)
      USERS="${1#*=}"
      shift
      ;;
    --spawn-rate=*)
      SPAWN_RATE="${1#*=}"
      shift
      ;;
    --duration=*)
      DURATION="${1#*=}"
      shift
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

echo -e "\e[32mStarting TwinSecure load testing with Docker Compose...\e[0m"

# Check if locustfile.py exists
if [ ! -f "locustfile.py" ]; then
  echo -e "\e[33mlocustfile.py not found. Creating it...\e[0m"
  # The script will create it automatically
fi

# Start the containers
echo -e "\e[33mStarting Docker containers...\e[0m"
docker-compose -f docker-compose.load-test.yml up -d

# Wait for the backend to be ready
echo -e "\e[33mWaiting for backend to be ready...\e[0m"
sleep 10

if [ "$HEADLESS" = true ]; then
  # Run Locust in headless mode
  echo -e "\e[33mRunning Locust in headless mode...\e[0m"
  echo -e "\e[33mUsers: $USERS, Spawn Rate: $SPAWN_RATE, Duration: $DURATION seconds\e[0m"
  
  docker exec twinsecure_locust locust --headless -u $USERS -r $SPAWN_RATE -t ${DURATION}s --csv=load_test_results
  
  # Copy the results from the container
  echo -e "\e[33mCopying results from container...\e[0m"
  docker cp twinsecure_locust:/home/locust/load_test_results_stats.csv .
  docker cp twinsecure_locust:/home/locust/load_test_results_stats_history.csv .
  docker cp twinsecure_locust:/home/locust/load_test_results_failures.csv .
  
  echo -e "\e[32mLoad test completed. Results saved to load_test_results_*.csv\e[0m"
  
  # Stop the containers when done
  echo -e "\e[33mStopping Docker containers...\e[0m"
  docker-compose -f docker-compose.load-test.yml down
else
  # Run Locust in web mode
  echo -e "\e[32mLocust web interface is available at http://localhost:8089\e[0m"
  echo -e "\e[33mPress Ctrl+C to stop the containers when done\e[0m"
  
  # Open the browser if xdg-open is available
  if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:8089
  elif command -v open &> /dev/null; then
    open http://localhost:8089
  fi
  
  # Wait for user to press Ctrl+C
  trap "echo -e '\e[33mStopping Docker containers...\e[0m'; docker-compose -f docker-compose.load-test.yml down; exit 0" INT
  while true; do
    sleep 1
  done
fi
