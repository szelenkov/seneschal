def test_imports():
    try:
        print("Testing PyQt6 imports...")
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QSettings
        print("PyQt6 imports successful")
        
        print("\nTesting SettingsManager import...")
        from seneschal.utils.settings_manager import SettingsManager
        print("SettingsManager import successful")
        print("Creating SettingsManager instance...")
        settings = SettingsManager()
        print("SettingsManager instance created successfully")
        
        print("\nTesting ThemeManager import...")
        from seneschal.utils.theme_manager import ThemeManager
        print("ThemeManager import successful")
        
        print("\nTesting DatabaseBrowser import...")
        from seneschal.browser.database_browser import DatabaseBrowser
        print("DatabaseBrowser import successful")
        
        print("\nTesting QueryEditor import...")
        from seneschal.editors.query_editor import QueryEditor
        print("QueryEditor import successful")
        
        print("\nAll imports successful!")
        return 0
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(test_imports())
