import configparser
import logging
import os
import sys
import threading
import tkinter.font as tkfont
import traceback

# Configure logging at the module level
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # Log to console
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'settings_manager.log'), mode='w')  # Log to file, overwrite each run
    ]
)
logger = logging.getLogger(__name__)

# Add error logging function
def log_exception(e):
    """Log detailed exception information"""
    logger.error(f"Exception Type: {type(e).__name__}")
    logger.error(f"Exception Message: {str(e)}")
    logger.error("Full Traceback:")
    for line in traceback.format_exc().splitlines():
        logger.error(line)

editor_font_family = 'editor/font_family'
editor_font_size = 'editor/font_size'


class SettingsManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        logger.debug(f"__new__ method called. Current instance: {cls._instance}")
        if not cls._instance:
            with cls._lock:
                # Another thread could have created the instance 
                # before we acquired the lock.
                if not cls._instance:
                    logger.debug(f"Creating new instance of {cls.__name__}")
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Prevent multiple initializations of settings
        if not hasattr(self, '_settings_initialized'):
            try:
                logger.debug(f"Initialization start. Thread: {threading.current_thread().name}")

                # Create a list to store change listeners
                self._change_listeners = []

                # Create configparser with comprehensive error handling
                try:
                    # Ensure settings are created only once
                    if not hasattr(self, 'settings'):
                        self.settings = configparser.ConfigParser()
                        
                        # Try to read existing settings, create if not exists
                        settings_file = 'settings.ini'
                        if os.path.exists(settings_file):
                            self.settings.read(settings_file)
                        else:
                            # Create an empty settings file if it doesn't exist
                            with open(settings_file, 'w'):
                                pass
                        
                        logger.debug(f"ConfigParser created. Storage location: {settings_file}")
                    
                    # Load defaults if not already loaded
                    if not hasattr(self, '_defaults_loaded'):
                        logger.debug("Attempting to load defaults")
                        self._load_defaults()
                        self._defaults_loaded = True

                    # Mark initialization as complete
                    self._settings_initialized = True
                    logger.debug("Initialization complete")
                    
                except Exception as settings_err:
                    log_exception(settings_err)
                    raise

            except Exception as e:
                log_exception(e)
                raise
        else:
            logger.debug("Settings already initialized, skipping")

    def add_change_listener(self, listener):
        """
        Add a listener function that will be called when settings change
        
        :param listener: A function that takes (section, key, value) as arguments
        """
        self._change_listeners.append(listener)

    def _load_defaults(self):
        """Set default values for settings if they don't exist"""
        try:
            logger.debug("Entering _load_defaults()")
            defaults = {
                'general/language': 'English',
                'general/theme': 'Light',
                editor_font_family: 'Consolas',
                editor_font_size: '10',
                'editor/auto_complete': 'True',
                'editor/word_wrap': 'True',
                'editor/tab_size': '4',
                'editor/use_spaces': 'True',
                'editor/highlight_current_line': 'True',
                'editor/show_line_numbers': 'True',
                'data/max_rows': '1000',
                'data/null_display': 'NULL',
                'data/auto_commit': 'False',
                'data/batch_size': '1000',
                'connection/history_size': '10',
                'connection/save_passwords': 'False',
                'logging/level': 'INFO',
                'logging/file_enabled': 'True',
                'logging/console_enabled': 'True'
            }

            logger.debug("Defaults dictionary created")
            for key, default_value in defaults.items():
                section, option = key.split('/', 1)
                
                # Ensure section exists
                if not self.settings.has_section(section):
                    self.settings.add_section(section)
                
                # Only set if option doesn't exist
                if not self.settings.has_option(section, option):
                    logger.debug(f"Setting default for {key}: {default_value}")
                    self.settings.set(section, option, default_value)
            
            # Write defaults to file
            with open('settings.ini', 'w') as configfile:
                self.settings.write(configfile)
            
            logger.debug("Defaults loaded successfully")
        
        except Exception as e:
            log_exception(e)
            raise

    def get(self, key, default=None):
        """Get a setting value"""
        try:
            section, option = key.split('/', 1)
            return self.settings.get(section, option, fallback=default)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return default

    def set(self, key, value):
        """Set a setting value and notify listeners"""
        try:
            # Split the key into section and option
            section, option = key.split('/', 1)
            
            # Ensure the section exists
            if not self.settings.has_section(section):
                self.settings.add_section(section)
            
            # Convert value to string for ConfigParser
            str_value = str(value)
            
            # Set the value
            self.settings.set(section, option, str_value)
            
            # Write changes to file
            with open('settings.ini', 'w') as configfile:
                self.settings.write(configfile)
            
            # Notify all listeners
            for listener in self._change_listeners:
                listener(section, option, str_value)
            
            logger.debug(f"Setting {key} updated to {value}")
        
        except Exception as e:
            log_exception(e)
            raise

    def get_editor_font(self):
        """Get the configured editor font"""
        font = tkfont.Font(
            family=self.get(editor_font_family, 'Consolas'),
            size=int(self.get(editor_font_size, 10))
        )
        return font

    def get_theme_colors(self):
        """Get the current theme colors"""
        theme = self.get('general/theme', 'Light')
        
        if theme == 'Dark':
            return {
                'background': '#2b2b2b',
                'foreground': '#a9b7c6',
                'selection': '#214283',
                'line_number': '#606366',
                'current_line': '#323232',
                'keyword': '#cc7832',
                'string': '#6a8759',
                'number': '#6897bb',
                'comment': '#808080'
            }
        # Light theme
        return {
            'background': '#ffffff',
            'foreground': '#000000',
            'selection': '#add6ff',
            'line_number': '#999999',
            'current_line': '#fffae3',
            'keyword': '#0000ff',
            'string': '#008000',
            'number': '#0000ff',
            'comment': '#808080'
        }

    def get_logging_config(self):
        """Get logging configuration"""
        return {
            'level': self.get('logging/level', 'INFO'),
            'file_enabled': self.get('logging/file_enabled', 'True') == 'True',
            'console_enabled': self.get('logging/console_enabled', 'True') == 'True'
        }

    def get_connection_settings(self):
        """Get connection-related settings"""
        return {
            'history_size': int(self.get('connection/history_size', 10)),
            'save_passwords': self.get('connection/save_passwords', 'False') == 'True'
        }

    def get_editor_settings(self):
        """Get all editor-related settings"""
        return {
            'font_family': self.get(editor_font_family, 'Consolas'),
            'font_size': int(self.get(editor_font_size, 10)),
            'auto_complete': self.get('editor/auto_complete', 'True') == 'True',
            'word_wrap': self.get('editor/word_wrap', 'True') == 'True',
            'tab_size': int(self.get('editor/tab_size', 4)),
            'use_spaces': self.get('editor/use_spaces', 'True') == 'True',
            'highlight_current_line': self.get('editor/highlight_current_line', 'True') == 'True',
            'show_line_numbers': self.get('editor/show_line_numbers', 'True') == 'True'
        }

    def get_data_settings(self):
        """Get all data-related settings"""
        return {
            'max_rows': int(self.get('data/max_rows', 1000)),
            'null_display': self.get('data/null_display', 'NULL'),
            'auto_commit': self.get('data/auto_commit', 'False') == 'True',
            'batch_size': int(self.get('data/batch_size', 1000))
        }

    def clear_section(self, section):
        """Clear all settings in a section"""
        try:
            # Remove the entire section
            if self.settings.has_section(section):
                self.settings.remove_section(section)
                
                # Write changes to file
                with open('settings.ini', 'w') as configfile:
                    self.settings.write(configfile)
                
                # Reload defaults
                self._load_defaults()
                
                # Notify listeners
                for listener in self._change_listeners:
                    listener(section, None, None)
            
            logger.debug(f"Section {section} cleared")
        
        except Exception as e:
            log_exception(e)
            raise

    def add_listener(self, listener):
        """
        Add a listener for settings changes
        
        :param listener: A callable that will be invoked when settings change
        """
        self._change_listeners.append(listener)

    def remove_listener(self, listener):
        """
        Remove a listener for settings changes
        
        :param listener: The listener to remove
        """
        if listener in self._change_listeners:
            self._change_listeners.remove(listener)

    def _notify_listeners(self, key, value):
        """
        Notify all registered listeners of a settings change
        
        :param key: The settings key that changed
        :param value: The new value
        """
        for listener in self._change_listeners:
            try:
                listener(key, value)
            except Exception as e:
                logging.error(f"Error in settings change listener: {e}")

    def reset_to_defaults(self):
        """
        Reset all settings to default values
        """
        self._load_defaults()
        self._save_settings()
        
        # Notify all listeners about complete settings reset
        for key, value in self._walk_settings(self.settings):
            self._notify_listeners(key, value)

    @staticmethod
    def _walk_settings(settings):
        """
        Recursively walk through settings to generate key-value pairs
        
        :param settings: Settings dictionary
        :yield: Tuple of (full_key, value)
        """
        for section in settings.sections():
            for key, value in settings.items(section):
                yield f"{section}/{key}", value

    def _save_settings(self):
        """
        Save current settings to file
        """
        try:
            with open('settings.ini', 'w') as configfile:
                self.settings.write(configfile)
        except Exception as e:
            logging.error(f"Failed to save settings: {e}")
