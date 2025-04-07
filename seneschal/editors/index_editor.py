import tkinter as tk
from tkinter import messagebox, ttk

class IndexEditorDialog(tk.Toplevel):
    def __init__(self, parent=None, index_data=None, available_columns=None):
        super().__init__(parent)
        self.index_data = index_data or {}
        self.available_columns = available_columns or []
        self.setup_ui()
        
    def setup_ui(self):
        self.title("Index Editor")
        self.minsize(400, 300)
        
        # Main frame
        main_frame = tk.Frame(self)
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Name
        tk.Label(main_frame, text="Name:").pack(anchor='w')
        self.name_edit = tk.Entry(main_frame)
        self.name_edit.insert(0, self.index_data.get('name', ''))
        self.name_edit.pack(fill=tk.X, pady=(0, 10))
        
        # Type
        tk.Label(main_frame, text="Type:").pack(anchor='w')
        self.type_var = tk.StringVar(value=self.index_data.get('type', 'INDEX'))
        self.type_combo = ttk.Combobox(main_frame, textvariable=self.type_var, 
                                       values=['PRIMARY', 'UNIQUE', 'INDEX', 'FULLTEXT'], 
                                       state='readonly')
        self.type_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Columns
        tk.Label(main_frame, text="Columns:").pack(anchor='w')
        self.columns_list = tk.Listbox(main_frame, selectmode=tk.MULTIPLE)
        for column in self.available_columns:
            self.columns_list.insert(tk.END, column)
            if column in self.index_data.get('columns', []):
                index = self.available_columns.index(column)
                self.columns_list.selection_set(index)
        self.columns_list.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        save_button = tk.Button(button_frame, text="Save", command=self.on_save)
        save_button.pack(side=tk.LEFT, expand=True, padx=5)
        
        cancel_button = tk.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_button.pack(side=tk.LEFT, expand=True, padx=5)
        
    def on_save(self):
        self.result = {
            'name': self.name_edit.get(),
            'type': self.type_combo.get(),
            'columns': [self.available_columns[i] for i in self.columns_list.curselection()]
        }
        self.destroy()
        
    def get_index_data(self):
        return getattr(self, 'result', None)

class IndexEditor(tk.Frame):
    def __init__(self, parent=None, connection=None, table_name=None):
        super().__init__(parent)
        self.connection = connection
        self.table_name = table_name
        self.setup_ui()
        if table_name:
            self.load_indexes()
            
    def setup_ui(self):
        # Toolbar
        toolbar = tk.Frame(self)
        toolbar.pack(fill=tk.X)
        
        self.add_index_btn = tk.Button(toolbar, text="Add Index", command=self.add_index)
        self.add_index_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.edit_index_btn = tk.Button(toolbar, text="Edit Index", command=self.edit_index)
        self.edit_index_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.delete_index_btn = tk.Button(toolbar, text="Delete Index", command=self.delete_index)
        self.delete_index_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Index view
        self.index_view = ttk.Treeview(self, columns=("Name", "Type", "Columns", "Comment"), show='headings')
        self.index_view.heading("Name", text="Name")
        self.index_view.heading("Type", text="Type")
        self.index_view.heading("Columns", text="Columns")
        self.index_view.heading("Comment", text="Comment")
        self.index_view.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def get_available_columns(self):
        try:
            query = f"""
                SELECT COLUMN_NAME
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = '{self.table_name}'
                ORDER BY ORDINAL_POSITION
            """
            result = self.connection.execute_query(query)
            return [row[0] for row in result]
        except Exception:
            return []
            
    def load_indexes(self):
        if not self.connection or not self.table_name:
            return
            
        try:
            # Clear existing items
            for item in self.index_view.get_children():
                self.index_view.delete(item)
            
            # Get index information
            query = f"SHOW INDEX FROM {self.table_name}"
            result = self.connection.execute_query(query)
            
            # Process results
            indexes = {}
            for row in result:
                index_name = row[2]  # Key_name
                if index_name not in indexes:
                    indexes[index_name] = {
                        'name': index_name,
                        'type': 'PRIMARY' if index_name == 'PRIMARY' else 
                               'UNIQUE' if not row[1] else 'INDEX',  # Non_unique
                        'columns': [],
                        'comment': ''
                    }
                indexes[index_name]['columns'].append(row[4])  # Column_name
                
            # Update view
            for index in indexes.values():
                self.index_view.insert('', 'end', values=(
                    index['name'], 
                    index['type'], 
                    ', '.join(index['columns']), 
                    index['comment']
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load indexes: {str(e)}")
            
    def add_index(self):
        available_columns = self.get_available_columns()
        dialog = IndexEditorDialog(self, available_columns=available_columns)
        dialog.transient(self)
        dialog.grab_set()
        self.wait_window(dialog)
        
        index_data = dialog.get_index_data()
        if not index_data:
            return
        
        try:
            # Generate CREATE INDEX statement
            if index_data['type'] == 'PRIMARY':
                query = f"""
                    ALTER TABLE {self.table_name}
                    ADD PRIMARY KEY ({', '.join(index_data['columns'])})
                """
            else:
                index_type = 'UNIQUE ' if index_data['type'] == 'UNIQUE' else ''
                query = f"""
                    CREATE {index_type}INDEX {index_data['name']}
                    ON {self.table_name} ({', '.join(index_data['columns'])})
                """
            
            self.connection.execute_query(query)
            self.load_indexes()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create index: {str(e)}")
                
    def edit_index(self):
        selected_item = self.index_view.selection()
        if not selected_item:
            messagebox.showinfo("Info", "Please select an index to edit")
            return
            
        current_values = self.index_view.item(selected_item[0])['values']
        index_data = {
            'name': current_values[0],
            'type': current_values[1],
            'columns': [col.strip() for col in current_values[2].split(',')]
        }
        
        available_columns = self.get_available_columns()
        dialog = IndexEditorDialog(self, index_data, available_columns)
        dialog.transient(self)
        dialog.grab_set()
        self.wait_window(dialog)
        
        new_data = dialog.get_index_data()
        if not new_data:
            return
        
        try:
            # Drop old index
            if index_data['type'] == 'PRIMARY':
                drop_query = f"ALTER TABLE {self.table_name} DROP PRIMARY KEY"
            else:
                drop_query = f"DROP INDEX {index_data['name']} ON {self.table_name}"
                
            # Create new index
            if new_data['type'] == 'PRIMARY':
                create_query = f"""
                    ALTER TABLE {self.table_name}
                    ADD PRIMARY KEY ({', '.join(new_data['columns'])})
                """
            else:
                index_type = 'UNIQUE ' if new_data['type'] == 'UNIQUE' else ''
                create_query = f"""
                    CREATE {index_type}INDEX {new_data['name']}
                    ON {self.table_name} ({', '.join(new_data['columns'])})
                """
            
            # Execute queries
            self.connection.execute_query(drop_query)
            self.connection.execute_query(create_query)
            self.load_indexes()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to edit index: {str(e)}")
    
    def delete_index(self):
        selected_item = self.index_view.selection()
        if not selected_item:
            messagebox.showinfo("Info", "Please select an index to delete")
            return
        
        current_values = self.index_view.item(selected_item[0])['values']
        index_name = current_values[0]
        index_type = current_values[1]
        
        try:
            if index_type == 'PRIMARY':
                query = f"ALTER TABLE {self.table_name} DROP PRIMARY KEY"
            else:
                query = f"DROP INDEX {index_name} ON {self.table_name}"
            
            self.connection.execute_query(query)
            self.load_indexes()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete index: {str(e)}")
