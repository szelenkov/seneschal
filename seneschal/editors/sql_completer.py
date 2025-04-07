import tkinter as tk
import re

class SQLCompleter(tk.Listbox):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Configure listbox
        self.config(
            selectmode=tk.SINGLE,
            exportselection=False
        )
        
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
        
        # Populate initial keywords
        self.update_keywords()
        
        # Bind events
        self.bind('<KeyRelease>', self._on_key_release)
        
    def update_keywords(self, additional_words=None):
        """Update the listbox with keywords"""
        # Clear existing items
        self.delete(0, tk.END)
        
        # Combine base keywords with additional words
        words = self.keywords.copy()
        if additional_words:
            words.extend(additional_words)
        
        # Sort and insert words
        for word in sorted(set(words), key=str.lower):
            self.insert(tk.END, word)
        
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
                
            self.update_keywords(additional_words)
            
        except Exception:
            # If failed to get database objects, just use basic keywords
            self.update_keywords()
    
    def _on_key_release(self):
        """Handle key release event for filtering"""
        # Get current text from the associated text widget
        if hasattr(self, 'associated_text_widget'):
            text_widget = self.associated_text_widget
            current_text = text_widget.get('insert linestart', 'insert')
            
            # Extract the last word
            words = re.findall(r'\b\w+\b', current_text)
            last_word = words[-1] if words else ''
            
            # Filter keywords
            self.delete(0, tk.END)
            matching_keywords = [
                keyword for keyword in self.keywords 
                if keyword.lower().startswith(last_word.lower())
            ]
            
            for keyword in sorted(matching_keywords, key=str.lower):
                self.insert(tk.END, keyword)
    
    def bind_to_text_widget(self, text_widget):
        """Bind the completer to a text widget for auto-completion"""
        self.associated_text_widget = text_widget
        
        def on_text_change(event):
            self._on_key_release()
        
        text_widget.bind('<KeyRelease>', on_text_change)
        
        def on_listbox_select(event):
            if self.curselection():
                selected_keyword = self.get(self.curselection())
                current_pos = text_widget.index(tk.INSERT)
                
                # Replace the last word with the selected keyword
                text_widget.delete('insert linestart', current_pos)
                text_widget.insert(current_pos, selected_keyword)
        
        self.bind('<<ListboxSelect>>', on_listbox_select)
    
    def get_suggestions(self, partial_word):
        """Return a list of keyword suggestions for a partial word"""
        return [
            keyword for keyword in self.keywords 
            if keyword.lower().startswith(partial_word.lower())
        ]
