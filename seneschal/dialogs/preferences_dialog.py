from PyQt6.QtWidgets import (QDialog, QTabWidget, QWidget, QVBoxLayout,
                           QFormLayout, QSpinBox, QCheckBox, QComboBox,
                           QFontComboBox, QColorDialog, QPushButton,
                           QLabel, QGroupBox, QHBoxLayout, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from ..utils.settings_manager import SettingsManager

class PreferencesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = SettingsManager()
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        self.setWindowTitle("Preferences")
        self.resize(600, 400)

        layout = QVBoxLayout(self)
        
        # Tab widget for different settings categories
        self.tab_widget = QTabWidget()
        
        # General settings tab
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        
        # Interface group
        interface_group = QGroupBox("Interface")
        interface_layout = QFormLayout()
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "German", "French", "Spanish"])
        interface_layout.addRow("Language:", self.language_combo)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "System"])
        interface_layout.addRow("Theme:", self.theme_combo)
        
        interface_group.setLayout(interface_layout)
        general_layout.addWidget(interface_group)
        
        # Logging group
        logging_group = QGroupBox("Logging")
        logging_layout = QFormLayout()
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        logging_layout.addRow("Log Level:", self.log_level_combo)
        
        self.file_logging = QCheckBox()
        logging_layout.addRow("Enable File Logging:", self.file_logging)
        
        self.console_logging = QCheckBox()
        logging_layout.addRow("Enable Console Logging:", self.console_logging)
        
        logging_group.setLayout(logging_layout)
        general_layout.addWidget(logging_group)
        
        # Editor settings tab
        editor_tab = QWidget()
        editor_layout = QVBoxLayout(editor_tab)
        
        # Font settings group
        font_group = QGroupBox("Font Settings")
        font_layout = QFormLayout()
        
        self.editor_font = QFontComboBox()
        font_layout.addRow("Font:", self.editor_font)
        
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 72)
        font_layout.addRow("Size:", self.font_size)
        
        font_group.setLayout(font_layout)
        editor_layout.addWidget(font_group)
        
        # Editor behavior group
        behavior_group = QGroupBox("Editor Behavior")
        behavior_layout = QFormLayout()
        
        self.auto_complete = QCheckBox()
        behavior_layout.addRow("Enable Auto-Complete:", self.auto_complete)
        
        self.word_wrap = QCheckBox()
        behavior_layout.addRow("Word Wrap:", self.word_wrap)
        
        self.tab_size = QSpinBox()
        self.tab_size.setRange(2, 8)
        behavior_layout.addRow("Tab Size:", self.tab_size)
        
        self.use_spaces = QCheckBox()
        behavior_layout.addRow("Use Spaces for Tabs:", self.use_spaces)
        
        self.highlight_line = QCheckBox()
        behavior_layout.addRow("Highlight Current Line:", self.highlight_line)
        
        self.show_line_numbers = QCheckBox()
        behavior_layout.addRow("Show Line Numbers:", self.show_line_numbers)
        
        behavior_group.setLayout(behavior_layout)
        editor_layout.addWidget(behavior_group)
        
        # Data settings tab
        data_tab = QWidget()
        data_layout = QVBoxLayout(data_tab)
        
        # Results group
        results_group = QGroupBox("Query Results")
        results_layout = QFormLayout()
        
        self.max_rows = QSpinBox()
        self.max_rows.setRange(100, 1000000)
        results_layout.addRow("Max Rows:", self.max_rows)
        
        self.null_display = QComboBox()
        self.null_display.addItems(["NULL", "(null)", "empty"])
        results_layout.addRow("NULL Display:", self.null_display)
        
        self.auto_commit = QCheckBox()
        results_layout.addRow("Auto Commit:", self.auto_commit)
        
        self.batch_size = QSpinBox()
        self.batch_size.setRange(100, 10000)
        results_layout.addRow("Batch Size:", self.batch_size)
        
        results_group.setLayout(results_layout)
        data_layout.addWidget(results_group)
        
        # Connection settings group
        connection_group = QGroupBox("Connection")
        connection_layout = QFormLayout()
        
        self.history_size = QSpinBox()
        self.history_size.setRange(5, 50)
        connection_layout.addRow("Connection History Size:", self.history_size)
        
        self.save_passwords = QCheckBox()
        connection_layout.addRow("Save Passwords:", self.save_passwords)
        
        connection_group.setLayout(connection_layout)
        data_layout.addWidget(connection_group)
        
        # Add tabs
        self.tab_widget.addTab(general_tab, "General")
        self.tab_widget.addTab(editor_tab, "Editor")
        self.tab_widget.addTab(data_tab, "Data")
        
        layout.addWidget(self.tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_button)
        
        self.reset_button = QPushButton("Reset to Defaults")
        self.reset_button.clicked.connect(self.reset_settings)
        button_layout.addWidget(self.reset_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)

    def load_settings(self):
        # Load general settings
        self.language_combo.setCurrentText(
            self.settings.get('general/language', 'English'))
        self.theme_combo.setCurrentText(
            self.settings.get('general/theme', 'Light'))
            
        # Load logging settings
        logging_config = self.settings.get_logging_config()
        self.log_level_combo.setCurrentText(logging_config['level'])
        self.file_logging.setChecked(logging_config['file_enabled'])
        self.console_logging.setChecked(logging_config['console_enabled'])
        
        # Load editor settings
        editor_settings = self.settings.get_editor_settings()
        self.editor_font.setCurrentFont(QFont(editor_settings['font_family']))
        self.font_size.setValue(editor_settings['font_size'])
        self.auto_complete.setChecked(editor_settings['auto_complete'])
        self.word_wrap.setChecked(editor_settings['word_wrap'])
        self.tab_size.setValue(editor_settings['tab_size'])
        self.use_spaces.setChecked(editor_settings['use_spaces'])
        self.highlight_line.setChecked(editor_settings['highlight_current_line'])
        self.show_line_numbers.setChecked(editor_settings['show_line_numbers'])
        
        # Load data settings
        data_settings = self.settings.get_data_settings()
        self.max_rows.setValue(data_settings['max_rows'])
        self.null_display.setCurrentText(data_settings['null_display'])
        self.auto_commit.setChecked(data_settings['auto_commit'])
        self.batch_size.setValue(data_settings['batch_size'])
        
        # Load connection settings
        connection_settings = self.settings.get_connection_settings()
        self.history_size.setValue(connection_settings['history_size'])
        self.save_passwords.setChecked(connection_settings['save_passwords'])

    def save_settings(self):
        try:
            # Save general settings
            self.settings.set('general/language', self.language_combo.currentText())
            self.settings.set('general/theme', self.theme_combo.currentText())
            
            # Save logging settings
            self.settings.set('logging/level', self.log_level_combo.currentText())
            self.settings.set('logging/file_enabled', self.file_logging.isChecked())
            self.settings.set('logging/console_enabled', self.console_logging.isChecked())
            
            # Save editor settings
            self.settings.set('editor/font_family', self.editor_font.currentFont().family())
            self.settings.set('editor/font_size', self.font_size.value())
            self.settings.set('editor/auto_complete', self.auto_complete.isChecked())
            self.settings.set('editor/word_wrap', self.word_wrap.isChecked())
            self.settings.set('editor/tab_size', self.tab_size.value())
            self.settings.set('editor/use_spaces', self.use_spaces.isChecked())
            self.settings.set('editor/highlight_current_line', self.highlight_line.isChecked())
            self.settings.set('editor/show_line_numbers', self.show_line_numbers.isChecked())
            
            # Save data settings
            self.settings.set('data/max_rows', self.max_rows.value())
            self.settings.set('data/null_display', self.null_display.currentText())
            self.settings.set('data/auto_commit', self.auto_commit.isChecked())
            self.settings.set('data/batch_size', self.batch_size.value())
            
            # Save connection settings
            self.settings.set('connection/history_size', self.history_size.value())
            self.settings.set('connection/save_passwords', self.save_passwords.isChecked())
            
            QMessageBox.information(self, "Success", "Settings saved successfully!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")

    def reset_settings(self):
        """Reset all settings to defaults"""
        if QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            # Clear all sections
            for section in ['general', 'editor', 'data', 'connection', 'logging']:
                self.settings.clear_section(section)
            
            # Reload settings
            self.load_settings()
            QMessageBox.information(self, "Success", "Settings reset to defaults!")
