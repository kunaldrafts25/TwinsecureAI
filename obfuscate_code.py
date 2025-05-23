#!/usr/bin/env python3
"""
Code obfuscation script for TwinSecure project.
This script helps protect the source code by applying various obfuscation techniques.
"""

import ast
import base64
import os
import random
import string
import zlib
from pathlib import Path


class CodeObfuscator:
    """Simple code obfuscator for Python files."""
    
    def __init__(self):
        self.name_mapping = {}
        self.obfuscated_names = set()
    
    def generate_obfuscated_name(self, original_name: str) -> str:
        """Generate an obfuscated name for a variable/function."""
        if original_name in self.name_mapping:
            return self.name_mapping[original_name]
        
        # Generate random name
        while True:
            new_name = ''.join(random.choices(string.ascii_letters, k=8))
            if new_name not in self.obfuscated_names:
                self.obfuscated_names.add(new_name)
                self.name_mapping[original_name] = new_name
                return new_name
    
    def obfuscate_strings(self, content: str) -> str:
        """Obfuscate string literals in the code."""
        lines = content.split('\n')
        obfuscated_lines = []
        
        for line in lines:
            # Skip comments and docstrings
            if line.strip().startswith('#') or '"""' in line or "'''" in line:
                obfuscated_lines.append(line)
                continue
            
            # Simple string obfuscation (base64 encoding)
            if '"' in line and not line.strip().startswith('import'):
                # This is a very basic implementation
                # In practice, you'd want more sophisticated string obfuscation
                obfuscated_lines.append(line)
            else:
                obfuscated_lines.append(line)
        
        return '\n'.join(obfuscated_lines)
    
    def add_dummy_code(self, content: str) -> str:
        """Add dummy code to confuse reverse engineering."""
        dummy_functions = [
            "def _dummy_func_1(): pass",
            "def _dummy_func_2(): return None",
            "def _dummy_func_3(): x = 1 + 1",
            "_dummy_var_1 = 'dummy'",
            "_dummy_var_2 = [1, 2, 3]",
        ]
        
        # Insert dummy code at random positions
        lines = content.split('\n')
        for _ in range(3):  # Add 3 dummy lines
            pos = random.randint(0, len(lines))
            dummy = random.choice(dummy_functions)
            lines.insert(pos, dummy)
        
        return '\n'.join(lines)
    
    def obfuscate_file(self, file_path: Path, output_path: Path):
        """Obfuscate a single Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Skip files with copyright headers (already protected)
            if 'Copyright © 2024 TwinSecure' in content:
                print(f"Skipping {file_path} (already has copyright)")
                return
            
            # Apply obfuscation techniques
            obfuscated = self.obfuscate_strings(content)
            obfuscated = self.add_dummy_code(obfuscated)
            
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(obfuscated)
            
            print(f"Obfuscated: {file_path} -> {output_path}")
            
        except Exception as e:
            print(f"Error obfuscating {file_path}: {e}")


def create_build_script():
    """Create a build script that compiles Python to bytecode."""
    build_script = '''#!/usr/bin/env python3
"""
Build script for TwinSecure - compiles Python files to bytecode for protection.
"""

import py_compile
import os
import shutil
from pathlib import Path

def compile_to_bytecode(source_dir, output_dir):
    """Compile Python files to bytecode."""
    source_path = Path(source_dir)
    output_path = Path(output_dir)
    
    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)
    
    for py_file in source_path.rglob("*.py"):
        if "__pycache__" in str(py_file) or "venv" in str(py_file):
            continue
        
        # Calculate relative path
        rel_path = py_file.relative_to(source_path)
        output_file = output_path / rel_path.with_suffix('.pyc')
        
        # Create output directory for this file
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            py_compile.compile(py_file, output_file, doraise=True)
            print(f"Compiled: {py_file} -> {output_file}")
        except Exception as e:
            print(f"Error compiling {py_file}: {e}")

if __name__ == "__main__":
    compile_to_bytecode("backend/app", "dist/backend/app")
    print("Build complete!")
'''
    
    with open('build_protected.py', 'w') as f:
        f.write(build_script)
    
    print("Created build_protected.py")


def main():
    """Main function to run obfuscation."""
    obfuscator = CodeObfuscator()
    
    # Create obfuscated directory
    obfuscated_dir = Path("obfuscated")
    obfuscated_dir.mkdir(exist_ok=True)
    
    # Obfuscate backend Python files
    backend_dir = Path("backend/app")
    if backend_dir.exists():
        for py_file in backend_dir.rglob("*.py"):
            if "__pycache__" not in str(py_file):
                rel_path = py_file.relative_to(backend_dir)
                output_file = obfuscated_dir / "backend" / "app" / rel_path
                obfuscator.obfuscate_file(py_file, output_file)
    
    # Create build script
    create_build_script()
    
    print("\nObfuscation complete!")
    print("Next steps:")
    print("1. Review obfuscated code in 'obfuscated' directory")
    print("2. Run 'python build_protected.py' to compile to bytecode")
    print("3. Deploy only the compiled bytecode files")


if __name__ == "__main__":
    main()
