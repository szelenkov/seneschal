import tkinter as tk
from tkinter import messagebox, ttk

class ColumnEditorDialog(tk.Toplevel):
    def __init__(self, parent=None, column_data=None):
        super().__init__(parent)
        self.column_data = column_data or {}
        self.setup_ui()
        
    def setup_ui(self):
        self.title("Column Editor")
        self.minsize(400, 400)
        
        # Main frame
        main_frame = tk.Frame(self)
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Column name
        tk.Label(main_frame, text="Name:").pack(anchor='w')
        self.name_edit = tk.Entry(main_frame)
        self.name_edit.insert(0, self.column_data.get('name', ''))
        self.name_edit.pack(fill=tk.X, pady=(0, 10))
        
        # Data type
        tk.Label(main_frame, text="Type:").pack(anchor='w')
        self.type_var = tk.StringVar(value=self.column_data.get('type', 'VARCHAR'))
        self.type_combo = ttk.Combobox(main_frame, textvariable=self.type_var, 
                                       values=[
                                           'INT', 'BIGINT', 'FLOAT', 'DOUBLE', 'DECIMAL',
                                           'CHAR', 'VARCHAR', 'TEXT', 'DATE', 'DATETIME',
                                           'TIMESTAMP', 'BOOLEAN', 'BLOB'
                                       ], 
                                       state='readonly')
        self.type_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Length/Values
        tk.Label(main_frame, text="Length/Values:").pack(anchor='w')
        self.length_edit = tk.Entry(main_frame)
        self.length_edit.insert(0, self.column_data.get('length', ''))
        self.length_edit.pack(fill=tk.X, pady=(0, 10))
        
        # Not null
        self.not_null_var = tk.BooleanVar(value=self.column_data.get('not_null', False))
        self.not_null_check = tk.Checkbutton(main_frame, text="Not Null", 
                                             variable=self.not_null_var)
        self.not_null_check.pack(anchor='w', pady=(0, 10))
        
        # Default value
        tk.Label(main_frame, text="Default:").pack(anchor='w')
        self.default_edit = tk.Entry(main_frame)
        self.default_edit.insert(0, self.column_data.get('default', ''))
        self.default_edit.pack(fill=tk.X, pady=(0, 10))
        
        # Auto increment
        self.auto_increment_var = tk.BooleanVar(value=self.column_data.get('auto_increment', False))
        self.auto_increment_check = tk.Checkbutton(main_frame, text="Auto Increment", 
                                                   variable=self.auto_increment_var)
        self.auto_increment_check.pack(anchor='w', pady=(0, 10))
        
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
            'length': self.length_edit.get(),
            'not_null': self.not_null_var.get(),
            'default': self.default_edit.get(),
            'auto_increment': self.auto_increment_var.get()
        }
        self.destroy()
        
    def get_column_data(self):
        return getattr(self, 'result', None)

class StructureEditor(tk.Frame):
    def __init__(self, parent=None, connection=None, table_name=None):
        super().__init__(parent)
        self.connection = connection
        self.table_name = table_name
        self.setup_ui()
        if table_name:
            self.load_structure()
            
    def setup_ui(self):
        # Toolbar
        toolbar = tk.Frame(self)
        toolbar.pack(fill=tk.X)
        
        self.add_column_btn = tk.Button(toolbar, text="Add Column", command=self.add_column)
        self.add_column_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.edit_column_btn = tk.Button(toolbar, text="Edit Column", command=self.edit_column)
        self.edit_column_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.delete_column_btn = tk.Button(toolbar, text="Delete Column", command=self.delete_column)
        self.delete_column_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Structure view
        self.structure_view = ttk.Treeview(self, columns=(
            "Name", "Type", "Length/Values", "Not Null", 
            "Default", "Auto Increment", "Comment"
        ), show='headings')
        
        # Configure column headings
        for col in self.structure_view['columns']:
            self.structure_view.heading(col, text=col)
        
        self.structure_view.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def load_structure(self):
        if not self.connection or not self.table_name:
            return
            
        try:
            # Clear existing items
            for item in self.structure_view.get_children():
                self.structure_view.delete(item)
            
            # Get table structure
            query = f"""
                SELECT COLUMN_NAME, DATA_TYPE, 
                       CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE,
                       COLUMN_DEFAULT, EXTRA, COLUMN_COMMENT
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = '{self.table_name}'
                ORDER BY ORDINAL_POSITION
            """
            result = self.connection.execute_query(query)
            
            for row in result:
                self.structure_view.insert('', 'end', values=(
                    str(row[0]),  # Name
                    str(row[1]),  # Type
                    str(row[2]) if row[2] else '',  # Length
                    'NO' if row[3] == 'NO' else 'YES',  # Nullable
                    str(row[4]) if row[4] else '',  # Default
                    'YES' if 'auto_increment' in str(row[5]).lower() else 'NO',  # Auto Inc
                    str(row[6])  # Comment
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load table structure: {str(e)}")
            
    def add_column(self):
        dialog = ColumnEditorDialog(self)
        dialog.transient(self)
        dialog.grab_set()
        self.wait_window(dialog)
        
        column_data = dialog.get_column_data()
        if not column_data:
            return
        
        try:
            # Generate ALTER TABLE statement
            length_str = f"({column_data['length']})" if column_data['length'] else ''
            null_str = 'NOT NULL' if column_data['not_null'] else 'NULL'
            default_str = f"DEFAULT {column_data['default']}" if column_data['default'] else ''
            auto_inc_str = 'AUTO_INCREMENT' if column_data['auto_increment'] else ''
            
            query = f"""
                ALTER TABLE {self.table_name}
                ADD COLUMN {column_data['name']} {column_data['type']}{length_str}
                {null_str} {default_str} {auto_inc_str}
            """
            
            self.connection.execute_query(query)
            self.load_structure()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add column: {str(e)}")
                
    def edit_column(self):
        selected_item = self.structure_view.selection()
        if not selected_item:
            messagebox.showinfo("Info", "Please select a column to edit")
            return
            
        current_values = self.structure_view.item(selected_item[0])['values']
        column_data = {
            'name': current_values[0],
            'type': current_values[1],
            'length': current_values[2],
            'not_null': current_values[3] == 'NO',
            'default': current_values[4],
            'auto_increment': current_values[5] == 'YES'
        }
        
        dialog = ColumnEditorDialog(self, column_data)
        dialog.transient(self)
        dialog.grab_set()
        self.wait_window(dialog)
        
        new_data = dialog.get_column_data()
        if not new_data:
            return
        
        try:
            # Generate ALTER TABLE statement
            length_str = f"({new_data['length']})" if new_data['length'] else ''
            null_str = 'NOT NULL' if new_data['not_null'] else 'NULL'
            default_str = f"DEFAULT {new_data['default']}" if new_data['default'] else ''
            auto_inc_str = 'AUTO_INCREMENT' if new_data['auto_increment'] else ''
            
            query = f"""
                ALTER TABLE {self.table_name}
                MODIFY COLUMN {new_data['name']} {new_data['type']}{length_str}
                {null_str} {default_str} {auto_inc_str}
            """
            
            self.connection.execute_query(query)
            self.load_structure()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to modify column: {str(e)}")
    
    def delete_column(self):
        selected_item = self.structure_view.selection()
        if not selected_item:
            messagebox.showinfo("Info", "Please select a column to delete")
            return
        
        column_name = self.structure_view.item(selected_item[0])['values'][0]
        
        try:
            query = f"ALTER TABLE {self.table_name} DROP COLUMN {column_name}"
            
            self.connection.execute_query(query)
            self.load_structure()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete column: {str(e)}")
