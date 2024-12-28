"""
Seneschal Python Edition - Main Entry Point
"""
import sys
from PyQt6.QtWidgets import QApplication
from seneschal.main import Seneschal
from seneschal.utils.theme_manager import ThemeManager

def main():
    app = QApplication(sys.argv)
    
    # Apply theme
    ThemeManager.apply_theme(app)
    
    window = Seneschal()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
