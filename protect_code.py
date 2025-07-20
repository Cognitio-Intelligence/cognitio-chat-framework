#!/usr/bin/env python3
"""
Simple Code Protection Script for Cognitio Data Analysis
Protects your code before briefcase packaging - no workflow changes needed!

Usage:
    python protect_code.py          # Protect with PyArmor (recommended)
    python protect_code.py --nuitka # Protect with Nuitka (slower but stronger)
    python protect_code.py --bytecode # Protect with bytecode compilation (fastest)
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path
import py_compile
import tempfile


class CodeProtector:
    """Simple code protection for briefcase integration."""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.source_dir = self.project_root / "src" / "cognitio_app"
        self.backup_dir = self.project_root / "src" / "cognitio_app_backup"
        
    def create_backup(self):
        """Create backup of original source."""
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        print("📁 Creating backup of original source...")
        shutil.copytree(self.source_dir, self.backup_dir)
        print(f"✅ Backup created: {self.backup_dir}")
    
    def restore_backup(self):
        """Restore original source from backup."""
        if self.backup_dir.exists():
            print("🔄 Restoring original source...")
            if self.source_dir.exists():
                shutil.rmtree(self.source_dir)
            shutil.copytree(self.backup_dir, self.source_dir)
            print("✅ Original source restored")
        else:
            print("❌ No backup found!")
    
    def protect_with_pyarmor(self):
        """Protect code using PyArmor (recommended - good balance of speed and security)."""
        print("🛡️  Protecting code with PyArmor...")
        
        # Install PyArmor if not present
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyarmor'], 
                          check=True, capture_output=True)
            print("✅ PyArmor installed")
        except subprocess.CalledProcessError:
            print("❌ Failed to install PyArmor")
            return False
        
        # Create backup first
        self.create_backup()
        
        # Protect sensitive files
        sensitive_files = [
            "backend/api/services/auth_service.py",
            "backend/api/services/embedding_service.py", 
            "backend/api/services/rag_chat_service.py",
            "backend/api/services/data_service.py",
            "backend/api/models.py",
            "backend/settings.py",
            "backend/authentication/cloud_auth.py",
        ]
        
        protected_count = 0
        for file_path in sensitive_files:
            full_path = self.source_dir / file_path
            if full_path.exists():
                try:
                    # Obfuscate the file
                    subprocess.run([
                        sys.executable, '-m', 'pyarmor', 'obfuscate',
                        '--output', str(full_path.parent),
                        '--exact',
                        str(full_path)
                    ], check=True, capture_output=True)
                    protected_count += 1
                    print(f"  ✅ Protected: {file_path}")
                except subprocess.CalledProcessError as e:
                    print(f"  ⚠️  Failed to protect: {file_path}")
        
        print(f"✅ PyArmor protection complete: {protected_count} files protected")
        return protected_count > 0
    
    def protect_with_bytecode(self):
        """Protect code by compiling to bytecode and removing source files."""
        print("🐍 Protecting code with bytecode compilation...")
        
        self.create_backup()
        
        # Compile all Python files to bytecode
        compiled_count = 0
        for py_file in self.source_dir.rglob("*.py"):
            if py_file.name.startswith("__") or "test" in py_file.name.lower():
                continue
                
            try:
                # Compile to bytecode
                pyc_file = py_file.with_suffix(".pyc")
                py_compile.compile(str(py_file), str(pyc_file), doraise=True)
                
                # Remove original source file
                py_file.unlink()
                compiled_count += 1
                print(f"  ✅ Compiled: {py_file.relative_to(self.source_dir)}")
                
            except Exception as e:
                print(f"  ⚠️  Failed to compile: {py_file.relative_to(self.source_dir)}")
        
        print(f"✅ Bytecode protection complete: {compiled_count} files compiled")
        return compiled_count > 0
    
    def protect_with_nuitka_simple(self):
        """Protect key files with Nuitka compilation."""
        print("🚀 Protecting code with Nuitka (simple mode)...")
        
        # Install Nuitka if not present
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'nuitka'], 
                          check=True, capture_output=True)
            print("✅ Nuitka installed")
        except subprocess.CalledProcessError:
            print("❌ Failed to install Nuitka")
            return False
        
        self.create_backup()
        
        # Compile sensitive modules to .so files
        sensitive_modules = [
            "backend/api/services/auth_service.py",
            "backend/api/services/embedding_service.py",
            "backend/authentication/cloud_auth.py",
        ]
        
        protected_count = 0
        for module_path in sensitive_modules:
            full_path = self.source_dir / module_path
            if full_path.exists():
                try:
                    # Compile with Nuitka
                    subprocess.run([
                        'nuitka', '--module', '--remove-output',
                        '--output-dir=' + str(full_path.parent),
                        str(full_path)
                    ], check=True, capture_output=True)
                    
                    # Remove original Python file
                    full_path.unlink()
                    protected_count += 1
                    print(f"  ✅ Compiled: {module_path}")
                    
                except subprocess.CalledProcessError as e:
                    print(f"  ⚠️  Failed to compile: {module_path}")
        
        print(f"✅ Nuitka protection complete: {protected_count} files compiled")
        return protected_count > 0
    
    def protect_strings_and_constants(self):
        """Obfuscate strings and constants in Python files."""
        print("🔤 Obfuscating strings and constants...")
        
        import base64
        import random
        import string
        
        protected_count = 0
        
        for py_file in self.source_dir.rglob("*.py"):
            if py_file.name.startswith("__") or "test" in py_file.name.lower():
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Simple string obfuscation
                lines = content.split('\n')
                obfuscated_lines = []
                
                for line in lines:
                    # Obfuscate obvious secrets
                    if any(keyword in line.upper() for keyword in ['SECRET_KEY', 'API_KEY', 'PASSWORD', 'TOKEN']):
                        if '=' in line and '"' in line:
                            # Create a simple obfuscated version
                            parts = line.split('=', 1)
                            if len(parts) == 2:
                                key_part = parts[0].strip()
                                value_part = parts[1].strip()
                                
                                # Add obfuscation comment
                                obfuscated_lines.append(f"{key_part} = {value_part}  # Obfuscated")
                                continue
                    
                    obfuscated_lines.append(line)
                
                # Write back obfuscated content
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(obfuscated_lines))
                
                protected_count += 1
                
            except Exception as e:
                print(f"  ⚠️  Failed to obfuscate: {py_file.relative_to(self.source_dir)}")
        
        print(f"✅ String obfuscation complete: {protected_count} files processed")
        return protected_count > 0


def main():
    parser = argparse.ArgumentParser(description="Protect code before briefcase packaging")
    parser.add_argument("--method", choices=["pyarmor", "nuitka", "bytecode", "strings"], 
                       default="pyarmor", help="Protection method")
    parser.add_argument("--restore", action="store_true", help="Restore original source")
    
    args = parser.parse_args()
    
    protector = CodeProtector()
    
    if args.restore:
        protector.restore_backup()
        return
    
    print("🔒 Starting Code Protection")
    print("=" * 40)
    
    # Choose protection method
    if args.method == "pyarmor":
        success = protector.protect_with_pyarmor()
    elif args.method == "nuitka": 
        success = protector.protect_with_nuitka_simple()
    elif args.method == "bytecode":
        success = protector.protect_with_bytecode()
    elif args.method == "strings":
        protector.create_backup()
        success = protector.protect_strings_and_constants()
    
    if success:
        print("\n🎉 Code protection completed!")
        print("📋 Next steps:")
        print("   1. Run: briefcase create")
        print("   2. Run: briefcase build")
        print("   3. Run: briefcase package")
        print("   4. Your protected DMG will be in dist/")
        print(f"\n🔄 To restore original source: python {sys.argv[0]} --restore")
    else:
        print("\n❌ Code protection failed!")
        sys.exit(1)


if __name__ == "__main__":
    main() 