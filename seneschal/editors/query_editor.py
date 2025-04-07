import tkinter as tk
import tkinter.font as tkfont
import tkinter.scrolledtext as scrolledtext
import tkinter.ttk as ttk

from ..utils.settings_manager import SettingsManager
from ..utils.theme_manager import ThemeManager


class QueryEditor(tk.Frame):
    def __init__(self, connection=None, parent=None):
        super().__init__(parent)
        self.connection = connection
        self.settings = SettingsManager()
        self.theme_manager = ThemeManager()
        self.setup_ui()
        self.update_editor_settings()

    def setup_ui(self):
        # Main layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Toolbar
        toolbar = ttk.Frame(self)
        toolbar.grid(row=0, column=0, sticky='ew', padx=5, pady=5)

        # Execute button
        self.execute_btn = ttk.Button(toolbar, text="Execute", command=self.execute_query)
        self.execute_btn.pack(side=tk.LEFT, padx=5)

        # Clear button
        self.clear_btn = ttk.Button(toolbar, text="Clear", command=self.clear_editor)
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        # Query editor (with scrollbars)
        editor_frame = ttk.Frame(self)
        editor_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        editor_frame.grid_columnconfigure(0, weight=1)
        editor_frame.grid_rowconfigure(0, weight=1)

        self.editor = scrolledtext.ScrolledText(
            editor_frame, 
            wrap=tk.WORD, 
            height=10, 
            width=80
        )
        self.editor.grid(row=0, column=0, sticky='nsew')

        # Results area
        results_frame = ttk.Frame(self)
        results_frame.grid(row=2, column=0, sticky='nsew', padx=5, pady=5)
        results_frame.grid_columnconfigure(0, weight=1)

        # Results treeview
        self.results_table = ttk.Treeview(results_frame)
        self.results_table.grid(row=0, column=0, sticky='nsew')

        # Scrollbar for results
        results_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_table.yview)
        results_scrollbar.grid(row=0, column=1, sticky='ns')
        self.results_table.configure(yscrollcommand=results_scrollbar.set)

        # Status label
        self.status_label = ttk.Label(results_frame, text="")
        self.status_label.grid(row=1, column=0, sticky='w', padx=5, pady=5)

    def update_editor_settings(self):
        """Update editor settings based on preferences"""
        editor_settings = self.settings.get_editor_settings()
        
        # Set font
        font = tkfont.Font(
            family=editor_settings['font_family'], 
            size=editor_settings['font_size']
        )
        self.editor.configure(font=font)
        
        # Word wrap
        self.editor.configure(
            wrap='word' if editor_settings['word_wrap'] else 'none'
        )
        
        # Tab settings
        tab_size = editor_settings['tab_size']
        if editor_settings['use_spaces']:
            self.editor.configure(tabs=f'{tab_size}c')

        # Apply theme
        theme_colors = self.theme_manager.get_syntax_colors()
        self.editor.configure(
            background=self.theme_manager.theme_colors['background'],
            foreground=self.theme_manager.theme_colors['foreground']
        )

    def execute_query(self):
        """Execute the current query"""
        if not self.connection:
            self.status_label.configure(text="No database connection")
            return
            
        query = self.editor.get("1.0", tk.END).strip()
        if not query:
            return
            
        try:
            result = self.connection.execute_query(query)
            
            # Clear previous results
            for i in self.results_table.get_children():
                self.results_table.delete(i)
            
            if result:
                # Set headers
                headers = list(result[0].keys()) if result else []
                self.results_table['columns'] = headers
                
                # Configure column headings
                for header in headers:
                    self.results_table.heading(header, text=header)
                    self.results_table.column(header, anchor='w')
                
                # Add data
                for row in result:
                    values = [str(row.get(header, '')) for header in headers]
                    self.results_table.insert('', 'end', values=values)
                
                self.status_label.configure(
                    text=f"Query executed successfully. {len(result)} rows returned."
                )
            else:
                self.status_label.configure(
                    text="Query executed successfully. No results returned."
                )
                
        except Exception as e:
            self.status_label.configure(text=f"Error executing query: {str(e)}")

    def clear_editor(self):
        """Clear the query editor"""
        self.editor.delete("1.0", tk.END)
        self.status_label.configure(text="")
        
        # Clear results table
        for i in self.results_table.get_children():
            self.results_table.delete(i)
