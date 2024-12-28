import sys
from PyQt6.QtWidgets import QApplication
from seneschal.utils.settings_manager import SettingsManager
from seneschal.utils.theme_manager import ThemeManager

def main():
    try:
        print("Starting test launch...")
        
        print("Creating QApplication...")
        app = QApplication(sys.argv)
        print("QApplication created successfully")
        
        print("Initializing SettingsManager...")
        settings = SettingsManager()
        print("SettingsManager initialized successfully")
        
        print("Applying theme...")
        ThemeManager.apply_theme(app)
        print("Theme applied successfully")
        
        print("Creating main window...")
        from seneschal.main import Seneschal
        window = Seneschal()
        print("Main window created successfully")
        
        print("Showing window...")
        window.show()
        print("Window shown successfully")
        
        print("Starting event loop...")
        return app.exec()
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
