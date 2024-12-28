from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QComboBox, QPushButton, QFormLayout)
from PyQt6.QtCore import Qt

class ConnectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Database Connection")
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Connection type
        form_layout = QFormLayout()
        self.db_type = QComboBox()
        self.db_type.addItems(["MySQL", "PostgreSQL", "SQLite", "MS SQL Server"])
        form_layout.addRow("Database Type:", self.db_type)
        
        # Connection details
        self.hostname = QLineEdit()
        self.hostname.setText("localhost")
        form_layout.addRow("Hostname:", self.hostname)
        
        self.port = QLineEdit()
        self.port.setText("3306")  # Default MySQL port
        form_layout.addRow("Port:", self.port)
        
        self.username = QLineEdit()
        form_layout.addRow("Username:", self.username)
        
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Password:", self.password)
        
        self.database = QLineEdit()
        form_layout.addRow("Database:", self.database)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.test_button = QPushButton("Test Connection")
        self.connect_button = QPushButton("Connect")
        self.cancel_button = QPushButton("Cancel")
        
        button_layout.addWidget(self.test_button)
        button_layout.addStretch()
        button_layout.addWidget(self.connect_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # Connect signals
        self.connect_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        self.db_type.currentTextChanged.connect(self.on_db_type_changed)
        
        self.setLayout(layout)
        
    def on_db_type_changed(self, db_type):
        """Update port based on database type"""
        ports = {
            "MySQL": "3306",
            "PostgreSQL": "5432",
            "MS SQL Server": "1433"
        }
        if db_type in ports:
            self.port.setText(ports[db_type])
            self.hostname.setEnabled(True)
            self.port.setEnabled(True)
        else:  # SQLite
            self.hostname.setEnabled(False)
            self.port.setEnabled(False)
            
    def get_connection_params(self):
        """Return the connection parameters as a dictionary"""
        return {
            "type": self.db_type.currentText(),
            "host": self.hostname.text(),
            "port": self.port.text(),
            "user": self.username.text(),
            "password": self.password.text(),
            "database": self.database.text()
        }
