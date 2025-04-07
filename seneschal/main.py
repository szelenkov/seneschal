import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import ttkbootstrap

from seneschal.browser.database_browser import create_database_browser
from seneschal.editors.query_editor import QueryEditor
from seneschal.editors.table_editor import TableEditor
from seneschal.dialogs.connection_dialog import ConnectionDialog
from seneschal.dialogs.preferences_dialog import PreferencesDialog
from seneschal.tools.data_transfer import DataTransferTool
from seneschal.utils.settings_manager import SettingsManager
from seneschal.utils.theme_manager import ThemeManager

class Seneschal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.settings = SettingsManager()
        self.title("Seneschal")
        self.geometry("1200x800")
        self.current_connection = None
        
        # Create the main menu bar
        self.create_menu_bar()
        
        # Create the main layout
        self.main_splitter = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.main_splitter.pack(fill=tk.BOTH, expand=True)
        
        # Database browser (left side)
        self.setup_database_browser()
        
        # Right side content
        self.right_content = ttk.Notebook(self)
        self.right_content.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_bar = tk.Label(self, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Connect settings changes
        self.settings.add_listener(self.on_settings_changed)
        
    def create_menu_bar(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Connect", command=self.show_connection_dialog)
        file_menu.add_command(label="Disconnect", command=self.disconnect_database)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Copy")
        edit_menu.add_command(label="Paste")
        
        # Query menu
        query_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Query", menu=query_menu)
        query_menu.add_command(label="New Query", command=self.new_query_tab)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Export/Import Data", command=self.show_data_transfer)
        tools_menu.add_command(label="Preferences", command=self.show_preferences)
        tools_menu.add_command(label="Refresh Database Browser", command=self.refresh_database_browser)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
    def setup_database_browser(self):
        # Create a frame to contain the database browser
        self.db_browser_frame = ttk.Frame(self.main_splitter)
        
        # Create database browser within the frame
        self.db_browser = create_database_browser(
            self.db_browser_frame, 
            connection=self.current_connection
        )
        self.db_browser.pack(fill=tk.BOTH, expand=True)
        
        # Bind event handler
        self.db_browser.bind('<<DatabaseObjectSelected>>', self.handle_database_object_selection)
        
        # Add the frame to the main splitter
        self.main_splitter.add(self.db_browser_frame)
        
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
            
            self.status_bar.config(text=f"Connected to {params['type']}")
            
        except Exception as e:
            messagebox.showerror(f"Connection Error: {e}")
            
    def disconnect_database(self):
        if self.current_connection and self.current_connection.connected:
            self.current_connection.disconnect()
            self.current_connection = None
            self.db_browser.connection = None
            self.db_browser.model.clear()
            self.status_bar.config(text="Disconnected")
            
            # Close all open tabs
            while self.right_content.index("end") > 0:
                self.right_content.forget(self.right_content.index("end") - 1)
            
    def new_query_tab(self):
        editor = QueryEditor(connection=self.current_connection)
        self.right_content.add(editor, text="New Query")
        self.right_content.select(editor)
        
    def handle_database_object_selection(self, event):
        # event.data will be a tuple of (item_type, item_name)
        item_type, item_name = event.data
        
        if item_type == 'table':
            editor = TableEditor(
                connection=self.current_connection, 
                table_name=item_name
            )
            editor.data_changed.connect(self.refresh_database_browser)
            self.right_content.add(editor, text=f"Table: {item_name}")
            self.right_content.select(editor)
            
    def close_tab(self, index):
        widget = self.right_content.select()
        self.right_content.forget(index)
        
    def show_data_transfer(self):
        tool = DataTransferTool(connection=self.current_connection)
        self.right_content.add(tool, text="Data Transfer")
        self.right_content.select(tool)
        
    def show_preferences(self):
        dialog = PreferencesDialog(self)
        if dialog.exec():
            # Apply theme if it was changed
            app = ttkbootstrap.Window().instance()
            ThemeManager.apply_theme(app)
            
            # Update editor fonts and styles
            for i in range(self.right_content.index("end")):
                widget = self.right_content.select()
                if hasattr(widget, 'update_editor_settings'):
                    widget.update_editor_settings()
            
            self.status_bar.config(text="Settings updated")

    def on_settings_changed(self, key, value):
        """
        Handle settings changes
        
        :param key: The settings key that changed
        :param value: The new value
        """
        # Theme change
        if key == 'general/theme':
            self.update_theme()
        
        # Font changes
        elif key.startswith('editor/'):
            self.update_font_settings()
        
    def refresh_database_browser(self):
        if self.current_connection and self.current_connection.connected:
            self.db_browser.refresh_databases()
            self.status_bar.config(text="Database browser refreshed")
        
    @staticmethod
    def show_about():
        messagebox.showinfo(
            "About Seneschal", 
            "Seneschal Database Management Tool\n\n"
            "Version: 1.0.0\n"
            "Developed by: Your Company Name\n\n"
            "A comprehensive database management and query tool "
            "designed for efficiency and ease of use."
        )

def main():
    window = Seneschal()
    window.mainloop()
