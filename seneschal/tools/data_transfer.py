import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
import csv
import json
import threading
from datetime import datetime
import tkinter.simpledialog as simpledialog

class DataTransferWorker(threading.Thread):
    def __init__(self, connection, export_settings, progress_callback, completion_callback, error_callback):
        super().__init__()
        self.connection = connection
        self.settings = export_settings
        self.progress_callback = progress_callback
        self.completion_callback = completion_callback
        self.error_callback = error_callback
        
    def run(self):
        try:
            if self.settings['operation'] == 'export':
                self.export_data()
            else:
                self.import_data()
        except Exception as e:
            self.error_callback(str(e))
        finally:
            self.completion_callback()
            
    def export_data(self):
        query = f"SELECT * FROM {self.settings['table']}"
        result = self.connection.execute_query(query)
        
        total_rows = len(result)
        processed_rows = 0
        
        if self.settings['format'] == 'csv':
            with open(self.settings['filename'], 'w', newline='') as f:
                writer = csv.writer(f)
                # Write headers
                if self.settings['include_headers']:
                    writer.writerow(result[0].keys())
                
                # Write data
                for row in result:
                    writer.writerow(list(row.values()))
                    processed_rows += 1
                    self.progress_callback(int(processed_rows * 100 / total_rows))
                    
        elif self.settings['format'] == 'json':
            data = []
            
            for row in result:
                data.append(dict(row))
                processed_rows += 1
                self.progress_callback(int(processed_rows * 100 / total_rows))
                
            with open(self.settings['filename'], 'w') as f:
                json.dump(data, f, indent=2)
                
        elif self.settings['format'] == 'sql':
            with open(self.settings['filename'], 'w') as f:
                # Write header
                f.write(f"-- Export of table {self.settings['table']}\n")
                f.write(f"-- Date: {datetime.now()}\n\n")
                
                if self.settings['include_structure']:
                    # Get table structure
                    create_table = self.connection.execute_query(
                        f"SHOW CREATE TABLE {self.settings['table']}"
                    )
                    f.write(f"{create_table[0][1]};\n\n")
                
                # Write data
                headers = result[0].keys()
                for row in result:
                    values = []
                    for val in row.values():
                        if val is None:
                            values.append('NULL')
                        elif isinstance(val, (int, float)):
                            values.append(str(val))
                        else:
                            values.append(f"'{str(val)}'")
                            
                    f.write(
                        f"INSERT INTO {self.settings['table']} "
                        f"({', '.join(headers)}) VALUES ({', '.join(values)});\n"
                    )
                    
                    processed_rows += 1
                    self.progress_callback(int(processed_rows * 100 / total_rows))
                    
    def import_data(self):
        if self.settings['format'] == 'csv':
            with open(self.settings['filename'], 'r') as f:
                reader = csv.reader(f)
                headers = next(reader) if self.settings['include_headers'] else None
                
                # Get total rows for progress
                total_rows = sum(1 for _ in reader)
                f.seek(0)
                if self.settings['include_headers']:
                    next(reader)  # Skip header row
                    
                processed_rows = 0
                for row in reader:
                    if headers:
                        placeholders = ', '.join(['?' for _ in row])
                        query = f"""
                            INSERT INTO {self.settings['table']}
                            ({', '.join(headers)}) VALUES ({placeholders})
                        """
                    else:
                        placeholders = ', '.join(['?' for _ in row])
                        query = f"""
                            INSERT INTO {self.settings['table']}
                            VALUES ({placeholders})
                        """
                        
                    self.connection.execute_query(query, row)
                    processed_rows += 1
                    self.progress_callback(int(processed_rows * 100 / total_rows))

