"""
Seneschal Python Edition - Main Entry Point
"""
import ttkbootstrap
from seneschal.main import Seneschal
from seneschal.utils.theme_manager import ThemeManager

def main():
    # Use ttkbootstrap for modern theming
    app = ttkbootstrap.Window(themename="darkly")
    
    # Apply theme
    ThemeManager.apply_theme(app)
    
    window = Seneschal()
    window.mainloop()

if __name__ == '__main__':
    main()
