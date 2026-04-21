"""
Main application window and logic
"""

import tkinter as tk
from tkinter import ttk, messagebox
import asyncio
from typing import Optional
from concurrent.futures import ThreadPoolExecutor
import threading

from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError

from .framework import MainWindow, TabManager, StatusBar, MenuBar, TextEditor, DataGrid, TreeView, UITheme
from .dialogs import LoginDialog, ConnectionDialog
from ..db.connection import ConnectionManager, ConnectionInfo


class SchemaBrowser:
    """Schema browser widget for databases and tables"""
    
    def __init__(self, parent, conn_mgr: ConnectionManager):
        self.parent = parent
        self.conn_mgr = conn_mgr
        self.tree = TreeView(parent, columns=("type", "rows"))
        self.tree.build()
        
        # Bind double-click
        self.tree.widget.bind('<Double-Button-1>', self._on_double_click)
    
    def _on_double_click(self, event):
        """Handle double-click on tree item"""
        selected = self.tree.get_selected()
        if selected:
            self.tree.trigger('double_click', selected)
    
    def pack(self, **kwargs):
        """Pack the tree"""
        self.tree.widget.pack(**kwargs)


class QueryTab:
    """Query editor tab"""
    
    def __init__(self, parent, profile_name: str, conn_mgr: ConnectionManager):
        self.parent = parent
        self.profile_name = profile_name
        self.conn_mgr = conn_mgr
        self.frame = ttk.Frame(parent)
        
        # Create paned window
        self.paned = ttk.PanedWindow(self.frame, orient=tk.VERTICAL)
        self.paned.pack(fill=tk.BOTH, expand=True)
        
        # Query editor
        editor_frame = ttk.Frame(self.paned)
        self.paned.add(editor_frame)
        
        ttk.Label(editor_frame, text="SQL Query:").pack(anchor=tk.W, padx=5, pady=5)
        self.editor = TextEditor(editor_frame, syntax_highlight=True)
        self.editor_widget = self.editor.build()
        self.editor_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add buttons
        btn_frame = ttk.Frame(editor_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(btn_frame, text="Execute", command=self._execute_query).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Format", command=self._format_query).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Clear", command=self._clear_query).pack(side=tk.LEFT, padx=2)
        
        # Results grid
        results_frame = ttk.Frame(self.paned)
        self.paned.add(results_frame)
        
        ttk.Label(results_frame, text="Results:").pack(anchor=tk.W, padx=5, pady=5)
        self.grid = DataGrid(results_frame, columns=[])
        self.grid_widget = self.grid.build()
        self.grid_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Info label
        self.info_label = ttk.Label(results_frame, text="Ready")
        self.info_label.pack(anchor=tk.W, padx=5, pady=2)
    
    def _execute_query(self):
        """Execute SQL query"""
        query = self.editor.get_text()
        if not query.strip():
            messagebox.showwarning("Empty Query", "Please enter a query")
            return
        
        self._run_async(self._execute_async(query))
    
    async def _execute_async(self, query: str):
        """Execute query asynchronously"""
        try:
            engine = self.conn_mgr.get_engine(self.profile_name)
            
            with engine.connect() as conn:
                # Show executing status
                self.info_label.config(text="Executing...")
                self.parent.update()
                
                # Execute query
                result = conn.execute(text(query))
                
                # Get results
                columns = list(result.keys())
                rows = result.fetchall()
                
                # Update grid
                self.grid.columns = columns
                self.grid.set_data([list(row) for row in rows])
                
                # Update info
                num_rows = len(rows)
                self.info_label.config(text=f"Query executed. {num_rows} rows returned.")
        
        except SQLAlchemyError as e:
            messagebox.showerror("Query Error", f"Error executing query:\n{str(e)}")
            self.info_label.config(text="Query failed")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error:\n{str(e)}")
            self.info_label.config(text="Error")
    
    def _run_async(self, coro):
        """Run coroutine in thread pool"""
        loop = asyncio.new_event_loop()
        threading.Thread(target=lambda: loop.run_until_complete(coro), daemon=True).start()
    
    def _format_query(self):
        """Format SQL query"""
        # TODO: Implement SQL formatting
        messagebox.showinfo("Format", "Query formatting not yet implemented")
    
    def _clear_query(self):
        """Clear query editor"""
        self.editor.clear()


