from PyQt6.QtCore import QSettings, QObject, pyqtSignal
from PyQt6.QtGui import QFont, QColor

class SettingsManager(QObject):
    settings_changed = pyqtSignal(str, object)  # section, value

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SettingsManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        super().__init__()
        self.settings = QSettings('Seneschal', 'Python')
        self._initialized = True
        self._load_defaults()

    def _load_defaults(self):
        """Set default values for settings if they don't exist"""
        defaults = {
            'general/language': 'English',
            'general/theme': 'Light',
            'editor/font_family': 'Consolas',
            'editor/font_size': 10,
            'editor/auto_complete': True,
            'editor/word_wrap': True,
            'editor/tab_size': 4,
            'editor/use_spaces': True,
            'editor/highlight_current_line': True,
            'editor/show_line_numbers': True,
            'data/max_rows': 1000,
            'data/null_display': 'NULL',
            'data/auto_commit': False,
            'data/batch_size': 1000,
            'connection/history_size': 10,
            'connection/save_passwords': False,
            'logging/level': 'INFO',
            'logging/file_enabled': True,
            'logging/console_enabled': True
        }

        for key, default_value in defaults.items():
            if not self.settings.contains(key):
                self.settings.setValue(key, default_value)

    def get(self, key, default=None):
        """Get a setting value"""
        return self.settings.value(key, default)

    def set(self, key, value):
        """Set a setting value and emit signal"""
        self.settings.setValue(key, value)
        section = key.split('/')[0]
        self.settings_changed.emit(section, value)

    def get_editor_font(self):
        """Get the configured editor font"""
        font = QFont(
            self.get('editor/font_family', 'Consolas'),
            int(self.get('editor/font_size', 10))
        )
        return font

    def get_theme_colors(self):
        """Get the current theme colors"""
        theme = self.get('general/theme', 'Light')
        
        if theme == 'Dark':
            return {
                'background': QColor('#2b2b2b'),
                'foreground': QColor('#a9b7c6'),
                'selection': QColor('#214283'),
                'line_number': QColor('#606366'),
                'current_line': QColor('#323232'),
                'keyword': QColor('#cc7832'),
                'string': QColor('#6a8759'),
                'number': QColor('#6897bb'),
                'comment': QColor('#808080')
            }
        else:  # Light theme
            return {
                'background': QColor('#ffffff'),
                'foreground': QColor('#000000'),
                'selection': QColor('#add6ff'),
                'line_number': QColor('#999999'),
                'current_line': QColor('#fffae3'),
                'keyword': QColor('#0000ff'),
                'string': QColor('#008000'),
                'number': QColor('#0000ff'),
                'comment': QColor('#808080')
            }

    def get_logging_config(self):
        """Get logging configuration"""
        return {
            'level': self.get('logging/level', 'INFO'),
            'file_enabled': bool(self.get('logging/file_enabled', True)),
            'console_enabled': bool(self.get('logging/console_enabled', True))
        }

    def get_connection_settings(self):
        """Get connection-related settings"""
        return {
            'history_size': int(self.get('connection/history_size', 10)),
            'save_passwords': bool(self.get('connection/save_passwords', False))
        }

    def get_editor_settings(self):
        """Get all editor-related settings"""
        return {
            'font_family': self.get('editor/font_family', 'Consolas'),
            'font_size': int(self.get('editor/font_size', 10)),
            'auto_complete': bool(self.get('editor/auto_complete', True)),
            'word_wrap': bool(self.get('editor/word_wrap', True)),
            'tab_size': int(self.get('editor/tab_size', 4)),
            'use_spaces': bool(self.get('editor/use_spaces', True)),
            'highlight_current_line': bool(self.get('editor/highlight_current_line', True)),
            'show_line_numbers': bool(self.get('editor/show_line_numbers', True))
        }

    def get_data_settings(self):
        """Get all data-related settings"""
        return {
            'max_rows': int(self.get('data/max_rows', 1000)),
            'null_display': self.get('data/null_display', 'NULL'),
            'auto_commit': bool(self.get('data/auto_commit', False)),
            'batch_size': int(self.get('data/batch_size', 1000))
        }

    def clear_section(self, section):
        """Clear all settings in a section"""
        self.settings.beginGroup(section)
        self.settings.remove('')  # removes all keys in group
        self.settings.endGroup()
        self._load_defaults()  # reload defaults
        self.settings_changed.emit(section, None)
