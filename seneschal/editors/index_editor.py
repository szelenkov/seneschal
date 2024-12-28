from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QTableView, QToolBar,
                           QMessageBox, QDialog, QFormLayout,
                           QLineEdit, QComboBox, QListWidget)
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt, pyqtSignal

class IndexEditorDialog(QDialog):
    def __init__(self, parent=None, index_data=None, available_columns=None):
        super().__init__(parent)
        self.index_data = index_data or {}
        self.available_columns = available_columns or []
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Index Editor")
        self.setMinimumWidth(400)
        layout = QFormLayout(self)
        
        # Index name
        self.name_edit = QLineEdit(self.index_data.get('name', ''))
        layout.addRow("Name:", self.name_edit)
        
        # Index type
        self.type_combo = QComboBox()
        self.type_combo.addItems(['PRIMARY', 'UNIQUE', 'INDEX', 'FULLTEXT'])
        if 'type' in self.index_data:
            self.type_combo.setCurrentText(self.index_data['type'])
        layout.addRow("Type:", self.type_combo)
        
        # Columns
        self.columns_list = QListWidget()
        self.columns_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        for column in self.available_columns:
            self.columns_list.addItem(column)
            if column in self.index_data.get('columns', []):
                self.columns_list.item(self.columns_list.count() - 1).setSelected(True)
        layout.addRow("Columns:", self.columns_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addRow("", button_layout)
        
    def get_index_data(self):
        return {
            'name': self.name_edit.text(),
            'type': self.type_combo.currentText(),
            'columns': [item.text() for item in self.columns_list.selectedItems()]
        }

class IndexEditor(QWidget):
    index_changed = pyqtSignal()
    
    def __init__(self, parent=None, connection=None, table_name=None):
        super().__init__(parent)
        self.connection = connection
        self.table_name = table_name
        self.setup_ui()
        if table_name:
            self.load_indexes()
            
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar = QToolBar()
        
        self.add_index_btn = QPushButton("Add Index")
        self.add_index_btn.clicked.connect(self.add_index)
        toolbar.addWidget(self.add_index_btn)
        
        self.edit_index_btn = QPushButton("Edit Index")
        self.edit_index_btn.clicked.connect(self.edit_index)
        toolbar.addWidget(self.edit_index_btn)
        
        self.delete_index_btn = QPushButton("Delete Index")
        self.delete_index_btn.clicked.connect(self.delete_index)
        toolbar.addWidget(self.delete_index_btn)
        
        layout.addWidget(toolbar)
        
        # Index view
        self.index_view = QTableView()
        self.index_model = QStandardItemModel()
        self.index_model.setHorizontalHeaderLabels([
            "Name", "Type", "Columns", "Comment"
        ])
        self.index_view.setModel(self.index_model)
        layout.addWidget(self.index_view)
        
    def get_available_columns(self):
        try:
            query = f"""
                SELECT COLUMN_NAME
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = '{self.table_name}'
                ORDER BY ORDINAL_POSITION
            """
            result = self.connection.execute_query(query)
            return [row[0] for row in result]
        except Exception:
            return []
            
    def load_indexes(self):
        if not self.connection or not self.table_name:
            return
            
        try:
            # Get index information
            query = f"SHOW INDEX FROM {self.table_name}"
            result = self.connection.execute_query(query)
            
            # Process results
            indexes = {}
            for row in result:
                index_name = row[2]  # Key_name
                if index_name not in indexes:
                    indexes[index_name] = {
                        'name': index_name,
                        'type': 'PRIMARY' if index_name == 'PRIMARY' else 
                               'UNIQUE' if not row[1] else 'INDEX',  # Non_unique
                        'columns': [],
                        'comment': ''
                    }
                indexes[index_name]['columns'].append(row[4])  # Column_name
                
            # Update model
            self.index_model.setRowCount(0)
            for index in indexes.values():
                items = [
                    QStandardItem(index['name']),
                    QStandardItem(index['type']),
                    QStandardItem(', '.join(index['columns'])),
                    QStandardItem(index['comment'])
                ]
                self.index_model.appendRow(items)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load indexes: {str(e)}")
            
    def add_index(self):
        available_columns = self.get_available_columns()
        dialog = IndexEditorDialog(self, available_columns=available_columns)
        if dialog.exec():
            index_data = dialog.get_index_data()
            try:
                # Generate CREATE INDEX statement
                if index_data['type'] == 'PRIMARY':
                    query = f"""
                        ALTER TABLE {self.table_name}
                        ADD PRIMARY KEY ({', '.join(index_data['columns'])})
                    """
                else:
                    index_type = 'UNIQUE ' if index_data['type'] == 'UNIQUE' else ''
                    query = f"""
                        CREATE {index_type}INDEX {index_data['name']}
                        ON {self.table_name} ({', '.join(index_data['columns'])})
                    """
                
                self.connection.execute_query(query)
                self.load_indexes()
                self.index_changed.emit()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create index: {str(e)}")
                
    def edit_index(self):
        current = self.index_view.currentIndex()
        if not current.isValid():
            return
            
        row = current.row()
        index_data = {
            'name': self.index_model.item(row, 0).text(),
            'type': self.index_model.item(row, 1).text(),
            'columns': [col.strip() for col in 
                       self.index_model.item(row, 2).text().split(',')]
        }
        
        available_columns = self.get_available_columns()
        dialog = IndexEditorDialog(self, index_data, available_columns)
        if dialog.exec():
            new_data = dialog.get_index_data()
            try:
                # Drop old index
                if index_data['type'] == 'PRIMARY':
                    drop_query = f"ALTER TABLE {self.table_name} DROP PRIMARY KEY"
                else:
                    drop_query = f"DROP INDEX {index_data['name']} ON {self.table_name}"
                    
                # Create new index
                if new_data['type'] == 'PRIMARY':
                    create_query = f"""
                        ALTER TABLE {self.table_name}
                        ADD PRIMARY KEY ({', '.join(new_data['columns'])})
                    """
                else:
                    index_type = 'UNIQUE ' if new_data['type'] == 'UNIQUE' else ''
                    create_query = f"""
                        CREATE {index_type}INDEX {new_data['name']}
                        ON {self.table_name} ({', '.join(new_data['columns'])})
                    """
                
                self.connection.execute_query(drop_query)
                self.connection.execute_query(create_query)
                self.load_indexes()
                self.index_changed.emit()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to modify index: {str(e)}")
                
    def delete_index(self):
        current = self.index_view.currentIndex()
        if not current.isValid():
            return
            
        index_name = self.index_model.item(current.row(), 0).text()
        index_type = self.index_model.item(current.row(), 1).text()
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete index '{index_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if index_type == 'PRIMARY':
                    query = f"ALTER TABLE {self.table_name} DROP PRIMARY KEY"
                else:
                    query = f"DROP INDEX {index_name} ON {self.table_name}"
                    
                self.connection.execute_query(query)
                self.load_indexes()
                self.index_changed.emit()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete index: {str(e)}")
