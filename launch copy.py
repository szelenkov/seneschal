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
    try:
        import PyQt6
        import sqlalchemy
        import mysql.connector
        import psycopg2
        import pyodbc
        import cryptography
        import dotenv
        import qtawesome
        return True
    except ImportError as e:
        print(f"Missing dependency: {str(e)}")
        return False

def install_dependencies():
    """Install required dependencies"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", ".", "--use-pep517"])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {str(e)}")
        return False

def main():
    """Main entry point"""
    try:
        print("Starting application...")
        print("Checking dependencies...")
        if not check_dependencies():
            print("Installing dependencies...")
            if not install_dependencies():
                print("Failed to install dependencies. Please install manually.")
                return

        print("Importing required modules...")
        import sys
        from PyQt6.QtWidgets import QApplication
        from seneschal.main import Seneschal
        from seneschal.utils.theme_manager import ThemeManager
        
        print("Creating QApplication...")
        app = QApplication(sys.argv)
        
        print("Applying theme...")
        ThemeManager.apply_theme(app)
        
        print("Creating main window...")
        window = Seneschal()
        
        print("Showing window...")
        window.show()
        
        print("Starting event loop...")
        sys.exit(app.exec())
        
    except Exception as e:
        error_msg = f"""
Error launching Seneschal Python Edition:
{str(e)}

Traceback:
{traceback.format_exc()}

Python version: {sys.version}
Python path: {sys.path}
Current directory: {os.getcwd()}
"""
        print(error_msg)
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()
