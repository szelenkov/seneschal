from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QPlainTextEdit, QPushButton, QToolBar,
                           QSplitter, QTableView, QLabel)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor

from ..utils.settings_manager import SettingsManager
from ..utils.theme_manager import SQLHighlighter, ThemeManager

class QueryEditor(QWidget):
    query_executed = pyqtSignal(str)  # Signal emitted when query is executed

    def __init__(self, connection=None, parent=None):
        super().__init__(parent)
        self.connection = connection
        self.settings = SettingsManager()
        self.setup_ui()
        self.update_editor_settings()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar = QToolBar()
        
        self.execute_btn = QPushButton("Execute")
        self.execute_btn.clicked.connect(self.execute_query)
        toolbar.addWidget(self.execute_btn)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_editor)
        toolbar.addWidget(self.clear_btn)
        
        layout.addWidget(toolbar)
        
        # Main splitter
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Query editor
        self.editor = QPlainTextEdit()
        self.highlighter = SQLHighlighter(self.editor.document())
        splitter.addWidget(self.editor)
        
        # Results area
        self.results_widget = QWidget()
        results_layout = QVBoxLayout(self.results_widget)
        
        # Results table
        self.results_table = QTableView()
        results_layout.addWidget(self.results_table)
        
        # Status label
        self.status_label = QLabel()
        results_layout.addWidget(self.status_label)
        
        splitter.addWidget(self.results_widget)
        
        # Set initial sizes (60% editor, 40% results)
        splitter.setSizes([600, 400])
        
        layout.addWidget(splitter)

    def update_editor_settings(self):
        """Update editor settings based on preferences"""
        editor_settings = self.settings.get_editor_settings()
        
        # Set font
        font = QFont(editor_settings['font_family'], editor_settings['font_size'])
        self.editor.setFont(font)
        
        # Word wrap
        self.editor.setLineWrapMode(
            QPlainTextEdit.LineWrapMode.WidgetWidth if editor_settings['word_wrap']
            else QPlainTextEdit.LineWrapMode.NoWrap
        )
        
        # Tab settings
        if editor_settings['use_spaces']:
            self.editor.setTabStopDistance(
                editor_settings['tab_size'] * self.editor.fontMetrics().horizontalAdvance(' ')
            )
        
        # Line numbers and current line highlighting are handled by the custom editor
        
        # Update syntax highlighting
        self.highlighter.update_theme()
        
        # Apply editor style
        self.editor.setStyleSheet(ThemeManager.get_editor_style())

    def execute_query(self):
        """Execute the current query"""
        if not self.connection:
            self.status_label.setText("No database connection")
            return
            
        query = self.editor.textCursor().selectedText()
        if not query:
            query = self.editor.toPlainText()
            
        if not query.strip():
            return
            
        try:
            result = self.connection.execute_query(query)
            
            if result:
                # Update results table
                from PyQt6.QtGui import QStandardItemModel, QStandardItem
                
                model = QStandardItemModel()
                
                # Set headers
                headers = list(result.keys())
                model.setHorizontalHeaderLabels(headers)
                
                # Add data
                for row in result:
                    items = [QStandardItem(str(val) if val is not None 
                            else self.settings.get('data/null_display', 'NULL'))
                            for val in row]
                    model.appendRow(items)
                
                self.results_table.setModel(model)
                self.status_label.setText(f"Query executed successfully. {model.rowCount()} rows returned.")
            else:
                self.status_label.setText("Query executed successfully. No results returned.")
                
            self.query_executed.emit(query)
            
        except Exception as e:
            self.status_label.setText(f"Error executing query: {str(e)}")

    def clear_editor(self):
        """Clear the query editor"""
        self.editor.clear()
        self.status_label.clear()
        self.results_table.setModel(None)
