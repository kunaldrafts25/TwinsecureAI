#!/usr/bin/env python3
"""
Script to add copyright headers to all source files in the TwinSecure project.
This helps establish ownership and legal protection.
"""

import os
import glob
from pathlib import Path

# Copyright header templates
PYTHON_HEADER = '''"""
TwinSecure - Advanced Cybersecurity Platform
Copyright © 2024 TwinSecure. All rights reserved.

This file is part of TwinSecure, a proprietary cybersecurity platform.
Unauthorized copying, distribution, modification, or use of this software
is strictly prohibited without explicit written permission.

For licensing inquiries: kunalsingh2514@gmail.com
"""

'''

TYPESCRIPT_HEADER = '''/*
 * TwinSecure - Advanced Cybersecurity Platform
 * Copyright © 2024 TwinSecure. All rights reserved.
 *
 * This file is part of TwinSecure, a proprietary cybersecurity platform.
 * Unauthorized copying, distribution, modification, or use of this software
 * is strictly prohibited without explicit written permission.
 *
 * For licensing inquiries: kunalsingh2514@gmail.com
 */

'''

def add_header_to_file(file_path, header):
    """Add copyright header to a file if it doesn't already exist."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if copyright header already exists
        if 'Copyright © 2024 TwinSecure' in content:
            print(f"Header already exists in {file_path}")
            return

        # Add header at the beginning
        new_content = header + content

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"Added header to {file_path}")

    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def main():
    """Main function to add headers to all relevant files."""

    # Python files
    python_patterns = [
        'backend/app/**/*.py',
        'backend/scripts/**/*.py',
        'backend/tests/**/*.py',
        '*.py'
    ]

    for pattern in python_patterns:
        for file_path in glob.glob(pattern, recursive=True):
            if '__pycache__' not in file_path and 'venv' not in file_path:
                add_header_to_file(file_path, PYTHON_HEADER)

    # TypeScript/JavaScript files
    ts_patterns = [
        'frontend/src/**/*.ts',
        'frontend/src/**/*.tsx',
        'frontend/src/**/*.js',
        'frontend/src/**/*.jsx'
    ]

    for pattern in ts_patterns:
        for file_path in glob.glob(pattern, recursive=True):
            if 'node_modules' not in file_path:
                add_header_to_file(file_path, TYPESCRIPT_HEADER)

if __name__ == "__main__":
    main()
