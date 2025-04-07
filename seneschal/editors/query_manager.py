import tkinter as tk
import tkinter.messagebox as messagebox
import configparser
import tkinter.simpledialog as simpledialog

import os
import json
from datetime import datetime

class QueryManager:
    def __init__(self):
        self.settings = configparser.ConfigParser()
        self.query_file = os.path.join(
            os.path.expanduser('~'),
            '.seneschal',
            'saved_queries.json'
        )
        self.ensure_directory_exists()
        
    def ensure_directory_exists(self):
        """Ensure the .seneschal directory exists"""
        directory = os.path.dirname(self.query_file)
        if not os.path.exists(directory):
            os.makedirs(directory)
            
    def load_queries(self):
        """Load saved queries from file"""
        try:
            if os.path.exists(self.query_file):
                with open(self.query_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception:
            return {}
            
    def save_queries(self, queries):
        """Save queries to file"""
        try:
            with open(self.query_file, 'w') as f:
                json.dump(queries, f, indent=2)
            return True
        except Exception:
            return False
            
    def save_query(self, name, sql):
        """Save a new query"""
        queries = self.load_queries()
        queries[name] = {
            'sql': sql,
            'created': datetime.now().isoformat(),
            'last_used': datetime.now().isoformat()
        }
        return self.save_queries(queries)
        
    def load_query(self, name):
        """Load a specific query"""
        queries = self.load_queries()
        if name in queries:
            query = queries[name]
            # Update last used time
            query['last_used'] = datetime.now().isoformat()
            self.save_queries(queries)
            return query['sql']
        return None
        
    def delete_query(self, name):
        """Delete a saved query"""
        queries = self.load_queries()
        if name in queries:
            del queries[name]
            return self.save_queries(queries)
        return False
        
    def get_query_list(self):
        """Get list of saved queries"""
        return list(self.load_queries().keys())

class QueryManagerDialog(tk.Toplevel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.query_manager = QueryManager()
        self.setup_ui()
        self.load_queries()
        
    def setup_ui(self):
        self.title("Query Manager")
        self.geometry("400x300")
        
        layout = tk.Frame(self)
        layout.pack(fill=tk.BOTH, expand=True)
        
        # Query list
        self.query_list = tk.Listbox(layout)
        self.query_list.pack(fill=tk.BOTH, expand=True)
        self.query_list.bind('<Double-1>', self.load_selected_query)
        
        # Buttons
        button_layout = tk.Frame(layout)
        button_layout.pack(fill=tk.X)
        
        self.new_button = tk.Button(button_layout, text="New", command=self.new_query)
        self.new_button.pack(side=tk.LEFT, expand=True)
        
        self.load_button = tk.Button(button_layout, text="Load", command=self.load_selected_query_button)
        self.load_button.pack(side=tk.LEFT, expand=True)
        
        self.delete_button = tk.Button(button_layout, text="Delete", command=self.delete_selected_query)
        self.delete_button.pack(side=tk.LEFT, expand=True)
        
        self.close_button = tk.Button(button_layout, text="Close", command=self.destroy)
        self.close_button.pack(side=tk.LEFT, expand=True)
        
    def load_queries(self):
        """Load saved queries into the list"""
        self.query_list.delete(0, tk.END)
        for query in self.query_manager.get_query_list():
            self.query_list.insert(tk.END, query)
        
    def new_query(self):
        """Create a new saved query"""
        name = simpledialog.askstring("New Query", "Enter name for the query:")
        if name:
            sql = simpledialog.askstring("New Query", "Enter SQL query:", initialvalue="SELECT * FROM ")
            if sql:
                if self.query_manager.save_query(name, sql):
                    self.load_queries()
                else:
                    messagebox.showerror("Error", "Failed to save query")
                    
    def load_selected_query_button(self):
        """Load the selected query from button click"""
        selection = self.query_list.curselection()
        if selection:
            self.load_selected_query(None)
                    
    def load_selected_query(self, event=None):
        """Load the selected query"""
        selection = self.query_list.curselection()
        if selection:
            current = self.query_list.get(selection[0])
            sql = self.query_manager.load_query(current)
            if sql:
                # Emit signal or call callback to load query in editor
                if hasattr(self.master, 'load_query'):
                    self.master.load_query(sql)
                self.destroy()
            else:
                messagebox.showerror("Error", "Failed to load query")
                
    def delete_selected_query(self):
        """Delete the selected query"""
        selection = self.query_list.curselection()
        if selection:
            current = self.query_list.get(selection[0])
            if messagebox.askyesno("Confirm Delete", f"Delete query '{current}'?"):
                if self.query_manager.delete_query(current):
                    self.load_queries()
                else:
                    messagebox.showerror("Error", "Failed to delete query")
