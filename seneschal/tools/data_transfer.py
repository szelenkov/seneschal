from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QComboBox, QProgressBar,
                           QLabel, QFileDialog, QCheckBox, QSpinBox,
                           QMessageBox, QGroupBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import csv
import json
import sqlite3
from datetime import datetime

class DataTransferWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(self, connection, export_settings):
        super().__init__()
        self.connection = connection
        self.settings = export_settings
        
    def run(self):
        try:
            if self.settings['operation'] == 'export':
                self.export_data()
            else:
                self.import_data()
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()
            
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
                    writer.writerow(result.keys())
                
                # Write data
                for row in result:
                    writer.writerow(row)
                    processed_rows += 1
                    self.progress.emit(int(processed_rows * 100 / total_rows))
                    
        elif self.settings['format'] == 'json':
            data = []
            headers = result.keys()
            
            for row in result:
                row_dict = dict(zip(headers, row))
                data.append(row_dict)
                processed_rows += 1
                self.progress.emit(int(processed_rows * 100 / total_rows))
                
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
                headers = result.keys()
                for row in result:
                    values = []
                    for val in row:
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
                    self.progress.emit(int(processed_rows * 100 / total_rows))
                    
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
                    self.progress.emit(int(processed_rows * 100 / total_rows))

class DataTransferTool(QWidget):
    def __init__(self, parent=None, connection=None):
        super().__init__(parent)
        self.connection = connection
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Operation selection
        op_group = QGroupBox("Operation")
        op_layout = QHBoxLayout()
        self.operation = QComboBox()
        self.operation.addItems(["Export", "Import"])
        op_layout.addWidget(QLabel("Operation:"))
        op_layout.addWidget(self.operation)
        op_group.setLayout(op_layout)
        layout.addWidget(op_group)
        
        # Format selection
        format_group = QGroupBox("Format Settings")
        format_layout = QVBoxLayout()
        
        format_row = QHBoxLayout()
        self.format = QComboBox()
        self.format.addItems(["CSV", "JSON", "SQL"])
        format_row.addWidget(QLabel("Format:"))
        format_row.addWidget(self.format)
        format_layout.addLayout(format_row)
        
        self.include_headers = QCheckBox("Include Headers")
        self.include_headers.setChecked(True)
        format_layout.addWidget(self.include_headers)
        
        self.include_structure = QCheckBox("Include Table Structure (SQL only)")
        self.include_structure.setChecked(True)
        format_layout.addWidget(self.include_structure)
        
        format_group.setLayout(format_layout)
        layout.addWidget(format_group)
        
        # File selection
        file_group = QGroupBox("File Selection")
        file_layout = QHBoxLayout()
        self.filename = QLabel("No file selected")
        file_layout.addWidget(self.filename)
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_file)
        file_layout.addWidget(self.browse_button)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Progress
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout()
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_transfer)
        button_layout.addWidget(self.start_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_transfer)
        self.cancel_button.setEnabled(False)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
    def browse_file(self):
        if self.operation.currentText() == "Export":
            filename, _ = QFileDialog.getSaveFileName(
                self, "Save File",
                "",
                "CSV Files (*.csv);;JSON Files (*.json);;SQL Files (*.sql)"
            )
        else:
            filename, _ = QFileDialog.getOpenFileName(
                self, "Open File",
                "",
                "CSV Files (*.csv);;JSON Files (*.json);;SQL Files (*.sql)"
            )
            
        if filename:
            self.filename.setText(filename)
            
    def start_transfer(self):
        if not self.connection or not self.connection.connected:
            QMessageBox.critical(self, "Error", "No database connection!")
            return
            
        if self.filename.text() == "No file selected":
            QMessageBox.critical(self, "Error", "Please select a file!")
            return
            
        settings = {
            'operation': self.operation.currentText().lower(),
            'format': self.format.currentText().lower(),
            'filename': self.filename.text(),
            'include_headers': self.include_headers.isChecked(),
            'include_structure': self.include_structure.isChecked(),
            'table': 'your_table_name'  # This should be set based on selected table
        }
        
        self.worker = DataTransferWorker(self.connection, settings)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.transfer_finished)
        self.worker.error.connect(self.transfer_error)
        
        self.worker.start()
        self.start_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        
    def cancel_transfer(self):
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
            self.transfer_finished()
            
    def update_progress(self, value):
        self.progress_bar.setValue(value)
        
    def transfer_finished(self):
        self.start_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.progress_bar.setValue(0)
        QMessageBox.information(self, "Success", "Transfer completed successfully!")
        
    def transfer_error(self, error_message):
        QMessageBox.critical(self, "Error", f"Transfer failed: {error_message}")
        self.transfer_finished()
