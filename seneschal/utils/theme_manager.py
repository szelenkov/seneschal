import tkinter.ttk as ttk
import tkinter.font as tkfont
import threading

from .settings_manager import SettingsManager

class ThemeManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with ThemeManager._lock:
                if not cls._instance:
                    cls._instance = super(ThemeManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.settings = SettingsManager()
        self.current_theme = self.settings.get('general/theme', 'Light')
        self.theme_colors = self.settings.get_theme_colors()

    @staticmethod
    def apply_theme(root=None):
        """
        Apply theme to the entire application
        
        :param root: Main Tkinter root or Toplevel window
        """
        # Configure global style
        style = ttk.Style()
        this = ThemeManager()
        # Define theme colors
        bg = this.theme_colors['background']
        fg = this.theme_colors['foreground']
        selection = this.theme_colors['selection']
        current_line = this.theme_colors['current_line']
        
        # Configure global style for different widget types
        style.configure('TFrame', background=bg)
        style.configure('TLabel', background=bg, foreground=fg)
        style.configure('TButton', background=bg, foreground=fg)
        style.configure('TEntry', background=bg, foreground=fg, fieldbackground=bg)
        style.configure('TCombobox', background=bg, foreground=fg)
        style.configure('Treeview', background=bg, foreground=fg, fieldbackground=bg)
        style.configure('Treeview.Heading', background=current_line, foreground=fg)
        
        # Scrollbar theme
        style.configure('TScrollbar', background=bg)
        
        # Menu theme
        style.configure('TMenubutton', background=bg, foreground=fg)
        
        # Notebook (Tabs) theme
        style.configure('TNotebook', background=bg)
        style.configure('TNotebook.Tab', background=current_line, foreground=fg)
        style.map('TNotebook.Tab', 
            background=[('selected', selection)],
            foreground=[('selected', fg)]
        )
        
        # If a root window is provided, configure its colors
        if root:
            root.configure(
                bg=bg,
                highlightbackground=bg,
                highlightcolor=fg
            )
        
        # Optional: Configure default font
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(
            family=this.settings.get('editor/font_family', 'Consolas'),
            size=this.settings.get('editor/font_size', 10)
        )

    def get_syntax_colors(self):
        """
        Get syntax highlighting colors for code editors
        
        :return: Dictionary of syntax highlighting colors
        """
        return {
            'keyword': self.theme_colors['keyword'],
            'string': self.theme_colors['string'],
            'number': self.theme_colors['number'],
            'comment': self.theme_colors['comment']
        }

    def add_theme_listener(self):
        """
        Add a listener to detect theme changes
        """
        def on_theme_change(section, key, value):
            if section == 'general' and key == 'theme':
                self.current_theme = value
                self.theme_colors = self.settings.get_theme_colors()
                # Optionally, trigger a full theme reapplication
                self.apply_theme()
        
        self.settings.add_change_listener(on_theme_change)

    def toggle_theme(self):
        """
        Toggle between light and dark themes
        """
        new_theme = 'Dark' if self.current_theme == 'Light' else 'Light'
        self.settings.set('general/theme', new_theme)
