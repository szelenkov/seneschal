import os
import json
from datetime import datetime
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QListWidget, QInputDialog,
                           QMessageBox)
from PyQt6.QtCore import QSettings

class QueryManager:
    def __init__(self):
        self.settings = QSettings('Seneschal', 'Python')
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

class QueryManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.query_manager = QueryManager()
        self.setup_ui()
        self.load_queries()
        
    def setup_ui(self):
        self.setWindowTitle("Query Manager")
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # Query list
        self.query_list = QListWidget()
        self.query_list.itemDoubleClicked.connect(self.load_selected_query)
        layout.addWidget(self.query_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.new_button = QPushButton("New")
        self.new_button.clicked.connect(self.new_query)
        button_layout.addWidget(self.new_button)
        
        self.load_button = QPushButton("Load")
        self.load_button.clicked.connect(self.load_selected_query)
        button_layout.addWidget(self.load_button)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_selected_query)
        button_layout.addWidget(self.delete_button)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
    def load_queries(self):
        """Load saved queries into the list"""
        self.query_list.clear()
        self.query_list.addItems(self.query_manager.get_query_list())
        
    def new_query(self):
        """Create a new saved query"""
        name, ok = QInputDialog.getText(
            self,
            "New Query",
            "Enter name for the query:"
        )
        if ok and name:
            sql, ok = QInputDialog.getMultiLineText(
                self,
                "New Query",
                "Enter SQL query:"
            )
            if ok and sql:
                if self.query_manager.save_query(name, sql):
                    self.load_queries()
                else:
                    QMessageBox.critical(
                        self,
                        "Error",
                        "Failed to save query"
                    )
                    
    def load_selected_query(self):
        """Load the selected query"""
        current = self.query_list.currentItem()
        if current:
            sql = self.query_manager.load_query(current.text())
            if sql:
                # Emit signal or call callback to load query in editor
                self.parent().load_query(sql)
                self.accept()
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Failed to load query"
                )
                
    def delete_selected_query(self):
        """Delete the selected query"""
        current = self.query_list.currentItem()
        if current:
            if QMessageBox.question(
                self,
                "Confirm Delete",
                f"Delete query '{current.text()}'?"
            ) == QMessageBox.StandardButton.Yes:
                if self.query_manager.delete_query(current.text()):
                    self.load_queries()
                else:
                    QMessageBox.critical(
                        self,
                        "Error",
                        "Failed to delete query"
                    )
