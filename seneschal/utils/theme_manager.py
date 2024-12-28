from PyQt6.QtGui import QPalette, QColor, QSyntaxHighlighter, QTextCharFormat
from PyQt6.QtCore import Qt

from .settings_manager import SettingsManager

class SQLHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_colors = {}
        self.update_theme()

    def update_theme(self):
        settings = SettingsManager()
        self.theme_colors = settings.get_theme_colors()
        
        # Keywords
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(self.theme_colors['keyword'])
        self.keyword_format.setFontWeight(700)  # Bold
        
        # String literals
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(self.theme_colors['string'])
        
        # Number literals
        self.number_format = QTextCharFormat()
        self.number_format.setForeground(self.theme_colors['number'])
        
        # Comments
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(self.theme_colors['comment'])
        self.comment_format.setFontItalic(True)
        
        # SQL Keywords
        self.keywords = [
            'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE',
            'CREATE', 'ALTER', 'DROP', 'TABLE', 'INDEX', 'VIEW',
            'GROUP BY', 'ORDER BY', 'HAVING', 'JOIN', 'LEFT', 'RIGHT',
            'INNER', 'OUTER', 'ON', 'AS', 'AND', 'OR', 'NOT', 'IN',
            'LIKE', 'BETWEEN', 'IS', 'NULL', 'ASC', 'DESC', 'DISTINCT',
            'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'UNION', 'ALL',
            'LIMIT', 'OFFSET', 'TOP', 'CONSTRAINT', 'PRIMARY KEY',
            'FOREIGN KEY', 'REFERENCES', 'CASCADE', 'SET NULL',
            'DEFAULT', 'AUTO_INCREMENT', 'UNIQUE', 'CHECK'
        ]

    def highlightBlock(self, text):
        # Keywords
        for keyword in self.keywords:
            index = text.upper().find(keyword)
            while index >= 0:
                length = len(keyword)
                # Check if it's a whole word
                if (index == 0 or not text[index-1].isalnum()) and \
                   (index + length >= len(text) or not text[index + length].isalnum()):
                    self.setFormat(index, length, self.keyword_format)
                index = text.upper().find(keyword, index + length)

        # Strings (single quotes)
        in_string = False
        start_pos = 0
        for i, char in enumerate(text):
            if char == "'":
                if not in_string:
                    start_pos = i
                    in_string = True
                else:
                    length = i - start_pos + 1
                    self.setFormat(start_pos, length, self.string_format)
                    in_string = False

        # Numbers
        import re
        for match in re.finditer(r'\b\d+(\.\d+)?\b', text):
            self.setFormat(match.start(), match.end() - match.start(), 
                         self.number_format)

        # Single-line comments
        if '--' in text:
            comment_pos = text.find('--')
            self.setFormat(comment_pos, len(text) - comment_pos, 
                         self.comment_format)

        # Multi-line comments
        start_pos = text.find('/*')
        if start_pos >= 0:
            end_pos = text.find('*/', start_pos)
            if end_pos >= 0:
                self.setFormat(start_pos, end_pos - start_pos + 2, 
                             self.comment_format)
            else:
                self.setFormat(start_pos, len(text) - start_pos, 
                             self.comment_format)

class ThemeManager:
    @staticmethod
    def apply_theme(app):
        settings = SettingsManager()
        theme_colors = settings.get_theme_colors()
        
        palette = QPalette()
        
        # Set the color scheme
        palette.setColor(QPalette.ColorRole.Window, 
                        theme_colors['background'])
        palette.setColor(QPalette.ColorRole.WindowText, 
                        theme_colors['foreground'])
        palette.setColor(QPalette.ColorRole.Base, 
                        theme_colors['background'])
        palette.setColor(QPalette.ColorRole.AlternateBase,
                        theme_colors['background'].lighter(110))
        palette.setColor(QPalette.ColorRole.Text, 
                        theme_colors['foreground'])
        palette.setColor(QPalette.ColorRole.Button, 
                        theme_colors['background'])
        palette.setColor(QPalette.ColorRole.ButtonText, 
                        theme_colors['foreground'])
        palette.setColor(QPalette.ColorRole.Highlight, 
                        theme_colors['selection'])
        palette.setColor(QPalette.ColorRole.HighlightedText,
                        theme_colors['foreground'])
        palette.setColor(QPalette.ColorRole.Link, 
                        QColor('#0000ff') if settings.get('general/theme') == 'Light'
                        else QColor('#1a8cff'))
        
        # Apply the palette
        app.setPalette(palette)
        
        # Set stylesheet for custom widgets
        app.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid %s;
            }
            QTabBar::tab {
                background: %s;
                color: %s;
                padding: 5px;
                border: 1px solid %s;
            }
            QTabBar::tab:selected {
                background: %s;
                border-bottom: none;
            }
            QTreeView {
                background-color: %s;
                color: %s;
            }
            QTreeView::item:selected {
                background-color: %s;
            }
            QTableView {
                gridline-color: %s;
            }
            QHeaderView::section {
                background-color: %s;
                color: %s;
                padding: 4px;
                border: 1px solid %s;
            }
            QToolBar {
                border: none;
                background: %s;
            }
            QStatusBar {
                background: %s;
                color: %s;
            }
            QLineEdit, QSpinBox, QComboBox {
                background: %s;
                color: %s;
                border: 1px solid %s;
                padding: 2px;
            }
            QPushButton {
                background: %s;
                color: %s;
                border: 1px solid %s;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background: %s;
            }
            QMenu {
                background-color: %s;
                color: %s;
            }
            QMenu::item:selected {
                background-color: %s;
            }
        """ % (
            theme_colors['foreground'].name(),
            theme_colors['background'].name(),
            theme_colors['foreground'].name(),
            theme_colors['foreground'].name(),
            theme_colors['background'].lighter(110).name(),
            theme_colors['background'].name(),
            theme_colors['foreground'].name(),
            theme_colors['selection'].name(),
            theme_colors['foreground'].darker(140).name(),
            theme_colors['background'].darker(110).name(),
            theme_colors['foreground'].name(),
            theme_colors['foreground'].name(),
            theme_colors['background'].name(),
            theme_colors['background'].name(),
            theme_colors['foreground'].name(),
            theme_colors['background'].name(),
            theme_colors['foreground'].name(),
            theme_colors['foreground'].name(),
            theme_colors['background'].name(),
            theme_colors['foreground'].name(),
            theme_colors['foreground'].name(),
            theme_colors['background'].lighter(110).name(),
            theme_colors['background'].name(),
            theme_colors['foreground'].name(),
            theme_colors['selection'].name()
        ))

    @staticmethod
    def get_editor_style():
        settings = SettingsManager()
        theme_colors = settings.get_theme_colors()
        
        return f"""
            QPlainTextEdit {{
                background-color: {theme_colors['background'].name()};
                color: {theme_colors['foreground'].name()};
                selection-background-color: {theme_colors['selection'].name()};
                selection-color: {theme_colors['foreground'].name()};
            }}
            QLineNumber {{
                background-color: {theme_colors['background'].darker(105).name()};
                color: {theme_colors['line_number'].name()};
                border-right: 1px solid {theme_colors['foreground'].name()};
                padding: 0 5px;
            }}
        """
