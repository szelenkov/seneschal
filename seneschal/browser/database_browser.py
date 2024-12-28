from PyQt6.QtWidgets import (QTreeView, QMenu, QMessageBox, QInputDialog)
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt, pyqtSignal
import logging

class DatabaseBrowser(QTreeView):
    item_selected = pyqtSignal(str, str)  # type, name
    
    def __init__(self, parent=None, connection=None):
        super().__init__(parent)
        self.connection = connection
        self.setup_ui()
        
    def setup_ui(self):
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Database Objects"])
        self.setModel(self.model)
        
        # Enable selection
        self.setSelectionMode(QTreeView.SelectionMode.SingleSelection)
        self.clicked.connect(self.on_item_clicked)
        
    def refresh_databases(self):
        if not self.connection or not self.connection.connected:
            return
            
        self.model.clear()
        self.model.setHorizontalHeaderLabels(["Database Objects"])
        
        try:
            # Get list of databases using the connection's method
            databases = self.connection.get_databases()
            
            for db_name in databases:
                db_item = QStandardItem(db_name)
                db_item.setData("database", Qt.ItemDataRole.UserRole)
                
                # Add standard folders for each database
                tables_folder = QStandardItem("Tables")
                tables_folder.setData("tables_folder", Qt.ItemDataRole.UserRole)
                
                views_folder = QStandardItem("Views")
                views_folder.setData("views_folder", Qt.ItemDataRole.UserRole)
                
                procedures_folder = QStandardItem("Stored Procedures")
                procedures_folder.setData("procedures_folder", Qt.ItemDataRole.UserRole)
                
                functions_folder = QStandardItem("Functions")
                functions_folder.setData("functions_folder", Qt.ItemDataRole.UserRole)
                
                triggers_folder = QStandardItem("Triggers")
                triggers_folder.setData("triggers_folder", Qt.ItemDataRole.UserRole)
                
                db_item.appendRow(tables_folder)
                db_item.appendRow(views_folder)
                db_item.appendRow(procedures_folder)
                db_item.appendRow(functions_folder)
                db_item.appendRow(triggers_folder)
                
                self.model.appendRow(db_item)
                
        except Exception as e:
            logging.error(f"Failed to load databases: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load databases: {str(e)}")
            
    def refresh_database_objects(self, db_name):
        if not self.connection or not self.connection.connected:
            return
            
        try:
            # Switch to the selected database
            self.connection.execute_query(f"USE {db_name}")
            
            # Get tables
            tables = self.connection.execute_query("SHOW TABLES")
            tables_folder = self.find_folder(db_name, "Tables")
            if tables_folder:
                tables_folder.removeRows(0, tables_folder.rowCount())
                for table in tables:
                    item = QStandardItem(table[0])
                    item.setData("table", Qt.ItemDataRole.UserRole)
                    tables_folder.appendRow(item)
                    
            # Get views
            views = self.connection.execute_query("SHOW FULL TABLES WHERE Table_type = 'VIEW'")
            views_folder = self.find_folder(db_name, "Views")
            if views_folder:
                views_folder.removeRows(0, views_folder.rowCount())
                for view in views:
                    item = QStandardItem(view[0])
                    item.setData("view", Qt.ItemDataRole.UserRole)
                    views_folder.appendRow(item)
                    
            # Get procedures
            procedures = self.connection.execute_query(
                "SELECT ROUTINE_NAME FROM INFORMATION_SCHEMA.ROUTINES "
                "WHERE ROUTINE_TYPE='PROCEDURE' AND ROUTINE_SCHEMA=?", 
                (db_name,)
            )
            procedures_folder = self.find_folder(db_name, "Stored Procedures")
            if procedures_folder:
                procedures_folder.removeRows(0, procedures_folder.rowCount())
                for proc in procedures:
                    item = QStandardItem(proc[0])
                    item.setData("procedure", Qt.ItemDataRole.UserRole)
                    procedures_folder.appendRow(item)
                    
        except Exception as e:
            logging.error(f"Failed to load database objects: {str(e)}")
            QMessageBox.critical(self, "Error", 
                               f"Failed to load database objects: {str(e)}")
            
    def find_folder(self, db_name, folder_name):
        for i in range(self.model.rowCount()):
            db_item = self.model.item(i)
            if db_item.text() == db_name:
                for j in range(db_item.rowCount()):
                    folder_item = db_item.child(j)
                    if folder_item.text() == folder_name:
                        return folder_item
        return None
        
    def on_item_clicked(self, index):
        item = self.model.itemFromIndex(index)
        if not item:
            return
            
        item_type = item.data(Qt.ItemDataRole.UserRole)
        if item_type in ["table", "view", "procedure", "function"]:
            self.item_selected.emit(item_type, item.text())
            
    def show_context_menu(self, position):
        index = self.indexAt(position)
        if not index.isValid():
            return
            
        item = self.model.itemFromIndex(index)
        item_type = item.data(Qt.ItemDataRole.UserRole)
        
        menu = QMenu()
        
        if item_type == "database":
            menu.addAction("Refresh", lambda: self.refresh_database_objects(item.text()))
            menu.addSeparator()
            menu.addAction("Create Database...")
            menu.addAction("Drop Database...")
            
        elif item_type == "table":
            menu.addAction("Open Table", lambda: self.item_selected.emit("table", item.text()))
            menu.addAction("Design Table...")
            menu.addSeparator()
            menu.addAction("Create Table...")
            menu.addAction("Drop Table...")
            menu.addSeparator()
            menu.addAction("Truncate Table...")
            menu.addAction("Rename Table...")
            
        elif item_type == "view":
            menu.addAction("Open View", lambda: self.item_selected.emit("view", item.text()))
            menu.addAction("Design View...")
            menu.addSeparator()
            menu.addAction("Create View...")
            menu.addAction("Drop View...")
            
        elif item_type == "procedure":
            menu.addAction("Edit Procedure...", 
                         lambda: self.item_selected.emit("procedure", item.text()))
            menu.addSeparator()
            menu.addAction("Create Procedure...")
            menu.addAction("Drop Procedure...")
            
        if menu.actions():
            menu.exec(self.viewport().mapToGlobal(position))
