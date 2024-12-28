from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, 
                           QTableView, QPushButton, QToolBar, 
                           QMessageBox, QInputDialog)
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt, pyqtSignal

from .structure_editor import StructureEditor
from .index_editor import IndexEditor

class TableEditor(QWidget):
    data_changed = pyqtSignal()

    def __init__(self, parent=None, connection=None, table_name=None):
        super().__init__(parent)
        self.connection = connection
        self.table_name = table_name
        self.setup_ui()
        if table_name:
            self.load_table_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Data tab
        self.data_tab = QWidget()
        data_layout = QVBoxLayout(self.data_tab)
        
        # Toolbar for data operations
        toolbar = QToolBar()
        self.add_row_btn = QPushButton("Add Row")
        self.add_row_btn.clicked.connect(self.add_row)
        toolbar.addWidget(self.add_row_btn)
        
        self.delete_row_btn = QPushButton("Delete Row")
        self.delete_row_btn.clicked.connect(self.delete_row)
        toolbar.addWidget(self.delete_row_btn)
        
        self.save_changes_btn = QPushButton("Save Changes")
        self.save_changes_btn.clicked.connect(self.save_changes)
        toolbar.addWidget(self.save_changes_btn)
        
        data_layout.addWidget(toolbar)
        
        # Table view
        self.table_view = QTableView()
        self.table_model = QStandardItemModel()
        self.table_view.setModel(self.table_model)
        data_layout.addWidget(self.table_view)
        
        # Structure tab
        self.structure_editor = StructureEditor(
            connection=self.connection,
            table_name=self.table_name
        )
        self.structure_editor.structure_changed.connect(self.on_structure_changed)
        
        # Indexes tab
        self.index_editor = IndexEditor(
            connection=self.connection,
            table_name=self.table_name
        )
        self.index_editor.index_changed.connect(self.on_structure_changed)
        
        # Add tabs
        self.tab_widget.addTab(self.data_tab, "Data")
        self.tab_widget.addTab(self.structure_editor, "Structure")
        self.tab_widget.addTab(self.index_editor, "Indexes")
        
        layout.addWidget(self.tab_widget)

    def load_table_data(self):
        if not self.connection or not self.table_name:
            return
            
        try:
            # Load table data
            query = f"SELECT * FROM {self.table_name}"
            result = self.connection.execute_query(query)
            
            # Clear and set headers
            self.table_model.clear()
            if result.keys():
                headers = list(result.keys())
                self.table_model.setHorizontalHeaderLabels(headers)
                
                # Add data
                for row in result:
                    items = [QStandardItem(str(val) if val is not None else '') 
                            for val in row]
                    self.table_model.appendRow(items)
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load table data: {str(e)}")
            
    def add_row(self):
        try:
            # Get column names
            columns = [self.table_model.headerData(i, Qt.Orientation.Horizontal) 
                      for i in range(self.table_model.columnCount())]
            
            # Create empty row
            values = ['NULL'] * len(columns)
            
            # Insert row
            query = f"""
                INSERT INTO {self.table_name}
                ({', '.join(columns)})
                VALUES ({', '.join(values)})
            """
            self.connection.execute_query(query)
            
            # Refresh data
            self.load_table_data()
            self.data_changed.emit()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add row: {str(e)}")
            
    def delete_row(self):
        selected = self.table_view.selectedIndexes()
        if not selected:
            return
            
        row = selected[0].row()
        try:
            # Get primary key or unique identifier
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
                pk_value = self.table_model.data(
                    self.table_model.index(row, 
                        list(self.table_model.headerData(i, Qt.Orientation.Horizontal) 
                             for i in range(self.table_model.columnCount())
                        ).index(pk_column)
                    )
                )
                
                # Delete row
                query = f"""
                    DELETE FROM {self.table_name}
                    WHERE {pk_column} = '{pk_value}'
                """
                self.connection.execute_query(query)
                
                # Refresh data
                self.load_table_data()
                self.data_changed.emit()
            else:
                QMessageBox.warning(
                    self,
                    "Warning",
                    "Cannot delete row: No primary key found in table"
                )
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete row: {str(e)}")
            
    def save_changes(self):
        try:
            # Get column names
            columns = [self.table_model.headerData(i, Qt.Orientation.Horizontal) 
                      for i in range(self.table_model.columnCount())]
            
            # Get primary key
            pk_query = f"""
                SELECT k.COLUMN_NAME
                FROM information_schema.table_constraints t
                JOIN information_schema.key_column_usage k
                USING(constraint_name,table_schema,table_name)
                WHERE t.constraint_type='PRIMARY KEY'
                AND t.table_name='{self.table_name}'
            """
            pk_result = self.connection.execute_query(pk_query)
            
            if not pk_result:
                QMessageBox.warning(
                    self,
                    "Warning",
                    "Cannot save changes: No primary key found in table"
                )
                return
                
            pk_column = pk_result[0][0]
            pk_index = columns.index(pk_column)
            
            # Update each row
            for row in range(self.table_model.rowCount()):
                updates = []
                for col in range(self.table_model.columnCount()):
                    value = self.table_model.data(self.table_model.index(row, col))
                    if value is None or value == '':
                        updates.append(f"{columns[col]} = NULL")
                    else:
                        updates.append(f"{columns[col]} = '{value}'")
                        
                pk_value = self.table_model.data(
                    self.table_model.index(row, pk_index)
                )
                
                query = f"""
                    UPDATE {self.table_name}
                    SET {', '.join(updates)}
                    WHERE {pk_column} = '{pk_value}'
                """
                self.connection.execute_query(query)
                
            self.data_changed.emit()
            QMessageBox.information(self, "Success", "Changes saved successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save changes: {str(e)}")
            
    def on_structure_changed(self):
        """Called when table structure or indexes change"""
        self.load_table_data()
