"""
Run load tests with Locust.
This script runs load tests using Locust and generates a report.
"""
import os
import sys
import time
import json
import subprocess
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Default values
DEFAULT_HOST = "http://localhost:8000"
DEFAULT_USERS = 10
DEFAULT_SPAWN_RATE = 1
DEFAULT_RUN_TIME = "1m"
DEFAULT_REPORT_DIR = "load_test_reports"

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run load tests with Locust")
    parser.add_argument("--host", default=DEFAULT_HOST, help=f"Host to load test (default: {DEFAULT_HOST})")
    parser.add_argument("--users", type=int, default=DEFAULT_USERS, help=f"Number of users to simulate (default: {DEFAULT_USERS})")
    parser.add_argument("--spawn-rate", type=int, default=DEFAULT_SPAWN_RATE, help=f"Rate at which users are spawned (default: {DEFAULT_SPAWN_RATE})")
    parser.add_argument("--run-time", default=DEFAULT_RUN_TIME, help=f"Duration of the test (default: {DEFAULT_RUN_TIME})")
    parser.add_argument("--report-dir", default=DEFAULT_REPORT_DIR, help=f"Directory to store reports (default: {DEFAULT_REPORT_DIR})")
    parser.add_argument("--tags", help="Comma-separated list of tags to include")
    parser.add_argument("--exclude-tags", help="Comma-separated list of tags to exclude")
    parser.add_argument("--csv", action="store_true", help="Generate CSV report")
    parser.add_argument("--html", action="store_true", help="Generate HTML report")
    parser.add_argument("--json", action="store_true", help="Generate JSON report")
    return parser.parse_args()

def check_locust_installed():
    """Check if Locust is installed."""
    try:
        import locust
        return True
    except ImportError:
        logger.error("Locust is not installed. Please install it with 'pip install locust'.")
        return False

def start_api_server():
    """Start the API server for testing."""
    logger.info("Starting API server...")
    process = subprocess.Popen(
        ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(Path(__file__).parent.parent)
    )
    # Wait for server to start
    time.sleep(5)
    return process

def stop_api_server(process):
    """Stop the API server."""
    logger.info("Stopping API server...")
    process.terminate()
    process.wait()

def run_load_test(args):
    """Run load tests with Locust."""
    # Create report directory if it doesn't exist
    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate timestamp for report files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Build Locust command
    cmd = [
        "locust",
        "-f", str(Path(__file__).parent / "locustfile.py"),
        "--headless",
        "--host", args.host,
        "--users", str(args.users),
        "--spawn-rate", str(args.spawn_rate),
        "--run-time", args.run_time
    ]
    
    # Add tags if specified
    if args.tags:
        cmd.extend(["--tags", args.tags])
    
    # Add exclude-tags if specified
    if args.exclude_tags:
        cmd.extend(["--exclude-tags", args.exclude_tags])
    
    # Add CSV output if requested
    if args.csv:
        csv_prefix = str(report_dir / f"load_test_{timestamp}")
        cmd.extend(["--csv", csv_prefix])
    
    # Add HTML output if requested
    if args.html:
        html_file = str(report_dir / f"load_test_{timestamp}.html")
        cmd.extend(["--html", html_file])
    
    # Run Locust
    logger.info(f"Running Locust with command: {' '.join(cmd)}")
    process = subprocess.run(cmd, capture_output=True, text=True)
    
    # Check if Locust ran successfully
    if process.returncode != 0:
        logger.error(f"Locust failed with return code {process.returncode}")
        logger.error(f"Error: {process.stderr}")
        return False
    
    # Generate JSON report if requested
    if args.json:
        json_file = report_dir / f"load_test_{timestamp}.json"
        try:
            # Parse statistics from Locust output
            stats = {}
            for line in process.stdout.splitlines():
                if "Aggregated" in line and "|" in line:
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) >= 7:
                        stats["total_requests"] = int(parts[2].replace(",", ""))
                        stats["failure_rate"] = float(parts[3].replace("%", ""))
                        stats["avg_response_time"] = float(parts[4])
                        stats["min_response_time"] = float(parts[5])
                        stats["max_response_time"] = float(parts[6])
            
            # Save statistics to JSON file
            with open(json_file, "w") as f:
                json.dump({
                    "timestamp": timestamp,
                    "host": args.host,
                    "users": args.users,
                    "spawn_rate": args.spawn_rate,
                    "run_time": args.run_time,
                    "tags": args.tags,
                    "exclude_tags": args.exclude_tags,
                    "stats": stats
                }, f, indent=2)
            
            logger.info(f"JSON report saved to {json_file}")
        except Exception as e:
            logger.error(f"Failed to generate JSON report: {e}")
    
    logger.info("Load test completed successfully")
    return True

def main():
    """Main function."""
    # Parse command line arguments
    args = parse_args()
    
    # Check if Locust is installed
    if not check_locust_installed():
        return 1
    
    # Start API server if host is localhost
    api_server = None
    if "localhost" in args.host or "127.0.0.1" in args.host:
        api_server = start_api_server()
    
    try:
        # Run load test
        success = run_load_test(args)
        return 0 if success else 1
    finally:
        # Stop API server if it was started
        if api_server:
            stop_api_server(api_server)

if __name__ == "__main__":
    sys.exit(main())
