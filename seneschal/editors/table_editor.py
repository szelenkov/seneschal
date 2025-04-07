import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import tkinter.simpledialog as simpledialog

from ..utils.settings_manager import SettingsManager
from ..utils.theme_manager import ThemeManager

class TableEditor(tk.Frame):
    def __init__(self, parent=None, connection=None, table_name=None):
        super().__init__(parent)
        self.connection = connection
        self.table_name = table_name
        self.settings = SettingsManager()
        self.theme_manager = ThemeManager()
        
        self.setup_ui()
        if table_name:
            self.load_table_data()

    def setup_ui(self):
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create tab widget
        self.tab_widget = ttk.Notebook(self)
        self.tab_widget.grid(row=0, column=0, sticky='nsew')

        # Data tab
        self.data_tab = ttk.Frame(self.tab_widget)
        self.data_tab.grid_columnconfigure(0, weight=1)
        self.data_tab.grid_rowconfigure(1, weight=1)

        # Toolbar for data operations
        toolbar = ttk.Frame(self.data_tab)
        toolbar.grid(row=0, column=0, sticky='ew', padx=5, pady=5)

        # Add Row button
        self.add_row_btn = ttk.Button(
            toolbar, 
            text="Add Row", 
            command=self.add_row
        )
        self.add_row_btn.pack(side=tk.LEFT, padx=5)

        # Delete Row button
        self.delete_row_btn = ttk.Button(
            toolbar, 
            text="Delete Row", 
            command=self.delete_row
        )
        self.delete_row_btn.pack(side=tk.LEFT, padx=5)

        # Save Changes button
        self.save_changes_btn = ttk.Button(
            toolbar, 
            text="Save Changes", 
            command=self.save_changes
        )
        self.save_changes_btn.pack(side=tk.LEFT, padx=5)

        # Table view
        self.table_view = ttk.Treeview(
            self.data_tab, 
            show='headings'
        )
        self.table_view.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)

        # Scrollbars for table view
        y_scrollbar = ttk.Scrollbar(
            self.data_tab, 
            orient=tk.VERTICAL, 
            command=self.table_view.yview
        )
        y_scrollbar.grid(row=1, column=1, sticky='ns')
        
        x_scrollbar = ttk.Scrollbar(
            self.data_tab, 
            orient=tk.HORIZONTAL, 
            command=self.table_view.xview
        )
        x_scrollbar.grid(row=2, column=0, sticky='ew')

        self.table_view.configure(
            yscrollcommand=y_scrollbar.set,
            xscrollcommand=x_scrollbar.set
        )

        # Add tabs to notebook
        self.tab_widget.add(self.data_tab, text="Data")

        # Apply theme
        self.theme_manager.apply_theme(self)

    def load_table_data(self):
        if not self.connection or not self.table_name:
            return
            
        try:
            # Load table data
            query = f"SELECT * FROM {self.table_name}"
            result = self.connection.execute_query(query)
            
            # Clear existing data
            for item in self.table_view.get_children():
                self.table_view.delete(item)
            
            # Clear existing columns
            self.table_view['columns'] = []
            
            # Set headers and columns
            if result and len(result) > 0:
                headers = list(result[0].keys())
                self.table_view['columns'] = headers
                
                # Configure column headings
                for header in headers:
                    self.table_view.heading(header, text=header)
                    self.table_view.column(header, anchor='center')
                
                # Add data
                for row in result:
                    values = [str(row.get(header, '')) for header in headers]
                    self.table_view.insert('', 'end', values=values)
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load table data: {str(e)}")

    def add_row(self):
        try:
            # Get column names from table view
            columns = self.table_view['columns']
            
            # Prompt user for values
            row_values = {}
            for column in columns:
                value = simpledialog.askstring(
                    "Add Row", 
                    f"Enter value for {column}:", 
                    parent=self
                )
                row_values[column] = value if value else 'NULL'
            
            # Construct INSERT query
            columns_str = ', '.join(columns)
            values_str = ', '.join(f"'{val}'" for val in row_values.values())
            
            query = f"""
                INSERT INTO {self.table_name} ({columns_str})
                VALUES ({values_str})
            """
            
            self.connection.execute_query(query)
            
            # Refresh data
            self.load_table_data()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add row: {str(e)}")

    def delete_row(self):
        # Get selected item
        selected_item = self.table_view.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "No row selected")
            return
        
        try:
            # Get column names
            columns = self.table_view['columns']
            
            # Get values of selected row
            row_values = self.table_view.item(selected_item[0])['values']
            
            # Attempt to find primary key
            pk_query = f"""
                SELECT k.COLUMN_NAME
                FROM information_schema.table_constraints t
                JOIN information_schema.key_column_usage k
                USING(constraint_name,table_schema,table_name)
                WHERE t.constraint_type='PRIMARY KEY'
                AND t.table_name='{self.table_name}'
            """
            pk_result = self.connection.execute_query(pk_query)
            
            if pk_result:
                pk_column = pk_result[0][0]
                pk_index = columns.index(pk_column)
                pk_value = row_values[pk_index]
                
                # Delete row
                query = f"""
                    DELETE FROM {self.table_name}
                    WHERE {pk_column} = '{pk_value}'
                """
                self.connection.execute_query(query)
                
                # Refresh data
                self.load_table_data()
            else:
                messagebox.showwarning(
                    "Warning",
                    "Cannot delete row: No primary key found in table"
                )
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete row: {str(e)}")

    @staticmethod
    def save_changes():
        # In a Tkinter implementation, changes are typically saved 
        # immediately after each edit or when adding/deleting rows
        messagebox.showinfo("Save Changes", "Changes are saved automatically")
