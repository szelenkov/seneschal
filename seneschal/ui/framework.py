"""
Tkinter-based UI framework for Seneschal Python port.
Provides base classes and utilities for building the application UI.
"""

import tkinter as tk
from tkinter import ttk
from abc import ABC, abstractmethod
from typing import Optional, Callable, Any, Dict
from dataclasses import dataclass
import ttkbootstrap as ttk_bootstrap
from ttkbootstrap.constants import *


@dataclass
class UITheme:
    """UI theme configuration"""
    name: str = "darkly"
    font_family: str = "Segoe UI"
    font_size: int = 10
    monospace_font: str = "Consolas"
    monospace_size: int = 10


class UIComponent(ABC):
    """Base class for UI components"""
    
    def __init__(self, parent=None, **kwargs):
        self.parent = parent
        self.widget = None
        self.callbacks = {}
    
    @abstractmethod
    def build(self) -> tk.Widget:
        """Build and return the widget"""
        pass
    
    def on(self, event: str, callback: Callable) -> None:
        """Register event callback"""
        self.callbacks[event] = callback
    
    def trigger(self, event: str, *args) -> None:
        """Trigger an event"""
        if event in self.callbacks:
            self.callbacks[event](*args)


class Button(UIComponent):
    """Button component"""
    
    def __init__(self, parent=None, text: str = "", command: Optional[Callable] = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.text = text
        self.command = command
    
    def build(self) -> tk.Button:
        self.widget = tk.Button(self.parent, text=self.text, command=self.command)
        return self.widget


class Entry(UIComponent):
    """Text entry component"""
    
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.show = kwargs.pop('show', '')
    
    def build(self) -> tk.Entry:
        self.widget = tk.Entry(self.parent, show=self.show)
        return self.widget
    
    def get_text(self) -> str:
        """Get entry text"""
        return self.widget.get() if self.widget else ""
    
    def set_text(self, text: str) -> None:
        """Set entry text"""
        if self.widget:
            self.widget.delete(0, tk.END)
            self.widget.insert(0, text)


class Label(UIComponent):
    """Label component"""
    
    def __init__(self, parent=None, text: str = "", **kwargs):
        super().__init__(parent, **kwargs)
        self.text = text
    
    def build(self) -> tk.Label:
        self.widget = tk.Label(self.parent, text=self.text)
        return self.widget


class Frame(UIComponent):
    """Frame component"""
    
    def build(self) -> tk.Frame:
        self.widget = tk.Frame(self.parent)
        return self.widget


class TreeView(UIComponent):
    """TreeView component (replaces VirtualTrees)"""
    
    def __init__(self, parent=None, columns: tuple = (), **kwargs):
        super().__init__(parent, **kwargs)
        self.columns = columns
        self.items: Dict[str, Any] = {}
    
    def build(self) -> ttk.Treeview:
        self.widget = ttk.Treeview(
            self.parent,
            columns=self.columns,
            height=15
        )
        self.widget.column("#0", width=200)
        self.widget.heading("#0", text="Name")
        for col in self.columns:
            self.widget.column(col, width=100)
            self.widget.heading(col, text=col)
        
        # Bind events
        self.widget.bind('<<TreeviewSelect>>', self._on_select)
        return self.widget
    
    def _on_select(self, event):
        """Handle selection"""
        self.trigger('select')
    
    def add_item(self, parent: str, item_id: str, text: str, values: tuple = ()) -> None:
        """Add item to tree"""
        self.widget.insert(parent or '', tk.END, item_id, text=text, values=values)
        self.items[item_id] = {'parent': parent, 'text': text, 'values': values}
    
    def get_selected(self) -> Optional[str]:
        """Get selected item ID"""
        selection = self.widget.selection()
        return selection[0] if selection else None
    
    def clear(self) -> None:
        """Clear tree"""
        for item in self.widget.get_children():
            self.widget.delete(item)
        self.items.clear()


class TextEditor(UIComponent):
    """Text editor component for SQL (replaces SynEdit)"""
    
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.syntax_highlight = kwargs.pop('syntax_highlight', False)
    
    def build(self) -> tk.Text:
        self.widget = tk.Text(
            self.parent,
            wrap=tk.WORD,
            height=10,
            width=60,
            font=("Consolas", 10)
        )
        return self.widget
    
    def get_text(self) -> str:
        """Get editor text"""
        return self.widget.get("1.0", tk.END) if self.widget else ""
    
    def set_text(self, text: str) -> None:
        """Set editor text"""
        if self.widget:
            self.widget.delete("1.0", tk.END)
            self.widget.insert("1.0", text)
    
    def clear(self) -> None:
        """Clear editor"""
        if self.widget:
            self.widget.delete("1.0", tk.END)


class DataGrid(UIComponent):
    """Data grid component (replaces TDBGrid)"""
    
    def __init__(self, parent=None, columns: list = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.columns = columns or []
        self.rows = []
    
    def build(self) -> ttk.Treeview:
        self.widget = ttk.Treeview(
            self.parent,
            columns=self.columns,
            height=15
        )
        
        # Configure columns
        self.widget.column("#0", width=0, stretch=False)
        for i, col in enumerate(self.columns):
            self.widget.column(col, anchor=tk.W, width=100)
            self.widget.heading(col, text=col, anchor=tk.W)
        
        return self.widget
    
    def add_row(self, values: list) -> None:
        """Add row to grid"""
        self.widget.insert('', tk.END, values=values)
        self.rows.append(values)
    
    def set_data(self, data: list) -> None:
        """Set grid data"""
        # Clear existing rows
        for item in self.widget.get_children():
            self.widget.delete(item)
        
        self.rows = data
        for row in data:
            self.widget.insert('', tk.END, values=row)
    
    def get_selected_row(self) -> Optional[list]:
        """Get selected row data"""
        selection = self.widget.selection()
        if selection:
            item_id = selection[0]
            return list(self.widget.item(item_id, 'values'))
        return None
    
    def clear(self) -> None:
        """Clear grid"""
        for item in self.widget.get_children():
            self.widget.delete(item)
        self.rows.clear()


class Dialog(tk.Toplevel, ABC):
    """Base class for modal dialogs"""
    
    def __init__(self, parent: tk.Tk, title: str = "", **kwargs):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.result = None
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
    
    @abstractmethod
    def build_ui(self) -> None:
        """Build dialog UI"""
        pass
    
    def show(self) -> Any:
        """Show dialog and wait for result"""
        self.build_ui()
        self.wait_window()
        return self.result
    
    def close(self, result=None) -> None:
        """Close dialog"""
        self.result = result
        self.destroy()


class MainWindow(ttk_bootstrap.Window):
    """Main application window"""
    
    def __init__(self, theme: UITheme = None, **kwargs):
        if theme is None:
            theme = UITheme()
        
        super().__init__(themename=theme.name if theme is UITheme else theme)
        self.theme = theme
        self.title("Seneschal - Python Edition")
        
        # Set window size
        self.geometry("1200x700")
        
        # Center window on screen
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def build_ui(self) -> None:
        """Build main window UI - override in subclass"""
        pass
    
    def run(self) -> None:
        """Run the application"""
        self.build_ui()
        self.mainloop()


class TabManager:
    """Manages tabbed interface"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.notebook = ttk.Notebook(parent)
        self.tabs: Dict[str, tk.Frame] = {}
    
    def add_tab(self, tab_id: str, tab_title: str) -> tk.Frame:
        """Add a new tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=tab_title)
        self.tabs[tab_id] = frame
        return frame
    
    def get_tab(self, tab_id: str) -> Optional[tk.Frame]:
        """Get tab by ID"""
        return self.tabs.get(tab_id)
    
    def remove_tab(self, tab_id: str) -> None:
        """Remove tab"""
        if tab_id in self.tabs:
            self.notebook.forget(self.tabs[tab_id])
            del self.tabs[tab_id]
    
    def pack(self, **kwargs) -> None:
        """Pack notebook"""
        self.notebook.pack(**kwargs)
    
    def grid(self, **kwargs) -> None:
        """Grid notebook"""
        self.notebook.grid(**kwargs)


class StatusBar:
    """Status bar at bottom of window"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.frame = ttk.Frame(parent, relief=tk.SUNKEN)
        self.label = ttk.Label(self.frame, text="Ready", anchor=tk.W)
        self.label.pack(fill=tk.BOTH, expand=True)
    
    def set_status(self, text: str) -> None:
        """Set status text"""
        self.label.config(text=text)
    
    def pack(self, **kwargs) -> None:
        """Pack status bar"""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs) -> None:
        """Grid status bar"""
        self.frame.grid(**kwargs)


class MenuBar:
    """Menu bar"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.menubar = tk.Menu(root)
        root.config(menu=self.menubar)
    
    def add_menu(self, label: str) -> tk.Menu:
        """Add menu"""
        menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=label, menu=menu)
        return menu
    
    def add_command(self, menu: tk.Menu, label: str, command: Callable) -> None:
        """Add menu command"""
        menu.add_command(label=label, command=command)
    
    def add_separator(self, menu: tk.Menu) -> None:
        """Add menu separator"""
        menu.add_separator()
    
    def add_submenu(self, menu: tk.Menu, label: str) -> tk.Menu:
        """Add submenu"""
        submenu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label=label, menu=submenu)
        return submenu

