import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, 
                           QTreeView, QSplitter, QMenuBar, QStatusBar,
                           QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
import qtawesome as qta

from seneschal.browser.database_browser import DatabaseBrowser
from seneschal.editors.query_editor import QueryEditor
from seneschal.editors.table_editor import TableEditor
from seneschal.dialogs.connection_dialog import ConnectionDialog
from seneschal.dialogs.preferences_dialog import PreferencesDialog
from seneschal.tools.data_transfer import DataTransferTool
from seneschal.utils.settings_manager import SettingsManager
from seneschal.utils.theme_manager import ThemeManager

class Seneschal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = SettingsManager()
        self.setWindowTitle("Seneschal Python")
        self.resize(1200, 800)
        self.current_connection = None
        
        # Create the main menu bar
        self.create_menu_bar()
        
        # Create the main layout
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(self.main_splitter)
        
        # Database browser (left side)
        self.db_browser = DatabaseBrowser(connection=self.current_connection)
        self.db_browser.item_selected.connect(self.on_db_item_selected)
        self.main_splitter.addWidget(self.db_browser)
        
        # Right side content
        self.right_content = QTabWidget()
        self.right_content.setTabsClosable(True)
        self.right_content.tabCloseRequested.connect(self.close_tab)
        self.main_splitter.addWidget(self.right_content)
        
        # Set the split ratio (30% left, 70% right)
        self.main_splitter.setSizes([300, 700])
        
        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
        
        # Set application icon
        self.setWindowIcon(qta.icon('fa5s.database'))
        
        # Connect settings changes
        self.settings.settings_changed.connect(self.on_settings_changed)
        
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        connect_action = file_menu.addAction("&Connect")
        connect_action.setIcon(qta.icon('fa5s.plug'))
        connect_action.triggered.connect(self.show_connection_dialog)
        
        disconnect_action = file_menu.addAction("&Disconnect")
        disconnect_action.setIcon(qta.icon('fa5s.power-off'))
        disconnect_action.triggered.connect(self.disconnect_database)
        
        file_menu.addSeparator()
        file_menu.addAction(qta.icon('fa5s.times'), "&Exit", self.close)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        edit_menu.addAction(qta.icon('fa5s.copy'), "&Copy")
        edit_menu.addAction(qta.icon('fa5s.paste'), "&Paste")
        
        # Query menu
        query_menu = menubar.addMenu("&Query")
        new_query_action = query_menu.addAction("&New Query")
        new_query_action.setIcon(qta.icon('fa5s.file-code'))
        new_query_action.triggered.connect(self.new_query_tab)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        export_action = tools_menu.addAction("&Export/Import Data")
        export_action.setIcon(qta.icon('fa5s.exchange-alt'))
        export_action.triggered.connect(self.show_data_transfer)
        
        preferences_action = tools_menu.addAction("&Preferences")
        preferences_action.setIcon(qta.icon('fa5s.cog'))
        preferences_action.triggered.connect(self.show_preferences)
        
        refresh_action = tools_menu.addAction("&Refresh Database Browser")
        refresh_action.setIcon(qta.icon('fa5s.sync'))
        refresh_action.triggered.connect(self.refresh_database_browser)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        help_menu.addAction(qta.icon('fa5s.info-circle'), "&About", self.show_about)
        
    def show_connection_dialog(self):
        dialog = ConnectionDialog(self)
        if dialog.exec():
            params = dialog.get_connection_params()
            self.connect_database(params)
            
    def connect_database(self, params):
        try:
            # Create appropriate connection based on database type
            if params['type'] == 'MySQL':
                from seneschal.db.connection import MySQLConnection
                self.current_connection = MySQLConnection()
            elif params['type'] == 'PostgreSQL':
                from seneschal.db.connection import PostgreSQLConnection
                self.current_connection = PostgreSQLConnection()
            elif params['type'] == 'SQLite':
                from seneschal.db.connection import SQLiteConnection
                self.current_connection = SQLiteConnection()
                
            # Connect using the parameters
            self.current_connection.connect(params)
            
            # Update the database browser
            self.db_browser.connection = self.current_connection
            self.db_browser.refresh_databases()
            
            self.statusBar.showMessage(f"Connected to {params['type']}")
            
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", str(e))
            
    def disconnect_database(self):
        if self.current_connection and self.current_connection.connected:
            self.current_connection.disconnect()
            self.current_connection = None
            self.db_browser.connection = None
            self.db_browser.model.clear()
            self.statusBar.showMessage("Disconnected")
            
            # Close all open tabs
            while self.right_content.count() > 0:
                self.right_content.removeTab(0)
            
    def new_query_tab(self):
        editor = QueryEditor(connection=self.current_connection)
        self.right_content.addTab(editor, "New Query")
        self.right_content.setCurrentWidget(editor)
        
    def on_db_item_selected(self, item_type, name):
        if item_type == "table":
            editor = TableEditor(
                connection=self.current_connection, 
                table_name=name
            )
            editor.data_changed.connect(self.refresh_database_browser)
            self.right_content.addTab(editor, f"Table: {name}")
            self.right_content.setCurrentWidget(editor)
            
    def close_tab(self, index):
        widget = self.right_content.widget(index)
        widget.deleteLater()
        self.right_content.removeTab(index)
        
    def show_data_transfer(self):
        tool = DataTransferTool(connection=self.current_connection)
        self.right_content.addTab(tool, "Data Transfer")
        self.right_content.setCurrentWidget(tool)
        
    def show_preferences(self):
        dialog = PreferencesDialog(self)
        if dialog.exec():
            # Apply theme if it was changed
            app = QApplication.instance()
            ThemeManager.apply_theme(app)
            
            # Update editor fonts and styles
            for i in range(self.right_content.count()):
                widget = self.right_content.widget(i)
                if hasattr(widget, 'update_editor_settings'):
                    widget.update_editor_settings()
            
            self.statusBar.showMessage("Settings updated")

    def on_settings_changed(self, section, value):
        """Handle settings changes"""
        if section == 'general':
            # Apply theme if it was changed
            app = QApplication.instance()
            ThemeManager.apply_theme(app)
        elif section == 'editor':
            # Update editor settings in all open editors
            for i in range(self.right_content.count()):
                widget = self.right_content.widget(i)
                if hasattr(widget, 'update_editor_settings'):
                    widget.update_editor_settings()
        
    def refresh_database_browser(self):
        if self.current_connection and self.current_connection.connected:
            self.db_browser.refresh_databases()
            self.statusBar.showMessage("Database browser refreshed")
        
    def show_about(self):
        QMessageBox.about(
            self,
            "About Seneschal Python",
            "Seneschal Python Edition\n\n"
            "A modern database management tool\n"
            "Python port of the original Seneschal"
        )

def main():
    app = QApplication(sys.argv)
    window = Seneschal()
    window.show()
    sys.exit(app.exec())
