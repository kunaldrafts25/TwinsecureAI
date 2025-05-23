"""
TwinSecure - Advanced Cybersecurity Platform
Copyright © 2024 TwinSecure. All rights reserved.

This file is part of TwinSecure, a proprietary cybersecurity platform.
Unauthorized copying, distribution, modification, or use of this software
is strictly prohibited without explicit written permission.

For licensing inquiries: kunalsingh2514@gmail.com
"""

#!/usr/bin/env python3
"""
Protected deployment script for TwinSecure.
This script creates a production-ready, protected version of the application.
"""

import os
import shutil
import subprocess
import zipfile
from pathlib import Path
import json
import hashlib


class ProtectedDeployment:
    """Handles creation of protected deployment packages."""
    
    def __init__(self):
        self.project_root = Path(".")
        self.dist_dir = Path("dist")
        self.protected_dir = Path("protected")
        
    def clean_directories(self):
        """Clean previous build artifacts."""
        for dir_path in [self.dist_dir, self.protected_dir]:
            if dir_path.exists():
                shutil.rmtree(dir_path)
            dir_path.mkdir(parents=True, exist_ok=True)
        print("Cleaned build directories")
    
    def copy_essential_files(self):
        """Copy only essential files for deployment."""
        essential_files = [
            "docker-compose.yml",
            "docker-compose.prod.yml", 
            "README.md",
            "LICENSE",
            ".env.example",
            "requirements.txt"
        ]
        
        for file_name in essential_files:
            src = self.project_root / file_name
            if src.exists():
                dst = self.protected_dir / file_name
                if src.is_file():
                    shutil.copy2(src, dst)
                else:
                    shutil.copytree(src, dst)
                print(f"Copied: {file_name}")
    
    def create_protected_backend(self):
        """Create protected backend with compiled bytecode."""
        backend_src = self.project_root / "backend"
        backend_dst = self.protected_dir / "backend"
        
        if not backend_src.exists():
            print("Backend directory not found")
            return
        
        # Copy structure but compile Python files
        for root, dirs, files in os.walk(backend_src):
            # Skip unwanted directories
            dirs[:] = [d for d in dirs if d not in ['__pycache__', 'venv', '.pytest_cache']]
            
            root_path = Path(root)
            rel_path = root_path.relative_to(backend_src)
            dst_root = backend_dst / rel_path
            dst_root.mkdir(parents=True, exist_ok=True)
            
            for file in files:
                src_file = root_path / file
                dst_file = dst_root / file
                
                if file.endswith('.py'):
                    # Compile to bytecode
                    try:
                        import py_compile
                        compiled_file = dst_root / (file + 'c')  # .pyc
                        py_compile.compile(src_file, compiled_file, doraise=True)
                        print(f"Compiled: {src_file}")
                    except Exception as e:
                        print(f"Error compiling {src_file}: {e}")
                        # Fallback: copy original file
                        shutil.copy2(src_file, dst_file)
                else:
                    # Copy non-Python files as-is
                    shutil.copy2(src_file, dst_file)
    
    def create_protected_frontend(self):
        """Create production build of frontend."""
        frontend_src = self.project_root / "frontend"
        frontend_dst = self.protected_dir / "frontend"
        
        if not frontend_src.exists():
            print("Frontend directory not found")
            return
        
        # Copy package.json and other config files
        config_files = ["package.json", "package-lock.json", "vite.config.ts", 
                       "tsconfig.json", "tailwind.config.js", "postcss.config.js"]
        
        frontend_dst.mkdir(parents=True, exist_ok=True)
        
        for config_file in config_files:
            src = frontend_src / config_file
            if src.exists():
                shutil.copy2(src, frontend_dst / config_file)
        
        # Copy src directory (will be built later)
        src_dir = frontend_src / "src"
        if src_dir.exists():
            shutil.copytree(src_dir, frontend_dst / "src")
        
        # Copy public directory
        public_dir = frontend_src / "public"
        if public_dir.exists():
            shutil.copytree(public_dir, frontend_dst / "public")
        
        print("Copied frontend files")
    
    def create_deployment_manifest(self):
        """Create deployment manifest with checksums."""
        manifest = {
            "name": "TwinSecure",
            "version": "1.0.0",
            "build_date": str(Path().stat().st_mtime),
            "protected": True,
            "license_required": True,
            "files": {}
        }
        
        # Calculate checksums for all files
        for root, dirs, files in os.walk(self.protected_dir):
            for file in files:
                file_path = Path(root) / file
                rel_path = file_path.relative_to(self.protected_dir)
                
                with open(file_path, 'rb') as f:
                    content = f.read()
                    checksum = hashlib.sha256(content).hexdigest()
                    manifest["files"][str(rel_path)] = {
                        "checksum": checksum,
                        "size": len(content)
                    }
        
        # Save manifest
        manifest_file = self.protected_dir / "deployment_manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print("Created deployment manifest")
    
    def create_docker_files(self):
        """Create production Docker files."""
        # Production Dockerfile for backend
        backend_dockerfile = '''FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (compiled bytecode)
COPY backend/ ./backend/

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
        
        with open(self.protected_dir / "Dockerfile.backend", 'w') as f:
            f.write(backend_dockerfile)
        
        # Production Dockerfile for frontend
        frontend_dockerfile = '''FROM node:18-alpine as builder

WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci --only=production

COPY frontend/ .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
'''
        
        with open(self.protected_dir / "Dockerfile.frontend", 'w') as f:
            f.write(frontend_dockerfile)
        
        print("Created production Docker files")
    
    def create_deployment_package(self):
        """Create final deployment package."""
        package_name = "twinsecure-protected-v1.0.0.zip"
        package_path = self.dist_dir / package_name
        
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.protected_dir):
                for file in files:
                    file_path = Path(root) / file
                    arc_name = file_path.relative_to(self.protected_dir)
                    zipf.write(file_path, arc_name)
        
        print(f"Created deployment package: {package_path}")
        return package_path
    
    def run(self):
        """Run the complete protection and deployment process."""
        print("Starting protected deployment process...")
        
        self.clean_directories()
        self.copy_essential_files()
        self.create_protected_backend()
        self.create_protected_frontend()
        self.create_docker_files()
        self.create_deployment_manifest()
        
        package_path = self.create_deployment_package()
        
        print("\n" + "="*50)
        print("PROTECTED DEPLOYMENT COMPLETE")
        print("="*50)
        print(f"Package: {package_path}")
        print(f"Size: {package_path.stat().st_size / 1024 / 1024:.2f} MB")
        print("\nDeployment Notes:")
        print("1. This package contains compiled bytecode for protection")
        print("2. A valid license key is required to run the application")
        print("3. Environment variables must be configured before deployment")
        print("4. Use the provided Docker files for containerized deployment")


if __name__ == "__main__":
    deployment = ProtectedDeployment()
    deployment.run()
