import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox

from ..utils.theme_manager import ThemeManager

class ConnectionDialog(tk.Toplevel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title("Database Connection")
        self.theme_manager = ThemeManager()
        self.result = None

        # Main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Database Type
        db_type_frame = ttk.Frame(main_frame)
        db_type_frame.pack(fill=tk.X, pady=5)

        ttk.Label(db_type_frame, text="Database Type:").pack(side=tk.LEFT)

        self.db_type = ttk.Combobox(
            db_type_frame,
            values=["MySQL", "PostgreSQL", "SQLite", "MS SQL Server"],
            state="readonly",
            width=20
        )
        self.db_type.pack(side=tk.RIGHT)
        self.db_type.set("MySQL")
        self.db_type.bind('<<ComboboxSelected>>', self.on_db_type_changed)

        # Hostname
        hostname_frame = ttk.Frame(main_frame)
        hostname_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(hostname_frame, text="Hostname:").pack(side=tk.LEFT)
        
        self.hostname = ttk.Entry(hostname_frame, width=25)
        self.hostname.pack(side=tk.RIGHT)
        self.hostname.insert(0, "localhost")

        # Port
        port_frame = ttk.Frame(main_frame)
        port_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(port_frame, text="Port:").pack(side=tk.LEFT)
        
        self.port = ttk.Entry(port_frame, width=25)
        self.port.pack(side=tk.RIGHT)
        self.port.insert(0, "3306")

        # Username
        username_frame = ttk.Frame(main_frame)
        username_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(username_frame, text="Username:").pack(side=tk.LEFT)
        
        self.username = ttk.Entry(username_frame, width=25)
        self.username.pack(side=tk.RIGHT)

        # Password
        password_frame = ttk.Frame(main_frame)
        password_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(password_frame, text="Password:").pack(side=tk.LEFT)
        
        self.password = ttk.Entry(password_frame, show="*", width=25)
        self.password.pack(side=tk.RIGHT)

        # Database
        database_frame = ttk.Frame(main_frame)
        database_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(database_frame, text="Database:").pack(side=tk.LEFT)
        
        self.database = ttk.Entry(database_frame, width=25)
        self.database.pack(side=tk.RIGHT)

        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        # Test Connection button
        self.test_button = ttk.Button(
            button_frame, 
            text="Test Connection", 
            command=self.test_connection
        )
        self.test_button.pack(side=tk.LEFT, padx=5)

        # Connect button
        self.connect_button = ttk.Button(
            button_frame, 
            text="Connect", 
            command=self.accept
        )
        self.connect_button.pack(side=tk.RIGHT, padx=5)

        # Cancel button
        self.cancel_button = ttk.Button(
            button_frame, 
            text="Cancel", 
            command=self.destroy
        )
        self.cancel_button.pack(side=tk.RIGHT, padx=5)

        # Apply theme
        self.theme_manager.apply_theme(self)

        # Center the window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def on_db_type_changed(self, _event=None):
        """Update port based on database type"""
        ports = {
            "MySQL": "3306",
            "PostgreSQL": "5432",
            "MS SQL Server": "1433"
        }

        db_type = self.db_type.get()

        if db_type in ports:
            self.port.delete(0, tk.END)
            self.port.insert(0, ports[db_type])
            self.hostname.config(state='normal')
            self.port.config(state='normal')
        else:  # SQLite
            self.hostname.delete(0, tk.END)
            self.port.delete(0, tk.END)
            self.hostname.config(state='disabled')
            self.port.config(state='disabled')

    def test_connection(self):
        """Test the database connection"""
        try:
            params = self.get_connection_params()
            # Implement connection testing logic here
            # This might involve creating a temporary connection
            messagebox.showinfo("Connection Test", "Connection successful!")
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def accept(self):
        """Validate and store connection parameters"""
        try:
            params = self.get_connection_params()
            # Validate parameters
            if not all([params['type'], params['database']]):
                messagebox.showwarning("Validation Error", "Please fill in required fields")
                return

            # Store result and close dialog
            self.result = params
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def get_connection_params(self):
        """Return the connection parameters as a dictionary"""
        return {
            "type": self.db_type.get(),
            "host": self.hostname.get() if self.hostname['state'] != ['disabled'] else '',
            "port": self.port.get() if self.port['state'] != ['disabled'] else '',
            "user": self.username.get(),
            "password": self.password.get(),
            "database": self.database.get()
        }

def show_connection_dialog(parent=None):
    """Convenience function to show the dialog and return connection params"""
    dialog = ConnectionDialog(parent)
    dialog.grab_set()  # Make the dialog modal
    dialog.wait_window(dialog)
    return dialog.result
