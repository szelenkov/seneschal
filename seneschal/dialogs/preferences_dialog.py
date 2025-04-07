import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkfont
import tkinter.messagebox as messagebox

from ..utils.settings_manager import SettingsManager
from ..utils.theme_manager import ThemeManager

class PreferencesDialog(tk.Toplevel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title("Preferences")
        self.geometry("600x500")
        
        self.settings = SettingsManager()
        self.theme_manager = ThemeManager()
        
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Tab widget
        self.tab_widget = ttk.Notebook(main_frame)
        self.tab_widget.pack(fill=tk.BOTH, expand=True, pady=10)

        # General Settings Tab
        general_tab = ttk.Frame(self.tab_widget)
        self.tab_widget.add(general_tab, text="General")

        # Interface Group
        interface_frame = ttk.LabelFrame(general_tab, text="Interface")
        interface_frame.pack(fill=tk.X, padx=10, pady=5)

        # Language Dropdown
        language_frame = ttk.Frame(interface_frame)
        language_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(language_frame, text="Language:").pack(side=tk.LEFT)
        self.language_combo = ttk.Combobox(
            language_frame, 
            values=["English", "German", "French", "Spanish"],
            state="readonly",
            width=20
        )
        self.language_combo.pack(side=tk.RIGHT)

        # Theme Dropdown
        theme_frame = ttk.Frame(interface_frame)
        theme_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(theme_frame, text="Theme:").pack(side=tk.LEFT)
        self.theme_combo = ttk.Combobox(
            theme_frame, 
            values=["Light", "Dark", "System"],
            state="readonly",
            width=20
        )
        self.theme_combo.pack(side=tk.RIGHT)

        # Logging Group
        logging_frame = ttk.LabelFrame(general_tab, text="Logging")
        logging_frame.pack(fill=tk.X, padx=10, pady=5)

        # Log Level Dropdown
        log_level_frame = ttk.Frame(logging_frame)
        log_level_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(log_level_frame, text="Log Level:").pack(side=tk.LEFT)
        self.log_level_combo = ttk.Combobox(
            log_level_frame, 
            values=["DEBUG", "INFO", "WARNING", "ERROR"],
            state="readonly",
            width=20
        )
        self.log_level_combo.pack(side=tk.RIGHT)

        # File Logging Checkbox
        self.file_logging = ttk.Checkbutton(logging_frame, text="Enable File Logging")
        self.file_logging.pack(anchor=tk.W, padx=5, pady=2)

        # Console Logging Checkbox
        self.console_logging = ttk.Checkbutton(logging_frame, text="Enable Console Logging")
        self.console_logging.pack(anchor=tk.W, padx=5, pady=2)

        # Editor Settings Tab
        editor_tab = ttk.Frame(self.tab_widget)
        self.tab_widget.add(editor_tab, text="Editor")

        # Font Settings Group
        font_frame = ttk.LabelFrame(editor_tab, text="Font Settings")
        font_frame.pack(fill=tk.X, padx=10, pady=5)

        # Font Selection
        font_selection_frame = ttk.Frame(font_frame)
        font_selection_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(font_selection_frame, text="Font:").pack(side=tk.LEFT)
        self.editor_font = ttk.Combobox(
            font_selection_frame, 
            values=list(tkfont.families()),
            state="readonly",
            width=20
        )
        self.editor_font.pack(side=tk.RIGHT)

        # Font Size
        font_size_frame = ttk.Frame(font_frame)
        font_size_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(font_size_frame, text="Size:").pack(side=tk.LEFT)
        self.font_size = ttk.Spinbox(
            font_size_frame, 
            from_=8, 
            to=72, 
            width=10
        )
        self.font_size.pack(side=tk.RIGHT)

        # Editor Behavior Group
        behavior_frame = ttk.LabelFrame(editor_tab, text="Editor Behavior")
        behavior_frame.pack(fill=tk.X, padx=10, pady=5)

        # Checkboxes for editor behavior
        behaviors = [
            ("Enable Auto-Complete", "auto_complete"),
            ("Word Wrap", "word_wrap"),
            ("Use Spaces for Tabs", "use_spaces"),
            ("Highlight Current Line", "highlight_line"),
            ("Show Line Numbers", "show_line_numbers")
        ]

        for label, attr_name in behaviors:
            checkbox = ttk.Checkbutton(behavior_frame, text=label)
            checkbox.pack(anchor=tk.W, padx=5, pady=2)
            setattr(self, attr_name, checkbox)

        # Tab Size
        tab_size_frame = ttk.Frame(behavior_frame)
        tab_size_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(tab_size_frame, text="Tab Size:").pack(side=tk.LEFT)
        self.tab_size = ttk.Spinbox(
            tab_size_frame, 
            from_=2, 
            to=8, 
            width=10
        )
        self.tab_size.pack(side=tk.RIGHT)

        # Data Settings Tab
        data_tab = ttk.Frame(self.tab_widget)
        self.tab_widget.add(data_tab, text="Data")

        # Query Results Group
        results_frame = ttk.LabelFrame(data_tab, text="Query Results")
        results_frame.pack(fill=tk.X, padx=10, pady=5)

        # Max Rows
        max_rows_frame = ttk.Frame(results_frame)
        max_rows_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(max_rows_frame, text="Max Rows:").pack(side=tk.LEFT)
        self.max_rows = ttk.Spinbox(
            max_rows_frame, 
            from_=100, 
            to=1000000, 
            width=10
        )
        self.max_rows.pack(side=tk.RIGHT)

        # NULL Display
        null_display_frame = ttk.Frame(results_frame)
        null_display_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(null_display_frame, text="NULL Display:").pack(side=tk.LEFT)
        self.null_display = ttk.Combobox(
            null_display_frame, 
            values=["NULL", "(null)", "empty"],
            state="readonly",
            width=20
        )
        self.null_display.pack(side=tk.RIGHT)

        # Auto Commit Checkbox
        self.auto_commit = ttk.Checkbutton(results_frame, text="Auto Commit")
        self.auto_commit.pack(anchor=tk.W, padx=5, pady=2)

        # Batch Size
        batch_size_frame = ttk.Frame(results_frame)
        batch_size_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(batch_size_frame, text="Batch Size:").pack(side=tk.LEFT)
        self.batch_size = ttk.Spinbox(
            batch_size_frame, 
            from_=100, 
            to=10000, 
            width=10
        )
        self.batch_size.pack(side=tk.RIGHT)

        # Connection Settings Group
        connection_frame = ttk.LabelFrame(data_tab, text="Connection")
        connection_frame.pack(fill=tk.X, padx=10, pady=5)

        # Connection History Size
        history_size_frame = ttk.Frame(connection_frame)
        history_size_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(history_size_frame, text="Connection History Size:").pack(side=tk.LEFT)
        self.history_size = ttk.Spinbox(
            history_size_frame, 
            from_=5, 
            to=50, 
            width=10
        )
        self.history_size.pack(side=tk.RIGHT)

        # Save Passwords Checkbox
        self.save_passwords = ttk.Checkbutton(connection_frame, text="Save Passwords")
        self.save_passwords.pack(anchor=tk.W, padx=5, pady=2)

        # Button Frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        # Save Button
        self.save_button = ttk.Button(
            button_frame, 
            text="Save", 
            command=self.save_settings
        )
        self.save_button.pack(side=tk.RIGHT, padx=5)

        # Reset Button
        self.reset_button = ttk.Button(
            button_frame, 
            text="Reset to Defaults", 
            command=self.reset_settings
        )
        self.reset_button.pack(side=tk.RIGHT, padx=5)

        # Cancel Button
        self.cancel_button = ttk.Button(
            button_frame, 
            text="Cancel", 
            command=self.destroy
        )
        self.cancel_button.pack(side=tk.RIGHT, padx=5)

        # Apply theme
        self.theme_manager.apply_theme(self)

    def load_settings(self):
        # General settings
        self.language_combo.set(
            self.settings.get('general/language', 'English')
        )
        self.theme_combo.set(
            self.settings.get('general/theme', 'Light')
        )

        # Logging settings
        logging_config = self.settings.get_logging_config()
        self.log_level_combo.set(logging_config['level'])
        
        # Set checkboxes based on logging config
        self.file_logging.state(['!alternate'] if logging_config['file_enabled'] else ['alternate'])
        self.console_logging.state(['!alternate'] if logging_config['console_enabled'] else ['alternate'])

        # Editor settings
        editor_config = self.settings.get_editor_config()
        self.editor_font.set(editor_config.get('font', 'Arial'))
        self.font_size.delete(0, tk.END)
        self.font_size.insert(0, str(editor_config.get('font_size', 12)))

        # Set editor behavior checkboxes
        behaviors = [
            ('auto_complete', 'auto_complete'),
            ('word_wrap', 'word_wrap'),
            ('use_spaces', 'use_spaces'),
            ('highlight_line', 'highlight_current_line'),
            ('show_line_numbers', 'show_line_numbers')
        ]
        for attr, config_key in behaviors:
            checkbox = getattr(self, attr)
            checkbox.state(['!alternate'] if editor_config.get(config_key, False) else ['alternate'])

        self.tab_size.delete(0, tk.END)
        self.tab_size.insert(0, str(editor_config.get('tab_size', 4)))

        # Data settings
        data_config = self.settings.get_data_config()
        self.max_rows.delete(0, tk.END)
        self.max_rows.insert(0, str(data_config.get('max_rows', 1000)))
        
        self.null_display.set(data_config.get('null_display', 'NULL'))
        
        self.auto_commit.state(['!alternate'] if data_config.get('auto_commit', False) else ['alternate'])
        
        self.batch_size.delete(0, tk.END)
        self.batch_size.insert(0, str(data_config.get('batch_size', 1000)))

        # Connection settings
        conn_config = self.settings.get_connection_config()
        self.history_size.delete(0, tk.END)
        self.history_size.insert(0, str(conn_config.get('history_size', 20)))
        
        self.save_passwords.state(['!alternate'] if conn_config.get('save_passwords', False) else ['alternate'])

    def save_settings(self):
        try:
            # General settings
            self.settings.set('general/language', self.language_combo.get())
            self.settings.set('general/theme', self.theme_combo.get())

            # Logging settings
            self.settings.set_logging_config({
                'level': self.log_level_combo.get(),
                'file_enabled': 'selected' in self.file_logging.state(),
                'console_enabled': 'selected' in self.console_logging.state()
            })

            # Editor settings
            self.settings.set_editor_config({
                'font': self.editor_font.get(),
                'font_size': int(self.font_size.get()),
                'auto_complete': 'selected' in self.auto_complete.state(),
                'word_wrap': 'selected' in self.word_wrap.state(),
                'use_spaces': 'selected' in self.use_spaces.state(),
                'highlight_current_line': 'selected' in self.highlight_line.state(),
                'show_line_numbers': 'selected' in self.show_line_numbers.state(),
                'tab_size': int(self.tab_size.get())
            })

            # Data settings
            self.settings.set_data_config({
                'max_rows': int(self.max_rows.get()),
                'null_display': self.null_display.get(),
                'auto_commit': 'selected' in self.auto_commit.state(),
                'batch_size': int(self.batch_size.get())
            })

            # Connection settings
            self.settings.set_connection_config({
                'history_size': int(self.history_size.get()),
                'save_passwords': 'selected' in self.save_passwords.state()
            })

            # Save all settings
            self.settings.save()

            messagebox.showinfo("Success", "Settings saved successfully!")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")

    def reset_settings(self):
        """Reset all settings to default values"""
        result = messagebox.askyesno("Reset Settings", 
                                     "Are you sure you want to reset all settings to defaults?")
        if result:
            # Reset settings to their default values
            self.settings.reset_to_defaults()
            
            # Reload settings
            self.load_settings()
            
            messagebox.showinfo("Reset Settings", "All settings have been reset to defaults.")

def show_preferences_dialog(parent=None):
    """Convenience function to show the preferences dialog"""
    dialog = PreferencesDialog(parent)
    dialog.grab_set()  # Make the dialog modal
    dialog.wait_window(dialog)
