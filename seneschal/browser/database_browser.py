import logging
import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.ttk as ttk


class DatabaseBrowser(ttk.Treeview):
    def __init__(self, parent=None, connection=None):
        super().__init__(parent, columns=("Database Objects",), show="tree")
        self.connection = connection
        self.heading("#0", text="Database Objects")
        
        # Custom event handling
        self.bind('<<TreeviewSelect>>', self.on_item_selected)
        
        # Context menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.bind('<Button-3>', self.show_context_menu)
        
        self.setup_ui()
    
    def setup_ui(self):
        # Configure columns
        self.column("#0", width=300, stretch=tk.YES)
        
        # Populate initial tree structure if connection exists
        if self.connection and getattr(self.connection, 'connected', False):
            self.refresh_databases()
    
    def refresh_databases(self):
        """Refresh the list of databases and their objects"""
        # Clear existing items
        for item in self.get_children():
            self.delete(item)
        
        try:
            # Get list of databases
            databases = self.connection.get_databases()
            
            for db_name in databases:
                # Add database as a top-level item
                db_id = self.insert('', 'end', text=db_name, open=False, tags=('database',))
                
                # Add standard folders for each database
                folders = [
                    ("Tables", "tables_folder"),
                    ("Views", "views_folder"),
                    ("Stored Procedures", "procedures_folder"),
                    ("Functions", "functions_folder"),
                    ("Triggers", "triggers_folder")
                ]
                
                for folder_name, folder_tag in folders:
                    folder_id = self.insert(db_id, 'end', text=folder_name, tags=(folder_tag,))
        
        except Exception as e:
            logging.error(f"Failed to load databases: {str(e)}")
            messagebox.showerror("Error", f"Failed to load databases: {str(e)}")
    
    def refresh_database_objects(self, db_name):
        """Refresh objects within a specific database"""
        if not self.connection or not self.connection.connected:
            return
        
        try:
            # Switch to the selected database
            self.connection.execute_query(f"USE {db_name}")
            
            # Find the database node
            db_node = None
            for item in self.get_children():
                if self.item(item, 'text') == db_name:
                    db_node = item
                    break
            
            if not db_node:
                return
            
            # Refresh tables
            tables_folder = self.get_children(db_node)[0]  # Assumes Tables is the first folder
            self.delete(*self.get_children(tables_folder))
            tables = self.connection.execute_query("SHOW TABLES")
            for table in tables:
                self.insert(tables_folder, 'end', text=table[0], tags=('table',))
            
            # Refresh views
            views_folder = self.get_children(db_node)[1]  # Assumes Views is the second folder
            self.delete(*self.get_children(views_folder))
            views = self.connection.execute_query("SHOW FULL TABLES WHERE Table_type = 'VIEW'")
            for view in views:
                self.insert(views_folder, 'end', text=view[0], tags=('view',))
            
            # Refresh procedures
            procedures_folder = self.get_children(db_node)[2]  # Assumes Procedures is the third folder
            self.delete(*self.get_children(procedures_folder))
            procedures = self.connection.execute_query(
                "SELECT ROUTINE_NAME FROM INFORMATION_SCHEMA.ROUTINES "
                "WHERE ROUTINE_TYPE='PROCEDURE' AND ROUTINE_SCHEMA=?", 
                (db_name,)
            )
            for proc in procedures:
                self.insert(procedures_folder, 'end', text=proc[0], tags=('procedure',))
        
        except Exception as e:
            logging.error(f"Failed to load database objects: {str(e)}")
            messagebox.showerror("Error", f"Failed to load database objects: {str(e)}")
    
    def on_item_selected(self, event=None):
        """Handle item selection"""
        selected_items = self.selection()
        if not selected_items:
            return
        
        selected_item = selected_items[0]
        item_text = self.item(selected_item, 'text')
        item_tags = self.item(selected_item, 'tags')
        
        # Trigger appropriate action based on item type
        if item_tags and len(item_tags) > 0:
            item_type = item_tags[0]
            if item_type in ['table', 'view', 'procedure', 'function']:
                # You might want to emit a custom event or call a callback
                self.event_generate('<<DatabaseObjectSelected>>', 
                                    when='tail', 
                                    data=(item_type, item_text))
    
    def show_context_menu(self, event):
        """Show context menu for selected item"""
        # Clear previous menu
        self.context_menu.delete(0, 'end')
        
        # Get item under cursor
        iid = self.identify_row(event.y)
        if not iid:
            return
        
        # Select the item
        self.selection_set(iid)
        
        # Determine item type
        item_text = self.item(iid, 'text')
        item_tags = self.item(iid, 'tags')
        
        if not item_tags:
            return
        
        item_type = item_tags[0]
        
        # Populate context menu based on item type
        if item_type == 'database':
            self.context_menu.add_command(
                label="Refresh", 
                command=lambda: self.refresh_database_objects(item_text)
            )
            self.context_menu.add_separator()
            self.context_menu.add_command(label="Create Database...")
            self.context_menu.add_command(label="Drop Database...")
        
        elif item_type == 'table':
            self.context_menu.add_command(
                label="Open Table", 
                command=lambda: self.event_generate('<<DatabaseObjectSelected>>', 
                                                   when='tail', 
                                                   data=('table', item_text))
            )
            self.context_menu.add_command(label="Design Table...")
            self.context_menu.add_separator()
            self.context_menu.add_command(label="Create Table...")
            self.context_menu.add_command(label="Drop Table...")
            self.context_menu.add_separator()
            self.context_menu.add_command(label="Truncate Table...")
            self.context_menu.add_command(label="Rename Table...")
        
        elif item_type == 'view':
            self.context_menu.add_command(
                label="Open View", 
                command=lambda: self.event_generate('<<DatabaseObjectSelected>>', 
                                                   when='tail', 
                                                   data=('view', item_text))
            )
            self.context_menu.add_command(label="Design View...")
            self.context_menu.add_separator()
            self.context_menu.add_command(label="Create View...")
            self.context_menu.add_command(label="Drop View...")
        
        elif item_type == 'procedure':
            self.context_menu.add_command(
                label="Edit Procedure", 
                command=lambda: self.event_generate('<<DatabaseObjectSelected>>', 
                                                   when='tail', 
                                                   data=('procedure', item_text))
            )
            self.context_menu.add_separator()
            self.context_menu.add_command(label="Create Procedure...")
            self.context_menu.add_command(label="Drop Procedure...")
        
        # Display the context menu
        self.context_menu.post(event.x_root, event.y_root)

def create_database_browser(parent, connection):
    """
    Convenience function to create and return a database browser
    
    :param parent: Parent widget
    :param connection: Database connection object
    :return: DatabaseBrowser instance
    """
    return DatabaseBrowser(parent, connection)