class DataTransferTool(ttk.Frame):
    def __init__(self, parent=None, connection=None):
        super().__init__(parent)
        self.connection = connection
        
        # Track current transfer operation
        self.current_transfer = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        # Operation selection
        operation_frame = ttk.LabelFrame(self, text="Operation")
        operation_frame.grid(row=0, column=0, padx=10, pady=5, sticky='ew')
        
        ttk.Label(operation_frame, text="Operation:").pack(side=tk.LEFT, padx=5)
        
        self.operation = ttk.Combobox(
            operation_frame, 
            values=["Export", "Import"],
            state="readonly",
            width=20
        )
        self.operation.pack(side=tk.RIGHT, padx=5)
        self.operation.set("Export")
        self.operation.bind('<<ComboboxSelected>>', self.update_ui_state)

        # Format settings
        format_frame = ttk.LabelFrame(self, text="Format Settings")
        format_frame.grid(row=1, column=0, padx=10, pady=5, sticky='ew')

        # Format selection
        format_subframe = ttk.Frame(format_frame)
        format_subframe.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(format_subframe, text="Format:").pack(side=tk.LEFT)
        
        self.format = ttk.Combobox(
            format_subframe, 
            values=["CSV", "JSON", "SQL"],
            state="readonly",
            width=20
        )
        self.format.pack(side=tk.RIGHT)
        self.format.set("CSV")
        self.format.bind('<<ComboboxSelected>>', self.update_ui_state)

        # Checkboxes
        self.include_headers = ttk.Checkbutton(format_frame, text="Include Headers")
        self.include_headers.pack(anchor=tk.W, padx=5)
        
        self.include_structure = ttk.Checkbutton(
            format_frame, 
            text="Include Table Structure (SQL only)"
        )
        self.include_structure.pack(anchor=tk.W, padx=5)

        # File selection
        file_frame = ttk.LabelFrame(self, text="File Selection")
        file_frame.grid(row=2, column=0, padx=10, pady=5, sticky='ew')

        file_subframe = ttk.Frame(file_frame)
        file_subframe.pack(fill=tk.X, padx=5, pady=5)
        
        self.filename_label = ttk.Label(file_subframe, text="No file selected")
        self.filename_label.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        self.browse_button = ttk.Button(
            file_subframe, 
            text="Browse...", 
            command=self.browse_file
        )
        self.browse_button.pack(side=tk.RIGHT)

        # Progress
        progress_frame = ttk.LabelFrame(self, text="Progress")
        progress_frame.grid(row=3, column=0, padx=10, pady=5, sticky='ew')

        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            orient='horizontal', 
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X, padx=5, pady=5)

        # Transfer button
        self.transfer_button = ttk.Button(
            self, 
            text="Start Transfer", 
            command=self.start_transfer
        )
        self.transfer_button.grid(row=4, column=0, padx=10, pady=5, sticky='ew')

        # Initial UI state update
        self.update_ui_state()

    def update_ui_state(self):
        """Update UI elements based on current selections"""
        format_selected = self.format.get()
        
        # Enable/disable structure checkbox only for SQL
        if format_selected == 'SQL':
            self.include_structure.state(['!disabled'])
        else:
            self.include_structure.state(['disabled'])

    def browse_file(self):
        """Open file dialog to select export/import file"""
        operation = self.operation.get().lower()
        file_types = [
            ('CSV Files', '*.csv'),
            ('JSON Files', '*.json'),
            ('SQL Files', '*.sql'),
            ('All Files', '*.*')
        ]
        
        if operation == 'export':
            filename = filedialog.asksaveasfilename(
                defaultextension=f".{self.format.get().lower()}",
                filetypes=file_types
            )
        else:
            filename = filedialog.askopenfilename(
                filetypes=file_types
            )
        
        if filename:
            self.filename_label.config(text=filename)

    def start_transfer(self):
        """Start data transfer process"""
        # Validate inputs
        if not self.connection:
            messagebox.showerror("Error", "No database connection established")
            return

        filename = self.filename_label.cget('text')
        if filename == "No file selected":
            messagebox.showerror("Error", "Please select a file")
            return

        # Prepare transfer settings
        transfer_settings = {
            'operation': self.operation.get().lower(),
            'format': self.format.get().lower(),
            'filename': filename,
            'table': self.get_table_name(),  # You'll need to implement this method
            'include_headers': 'selected' in self.include_headers.state(),
            'include_structure': 'selected' in self.include_structure.state()
        }

        # Reset progress bar
        self.progress_bar['value'] = 0
        
        # Disable transfer button during operation
        self.transfer_button.config(state='disabled')

        # Start transfer in a separate thread
        self.current_transfer = DataTransferWorker(
            self.connection, 
            transfer_settings, 
            self.update_progress, 
            self.transfer_complete, 
            self.handle_transfer_error
        )
        self.current_transfer.start()

    def update_progress(self, value):
        """Update progress bar from worker thread"""
        self.after(0, lambda: self.progress_bar.config(value=value))

    def transfer_complete(self):
        """Handle successful transfer completion"""
        self.after(0, self._finalize_transfer)

    def handle_transfer_error(self, error_message):
        """Handle errors during transfer"""
        self.after(0, lambda: messagebox.showerror("Transfer Error", error_message))
        self.after(0, self._finalize_transfer)

    def _finalize_transfer(self):
        """Reset UI after transfer completes or fails"""
        self.progress_bar['value'] = 0
        self.transfer_button.config(state='normal')
        self.current_transfer = None

    @staticmethod
    def get_table_name():
        """Prompt user to select a table name"""
        # This is a placeholder. You might want to implement a more robust 
        # method of selecting tables, perhaps with a dropdown or dialog
        table_name = simpledialog.askstring(
            "Table Selection", 
            "Enter the table name for transfer:"
        )
        return table_name

def create_data_transfer_tool(parent, connection):
    """Convenience function to create and return a data transfer tool"""
    return DataTransferTool(parent, connection)
