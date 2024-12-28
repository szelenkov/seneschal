#!/usr/bin/env python3
"""
Seneschal Python Edition Launcher
This script helps identify startup issues
"""
import sys
import os
import traceback
import subprocess

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_deps = [
        'PyQt6', 'sqlalchemy', 'mysql.connector', 
        'psycopg2', 'pyodbc', 'cryptography', 
        'dotenv', 'qtawesome'
    ]
    missing_deps = []

    for dep in required_deps:
        try:
            __import__(dep.replace('-', '_').split()[0])
        except ImportError:
            missing_deps.append(dep)

    if missing_deps:
        print(f"Missing dependencies: {', '.join(missing_deps)}")
        return False
    return True

def install_dependencies():
    """Install required dependencies"""
    required_deps = [
        'PyQt6', 'sqlalchemy', 'mysql-connector-python', 
        'psycopg2', 'pyodbc', 'cryptography', 
        'python-dotenv', 'qtawesome'
    ]
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + required_deps)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {str(e)}")
        return False

def main():
    """Main entry point with enhanced debugging"""
    import sys
    import os
    import traceback
    
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
    print(f"Architecture: {sys.maxsize > 2**32 and '64-bit' or '32-bit'}")
    
    try:
        # Explicit import with error tracking
        print("Importing PyQt6...")
        from PyQt6 import QtWidgets, QtCore
        print(f"PyQt6 Version: {QtCore.QT_VERSION_STR}")
        print(f"Qt Runtime Version: {QtCore.QLibraryInfo.version().toString()}")
        
        print("Creating QApplication...")
        app = QtWidgets.QApplication(sys.argv)
        
        print("Importing Seneschal...")
        from seneschal.main import Seneschal
        from seneschal.utils.theme_manager import ThemeManager
        
        print("Applying theme...")
        ThemeManager.apply_theme(app)
        
        print("Creating main window...")
        window = Seneschal()
        window.show()
        
        print("Starting event loop...")
        sys.exit(app.exec())
        
    except Exception as e:
        error_log_path = os.path.join(os.path.dirname(__file__), 'launch_debug.log')
        with open(error_log_path, 'w') as error_file:
            error_file.write(f"""Seneschal Launch Detailed Error
Error: {str(e)}

Traceback:
{traceback.format_exc()}

System Details:
Python Version: {sys.version}
Python Executable: {sys.executable}
Python Path: {sys.path}
Platform: {sys.platform}
Architecture: {sys.maxsize > 2**32 and '64-bit' or '32-bit'}
""")
        
        print(f"Critical error logged to {error_log_path}")
        print("Detailed error information has been saved. Please check the log.")
        sys.exit(1)

if __name__ == "__main__":
    main()