from PyQt6.QtWidgets import QCompleter
from PyQt6.QtCore import Qt, QStringListModel

class SQLCompleter(QCompleter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setModelSorting(QCompleter.ModelSorting.CaseInsensitivelySortedModel)
        self.setWrapAround(False)
        
        # Initialize with basic SQL keywords
        self.keywords = [
            # SQL Keywords
            'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE',
            'CREATE', 'ALTER', 'DROP', 'TABLE', 'DATABASE', 'INTO',
            'VALUES', 'AND', 'OR', 'NOT', 'NULL', 'JOIN', 'LEFT',
            'RIGHT', 'INNER', 'GROUP BY', 'ORDER BY', 'HAVING',
            'LIMIT', 'OFFSET', 'AS', 'ON', 'DISTINCT', 'COUNT',
            'SUM', 'AVG', 'MAX', 'MIN', 'BETWEEN', 'LIKE', 'IN',
            'EXISTS', 'UNION', 'INTERSECT', 'EXCEPT',
            
            # Data Types
            'INT', 'INTEGER', 'BIGINT', 'SMALLINT', 'TINYINT',
            'DECIMAL', 'NUMERIC', 'FLOAT', 'DOUBLE', 'REAL',
            'CHAR', 'VARCHAR', 'TEXT', 'BLOB', 'BINARY',
            'DATE', 'TIME', 'DATETIME', 'TIMESTAMP', 'YEAR',
            'BOOLEAN', 'BOOL',
            
            # Constraints
            'PRIMARY KEY', 'FOREIGN KEY', 'UNIQUE', 'CHECK',
            'DEFAULT', 'AUTO_INCREMENT', 'INDEX', 'REFERENCES'
        ]
        
        self.update_model()
        
    def update_model(self, additional_words=None):
        """Update the completer model with additional words"""
        words = self.keywords.copy()
        if additional_words:
            words.extend(additional_words)
        model = QStringListModel(words)
        self.setModel(model)
        
    def update_database_objects(self, connection):
        """Update completer with database objects"""
        if not connection or not connection.connected:
            return
            
        try:
            # Get database objects
            tables = connection.execute_query("SHOW TABLES")
            columns = connection.execute_query(
                "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS"
            )
            
            # Add database objects to keywords
            additional_words = []
            for table in tables:
                additional_words.append(table[0])
            for column in columns:
                additional_words.append(column[0])
                
            self.update_model(additional_words)
            
        except Exception:
            # If failed to get database objects, just use basic keywords
            self.update_model()
