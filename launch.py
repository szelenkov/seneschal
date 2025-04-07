#!/usr/bin/env python3
"""
Seneschal Python Edition Launcher
This script helps identify startup issues
"""
import sys
import traceback
import subprocess

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_deps = [
        'sqlalchemy', 'mysql-connector-python', 'psycopg2-binary', 'pyodbc',
        'cryptography', 'python-dotenv', 'configparser'
    ]
    missing_deps = []

    for dep in required_deps:
        try:
            parts = dep.replace('-', ' ').split()
            __import__(parts[0] if parts[0] != 'python' else parts[1])
        except ImportError:
            missing_deps.append(dep)

    if missing_deps:
        print(f"Missing dependencies: {', '.join(missing_deps)}")
        return False
    return True

def install_dependencies():
    """Install required dependencies"""
    required_deps = [
        'sqlalchemy', 'mysql-connector-python', 'psycopg2-binary', 'pyodbc',
        'cryptography', 'python-dotenv', 'configparser'
    ]
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + required_deps)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {str(e)}")
        return False

def main():
    """Main entry point with enhanced debugging"""

    # Dependency Check
    print("Checking dependencies...")
    if not check_dependencies():
        print("Attempting to install missing dependencies...")
        if not install_dependencies():
            print("Critical: Unable to install required dependencies.")
            print("Please run 'pip install -r requirements.txt' manually.")
            sys.exit(1)

    # Print detailed system information
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print(f"Python Path: {sys.path}")
    print(f"Platform: {sys.platform}")
    print(f"Architecture: {sys.maxsize > 2**32 and '64' or '32'}-bit")

    try:
        print("Importing Seneschal...")
        from seneschal.main import Seneschal

        print("Creating main window...")
        window = Seneschal()


        print("Starting application main loop...")
        window.mainloop()
        
    except Exception as e:
        print("Error during application startup: ", e)
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