class SeneschalApp(MainWindow):
    """Main Seneschal application window"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize connection manager
        self.conn_mgr = ConnectionManager()
        
        # Current profile
        self.current_profile: Optional[str] = None
        
        # Thread pool for background tasks
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Build main UI
        self.build_ui()
    
    def build_ui(self) -> None:
        """Build main application UI"""
        # Create menu bar
        self.menu_bar = MenuBar(self)
        
        # File menu
        file_menu = self.menu_bar.add_menu("File")
        self.menu_bar.add_command(file_menu, "New Connection", self._new_connection)
        self.menu_bar.add_command(file_menu, "Open Connection", self._open_connection)
        self.menu_bar.add_command(file_menu, "Manage Connections", self._manage_connections)
        self.menu_bar.add_separator(file_menu)
        self.menu_bar.add_command(file_menu, "Exit", self._exit)
        
        # Edit menu
        edit_menu = self.menu_bar.add_menu("Edit")
        self.menu_bar.add_command(edit_menu, "Preferences", self._show_preferences)
        
        # Tools menu
        tools_menu = self.menu_bar.add_menu("Tools")
        self.menu_bar.add_command(tools_menu, "Query History", self._show_query_history)
        self.menu_bar.add_command(tools_menu, "Export Data", self._export_data)
        
        # Help menu
        help_menu = self.menu_bar.add_menu("Help")
        self.menu_bar.add_command(help_menu, "About", self._show_about)
        
        # Main container
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Horizontal split: sidebar + content
        h_paned = ttk.PanedWindow(main_container, orient=tk.HORIZONTAL)
        h_paned.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar: Schema browser
        sidebar_frame = ttk.Frame(h_paned, width=250)
        h_paned.add(sidebar_frame)
        
        ttk.Label(sidebar_frame, text="Database Browser", font=("Segoe UI", 10, "bold")).pack(padx=5, pady=5)
        self.schema_browser = SchemaBrowser(sidebar_frame, self.conn_mgr)
        self.schema_browser.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Content area: Query tabs
        content_frame = ttk.Frame(h_paned)
        h_paned.add(content_frame)
        
        self.tab_manager = TabManager(content_frame)
        self.tab_manager.pack(fill=tk.BOTH, expand=True)
        
        # Add initial query tab
        self._add_query_tab()
        
        # Status bar
        self.status_bar = StatusBar(self)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Show login dialog
        self._open_connection()
    
    def _add_query_tab(self):
        """Add a new query tab"""
        if not self.current_profile:
            messagebox.showwarning("No Connection", "Please connect to a database first")
            return
        
        tab_id = f"query_tab_{len(self.tab_manager.tabs)}"
        frame = self.tab_manager.add_tab(tab_id, f"Query {len(self.tab_manager.tabs) + 1}")
        
        query_tab = QueryTab(frame, self.current_profile, self.conn_mgr)
        # Store reference
        setattr(frame, '_query_tab', query_tab)
    
    def _new_connection(self):
        """Create new connection"""
        dialog = ConnectionDialog(self, self.conn_mgr)
        result = dialog.show()
        if result:
            self.current_profile = result
            self._populate_schema_browser()
    
    def _open_connection(self):
        """Open existing connection"""
        dialog = LoginDialog(self, self.conn_mgr)
        result = dialog.show()
        if result:
            self.current_profile = result
            try:
                # Test connection
                engine = self.conn_mgr.get_engine(result)
                self.status_bar.set_status(f"Connected to {result}")
                self._populate_schema_browser()
            except Exception as e:
                messagebox.showerror("Connection Error", f"Failed to connect:\n{str(e)}")
    
    def _manage_connections(self):
        """Manage saved connections"""
        # TODO: Implement connection manager dialog
        messagebox.showinfo("Manage Connections", "Connection manager not yet implemented")
    
    def _populate_schema_browser(self):
        """Populate schema browser with databases and tables"""
        if not self.current_profile:
            return
        
        try:
            engine = self.conn_mgr.get_engine(self.current_profile)
            inspector = inspect(engine)
            
            # Clear tree
            self.schema_browser.tree.clear()
            
            # Get schemas/databases
            schemas = inspector.get_schema_names()
            for schema in schemas:
                schema_id = f"schema_{schema}"
                self.schema_browser.tree.add_item("", schema_id, schema)
                
                # Get tables
                tables = inspector.get_table_names(schema)
                for table in tables:
                    table_id = f"table_{schema}_{table}"
                    self.schema_browser.tree.add_item(schema_id, table_id, table, ("TABLE",))
                
                # Get views
                views = inspector.get_view_names(schema)
                for view in views:
                    view_id = f"view_{schema}_{view}"
                    self.schema_browser.tree.add_item(schema_id, view_id, view, ("VIEW",))
        
        except Exception as e:
            messagebox.showerror("Schema Browser Error", f"Failed to load schema:\n{str(e)}")
    
    def _show_preferences(self):
        """Show preferences dialog"""
        messagebox.showinfo("Preferences", "Preferences dialog not yet implemented")
    
    def _show_query_history(self):
        """Show query history"""
        messagebox.showinfo("Query History", "Query history not yet implemented")
    
    def _export_data(self):
        """Export data"""
        messagebox.showinfo("Export Data", "Export functionality not yet implemented")
    
    def _show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About", "Seneschal Python Edition\nVersion 0.1.0\n\nA Python port of Seneschal database management tool")
    
    def _exit(self):
        """Exit application"""
        self.conn_mgr.close_all()
        self.executor.shutdown(wait=False)
        self.quit()

