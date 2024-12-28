from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QTableView, QToolBar,
                           QMessageBox, QDialog, QFormLayout,
                           QLineEdit, QComboBox, QCheckBox)
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt, pyqtSignal

class ColumnEditorDialog(QDialog):
    def __init__(self, parent=None, column_data=None):
        super().__init__(parent)
        self.column_data = column_data or {}
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Column Editor")
        layout = QFormLayout(self)
        
        # Column name
        self.name_edit = QLineEdit(self.column_data.get('name', ''))
        layout.addRow("Name:", self.name_edit)
        
        # Data type
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            'INT', 'BIGINT', 'FLOAT', 'DOUBLE', 'DECIMAL',
            'CHAR', 'VARCHAR', 'TEXT', 'DATE', 'DATETIME',
            'TIMESTAMP', 'BOOLEAN', 'BLOB'
        ])
        if 'type' in self.column_data:
            self.type_combo.setCurrentText(self.column_data['type'])
        layout.addRow("Type:", self.type_combo)
        
        # Length/Values
        self.length_edit = QLineEdit(self.column_data.get('length', ''))
        layout.addRow("Length/Values:", self.length_edit)
        
        # Not null
        self.not_null = QCheckBox()
        self.not_null.setChecked(self.column_data.get('not_null', False))
        layout.addRow("Not Null:", self.not_null)
        
        # Default value
        self.default_edit = QLineEdit(self.column_data.get('default', ''))
        layout.addRow("Default:", self.default_edit)
        
        # Auto increment
        self.auto_increment = QCheckBox()
        self.auto_increment.setChecked(self.column_data.get('auto_increment', False))
        layout.addRow("Auto Increment:", self.auto_increment)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addRow("", button_layout)
        
    def get_column_data(self):
        return {
            'name': self.name_edit.text(),
            'type': self.type_combo.currentText(),
            'length': self.length_edit.text(),
            'not_null': self.not_null.isChecked(),
            'default': self.default_edit.text(),
            'auto_increment': self.auto_increment.isChecked()
        }

class StructureEditor(QWidget):
    structure_changed = pyqtSignal()
    
    def __init__(self, parent=None, connection=None, table_name=None):
        super().__init__(parent)
        self.connection = connection
        self.table_name = table_name
        self.setup_ui()
        if table_name:
            self.load_structure()
            
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar = QToolBar()
        
        self.add_column_btn = QPushButton("Add Column")
        self.add_column_btn.clicked.connect(self.add_column)
        toolbar.addWidget(self.add_column_btn)
        
        self.edit_column_btn = QPushButton("Edit Column")
        self.edit_column_btn.clicked.connect(self.edit_column)
        toolbar.addWidget(self.edit_column_btn)
        
        self.delete_column_btn = QPushButton("Delete Column")
        self.delete_column_btn.clicked.connect(self.delete_column)
        toolbar.addWidget(self.delete_column_btn)
        
        layout.addWidget(toolbar)
        
        # Structure view
        self.structure_view = QTableView()
        self.structure_model = QStandardItemModel()
        self.structure_model.setHorizontalHeaderLabels([
            "Name", "Type", "Length/Values", "Not Null", 
            "Default", "Auto Increment", "Comment"
        ])
        self.structure_view.setModel(self.structure_model)
        layout.addWidget(self.structure_view)
        
    def load_structure(self):
        if not self.connection or not self.table_name:
            return
            
        try:
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
            
            self.structure_model.setRowCount(0)
            for row in result:
                items = [
                    QStandardItem(str(row[0])),  # Name
                    QStandardItem(str(row[1])),  # Type
                    QStandardItem(str(row[2]) if row[2] else ''),  # Length
                    QStandardItem('NO' if row[3] == 'NO' else 'YES'),  # Nullable
                    QStandardItem(str(row[4]) if row[4] else ''),  # Default
                    QStandardItem('YES' if 'auto_increment' in str(row[5]).lower() else 'NO'),  # Auto Inc
                    QStandardItem(str(row[6]))  # Comment
                ]
                self.structure_model.appendRow(items)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load table structure: {str(e)}")
            
    def add_column(self):
        dialog = ColumnEditorDialog(self)
        if dialog.exec():
            column_data = dialog.get_column_data()
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
                self.structure_changed.emit()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add column: {str(e)}")
                
    def edit_column(self):
        current = self.structure_view.currentIndex()
        if not current.isValid():
            return
            
        row = current.row()
        column_data = {
            'name': self.structure_model.item(row, 0).text(),
            'type': self.structure_model.item(row, 1).text(),
            'length': self.structure_model.item(row, 2).text(),
            'not_null': self.structure_model.item(row, 3).text() == 'NO',
            'default': self.structure_model.item(row, 4).text(),
            'auto_increment': self.structure_model.item(row, 5).text() == 'YES'
        }
        
        dialog = ColumnEditorDialog(self, column_data)
        if dialog.exec():
            new_data = dialog.get_column_data()
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
                self.structure_changed.emit()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to modify column: {str(e)}")
                
    def delete_column(self):
        current = self.structure_view.currentIndex()
        if not current.isValid():
            return
            
        column_name = self.structure_model.item(current.row(), 0).text()
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete column '{column_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                query = f"ALTER TABLE {self.table_name} DROP COLUMN {column_name}"
                self.connection.execute_query(query)
                self.load_structure()
                self.structure_changed.emit()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete column: {str(e)}")
