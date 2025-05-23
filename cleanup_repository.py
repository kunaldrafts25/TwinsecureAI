#!/usr/bin/env python3
"""
TwinSecure Repository Cleanup Script
Copyright © 2024 TwinSecure. All rights reserved.
Contact: kunalsingh2514@gmail.com

This script cleans up the repository by removing unnecessary files
and ensuring only essential files are tracked by git.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def run_command(cmd, check=True):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command '{cmd}': {e}")
        if check:
            sys.exit(1)
        return None

def remove_directory(path):
    """Safely remove a directory if it exists."""
    if os.path.exists(path):
        try:
            shutil.rmtree(path)
            print(f"✅ Removed: {path}")
        except Exception as e:
            print(f"❌ Failed to remove {path}: {e}")

def remove_file(path):
    """Safely remove a file if it exists."""
    if os.path.exists(path):
        try:
            os.remove(path)
            print(f"✅ Removed: {path}")
        except Exception as e:
            print(f"❌ Failed to remove {path}: {e}")

def main():
    """Main cleanup function."""
    print("🧹 Starting TwinSecure Repository Cleanup...")
    print("=" * 50)
    
    # Remove virtual environments
    print("\n📁 Removing Virtual Environments...")
    remove_directory("venv")
    remove_directory("backend/venv")
    
    # Remove node_modules
    print("\n📦 Removing Node Modules...")
    remove_directory("frontend/node_modules")
    
    # Remove log directories
    print("\n📝 Removing Log Directories...")
    remove_directory("logs")
    remove_directory("backend/logs")
    
    # Remove cache directories
    print("\n🗂️ Removing Cache Directories...")
    remove_directory("backend/app/__pycache__")
    remove_directory("backend/tests/__pycache__")
    
    # Find and remove all __pycache__ directories
    for root, dirs, files in os.walk("."):
        if "__pycache__" in dirs:
            pycache_path = os.path.join(root, "__pycache__")
            remove_directory(pycache_path)
    
    # Remove temporary documentation files
    print("\n📄 Removing Temporary Documentation...")
    temp_docs = [
        "CLEANUP_COMPLETE.md",
        "INDIAN_PRICING_UPDATE_COMPLETE.md"
    ]
    for doc in temp_docs:
        remove_file(doc)
    
    # Remove development files
    print("\n🔧 Removing Development Files...")
    dev_files = [
        "locustfile.py",
        "GeoLite2-City.mmdb"
    ]
    for file in dev_files:
        remove_file(file)
    
    # Git cleanup
    print("\n🔄 Git Cleanup...")
    
    # Add all changes to git
    print("Adding changes to git...")
    run_command("git add .")
    
    # Check git status
    print("\n📊 Current Git Status:")
    status = run_command("git status --porcelain", check=False)
    if status:
        print(status)
    else:
        print("✅ Working directory clean")
    
    print("\n" + "=" * 50)
    print("🎉 Repository Cleanup Complete!")
    print("\n📋 Summary:")
    print("✅ Virtual environments removed")
    print("✅ Node modules removed") 
    print("✅ Log directories removed")
    print("✅ Cache directories removed")
    print("✅ Temporary documentation removed")
    print("✅ Development files removed")
    print("✅ Git tracking updated")
    
    print("\n🚀 Your repository is now clean and ready!")
    print("📧 Contact: kunalsingh2514@gmail.com")

if __name__ == "__main__":
    main()
