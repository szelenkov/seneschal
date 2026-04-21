"""
Login and connection dialogs
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Tuple
from dataclasses import dataclass

from ..db.connection import ConnectionInfo, ConnectionManager
from .framework import Dialog, Button, Entry, Label, Frame


class ConnectionDialog(Dialog):
    """Dialog for creating/editing database connections"""
    
    def __init__(self, parent: tk.Tk, conn_mgr: ConnectionManager, existing_profile: Optional[str] = None, **kwargs):
        super().__init__(parent, title="Database Connection", **kwargs)
        self.conn_mgr = conn_mgr
        self.existing_profile = existing_profile
        self.conn_info: Optional[ConnectionInfo] = None
        
        # Pre-fill if editing
        if existing_profile:
            self.conn_info = conn_mgr.get_profile(existing_profile)
        
        self.geometry("400x500")
    
    def build_ui(self) -> None:
        """Build connection dialog UI"""
        # Connection name
        ttk.Label(self, text="Connection Name:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.name_var = tk.StringVar(value=self.existing_profile or "")
        ttk.Entry(self, textvariable=self.name_var).grid(row=0, column=1, sticky=tk.EW, padx=10, pady=5)
        
        # Database type
        ttk.Label(self, text="Database Type:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.db_type_var = tk.StringVar(value=self.conn_info.db_type if self.conn_info else "mysql")
        type_combo = ttk.Combobox(
            self,
            textvariable=self.db_type_var,
            values=["mysql", "postgresql", "mssql", "sqlite"],
            state="readonly"
        )
        type_combo.grid(row=1, column=1, sticky=tk.EW, padx=10, pady=5)
        type_combo.bind("<<ComboboxSelected>>", self._on_db_type_changed)
        
        # Host
        ttk.Label(self, text="Host:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        self.host_var = tk.StringVar(value=self.conn_info.host if self.conn_info else "localhost")
        ttk.Entry(self, textvariable=self.host_var).grid(row=2, column=1, sticky=tk.EW, padx=10, pady=5)
        
        # Port
        ttk.Label(self, text="Port:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        self.port_var = tk.StringVar(value=str(self.conn_info.port if self.conn_info else 3306))
        ttk.Entry(self, textvariable=self.port_var).grid(row=3, column=1, sticky=tk.EW, padx=10, pady=5)
        
        # Database
        ttk.Label(self, text="Database:").grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
        self.db_var = tk.StringVar(value=self.conn_info.database if self.conn_info else "")
        ttk.Entry(self, textvariable=self.db_var).grid(row=4, column=1, sticky=tk.EW, padx=10, pady=5)
        
        # Username
        ttk.Label(self, text="Username:").grid(row=5, column=0, sticky=tk.W, padx=10, pady=5)
        self.username_var = tk.StringVar(value=self.conn_info.username if self.conn_info else "")
        ttk.Entry(self, textvariable=self.username_var).grid(row=5, column=1, sticky=tk.EW, padx=10, pady=5)
        
        # Password
        ttk.Label(self, text="Password:").grid(row=6, column=0, sticky=tk.W, padx=10, pady=5)
        self.password_var = tk.StringVar(value=self.conn_info.password if self.conn_info else "")
        ttk.Entry(self, textvariable=self.password_var, show="*").grid(row=6, column=1, sticky=tk.EW, padx=10, pady=5)
        
        # Charset
        ttk.Label(self, text="Charset:").grid(row=7, column=0, sticky=tk.W, padx=10, pady=5)
        self.charset_var = tk.StringVar(value=self.conn_info.charset if self.conn_info else "utf8mb4")
        ttk.Entry(self, textvariable=self.charset_var).grid(row=7, column=1, sticky=tk.EW, padx=10, pady=5)
        
        # SSL
        self.ssl_var = tk.BooleanVar(value=self.conn_info.ssl_enabled if self.conn_info else False)
        ttk.Checkbutton(self, text="Use SSL", variable=self.ssl_var).grid(row=8, column=0, columnspan=2, sticky=tk.W, padx=10, pady=5)
        
        # SSH
        self.ssh_var = tk.BooleanVar(value=self.conn_info.ssh_enabled if self.conn_info else False)
        ttk.Checkbutton(self, text="Use SSH Tunnel", variable=self.ssh_var).grid(row=9, column=0, columnspan=2, sticky=tk.W, padx=10, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.grid(row=10, column=0, columnspan=2, sticky=tk.EW, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Test Connection", command=self._test_connection).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="OK", command=self._ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.close).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        self.columnconfigure(1, weight=1)
    
    def _on_db_type_changed(self, event=None):
        """Handle database type change"""
        db_type = self.db_type_var.get()
        
        # Set default port based on type
        if db_type == "mysql":
            self.port_var.set("3306")
            self.host_var.set("localhost")
        elif db_type == "postgresql":
            self.port_var.set("5432")
            self.host_var.set("localhost")
        elif db_type == "mssql":
            self.port_var.set("1433")
            self.host_var.set("localhost")
        elif db_type == "sqlite":
            self.host_var.set("")  # For SQLite, host is file path
            self.port_var.set("")
    
    async def _test_connection(self):
        """Test database connection"""
        conn_info = ConnectionInfo(
            name=self.name_var.get(),
            db_type=self.db_type_var.get(),
            host=self.host_var.get(),
            port=int(self.port_var.get()) if self.port_var.get() else 0,
            database=self.db_var.get(),
            username=self.username_var.get(),
            password=self.password_var.get(),
            charset=self.charset_var.get(),
            ssl_enabled=self.ssl_var.get(),
            ssh_enabled=self.ssh_var.get()
        )
        
        success, message = await self.conn_mgr.test_connection(conn_info)
        if success:
            messagebox.showinfo("Connection Test", "Connection successful!")
        else:
            messagebox.showerror("Connection Test", f"Connection failed:\n{message}")
    
    def _ok_clicked(self):
        """Handle OK button"""
        if not self.name_var.get():
            messagebox.showerror("Validation", "Please enter a connection name")
            return
        
        conn_info = ConnectionInfo(
            name=self.name_var.get(),
            db_type=self.db_type_var.get(),
            host=self.host_var.get(),
            port=int(self.port_var.get()) if self.port_var.get() else 0,
            database=self.db_var.get(),
            username=self.username_var.get(),
            password=self.password_var.get(),
            charset=self.charset_var.get(),
            ssl_enabled=self.ssl_var.get(),
            ssh_enabled=self.ssh_var.get()
        )
        
        self.conn_mgr.add_profile(conn_info)
        self.close(conn_info.name)


class LoginDialog(Dialog):
    """Login dialog to select or create connection"""
    
    def __init__(self, parent: tk.Tk, conn_mgr: ConnectionManager, **kwargs):
        super().__init__(parent, title="Login - Seneschal", **kwargs)
        self.conn_mgr = conn_mgr
        self.geometry("300x200")
    
    def build_ui(self) -> None:
        """Build login dialog UI"""
        # Recent connections
        ttk.Label(self, text="Recent Connections:").pack(pady=5)
        
        profiles = self.conn_mgr.list_profiles()
        if profiles:
            self.profile_var = tk.StringVar(value=profiles[0])
            combo = ttk.Combobox(
                self,
                textvariable=self.profile_var,
                values=profiles,
                state="readonly"
            )
            combo.pack(fill=tk.X, padx=10, pady=5)
        else:
            ttk.Label(self, text="No saved connections").pack(pady=5)
            self.profile_var = None
        
        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        if self.profile_var:
            ttk.Button(button_frame, text="Connect", command=self._connect).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="New Connection", command=self._new_connection).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exit", command=self.close).pack(side=tk.LEFT, padx=5)
    
    def _connect(self):
        """Connect to selected profile"""
        if self.profile_var:
            self.close(self.profile_var.get())
    
    def _new_connection(self):
        """Open new connection dialog"""
        dialog = ConnectionDialog(self, self.conn_mgr)
        result = dialog.show()
        if result:
            self.close(result)

