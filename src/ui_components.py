"""
UI Components Module
Modern Tkinter UI components with dark theme
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable

class ModernUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.setup_styles()
        
    def setup_styles(self):
        """Setup modern dark theme styles"""
        style = ttk.Style()
        
        # Configure dark theme
        style.theme_use('clam')
        
        # Define colors
        self.colors = {
            'bg_primary': '#2b2b2b',
            'bg_secondary': '#3c3c3c',
            'bg_tertiary': '#4d4d4d',
            'fg_primary': '#ffffff',
            'fg_secondary': '#cccccc',
            'accent': '#4CAF50',
            'accent_hover': '#45a049',
            'warning': '#ff9800',
            'error': '#f44336',
            'info': '#2196f3'
        }
        
        # Configure ttk styles
        style.configure('Modern.TFrame', 
                       background=self.colors['bg_secondary'],
                       relief='flat',
                       borderwidth=1)
        
        style.configure('Modern.TLabel',
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['fg_primary'],
                       font=('Arial', 10))
        
        style.configure('Modern.TButton',
                       background=self.colors['accent'],
                       foreground='white',
                       font=('Arial', 10, 'bold'),
                       relief='flat',
                       borderwidth=0,
                       padding=(10, 5))
        
        style.map('Modern.TButton',
                 background=[('active', self.colors['accent_hover']),
                           ('pressed', self.colors['accent'])])
        
        style.configure('Modern.Horizontal.TProgressbar',
                       background=self.colors['accent'],
                       troughcolor=self.colors['bg_tertiary'],
                       borderwidth=0,
                       lightcolor=self.colors['accent'],
                       darkcolor=self.colors['accent'])
        
        style.configure('Modern.Treeview',
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['fg_primary'],
                       fieldbackground=self.colors['bg_secondary'],
                       borderwidth=0,
                       font=('Arial', 9))
        
        style.configure('Modern.Treeview.Heading',
                       background=self.colors['bg_tertiary'],
                       foreground=self.colors['fg_primary'],
                       font=('Arial', 10, 'bold'),
                       relief='flat')
        
        style.map('Modern.Treeview',
                 background=[('selected', self.colors['accent'])],
                 foreground=[('selected', 'white')])
        
    def create_frame(self, parent: tk.Widget, **kwargs) -> tk.Frame:
        """Create a modern styled frame"""
        default_kwargs = {
            'bg': self.colors['bg_secondary'],
            'relief': 'flat',
            'bd': 1
        }
        default_kwargs.update(kwargs)
        
        frame = tk.Frame(parent, **default_kwargs)
        return frame
        
    def create_label(self, parent: tk.Widget, text: str, **kwargs) -> tk.Label:
        """Create a modern styled label"""
        default_kwargs = {
            'bg': self.colors['bg_secondary'],
            'fg': self.colors['fg_primary'],
            'font': ('Arial', 10)
        }
        default_kwargs.update(kwargs)
        
        label = tk.Label(parent, text=text, **default_kwargs)
        return label
        
    def create_button(self, parent: tk.Widget, text: str, command: Optional[Callable] = None, **kwargs) -> tk.Button:
        """Create a modern styled button"""
        default_kwargs = {
            'bg': self.colors['accent'],
            'fg': 'white',
            'font': ('Arial', 10, 'bold'),
            'relief': 'flat',
            'bd': 0,
            'padx': 15,
            'pady': 8,
            'cursor': 'hand2'
        }
        default_kwargs.update(kwargs)
        
        button = tk.Button(parent, text=text, command=command, **default_kwargs)
        
        # Add hover effects
        def on_enter(e):
            button.config(bg=self.colors['accent_hover'])
            
        def on_leave(e):
            if button['state'] != 'disabled':
                button.config(bg=self.colors['accent'])
            
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        
        return button
        
    def create_progressbar(self, parent: tk.Widget, **kwargs) -> ttk.Progressbar:
        """Create a modern styled progress bar"""
        default_kwargs = {
            'style': 'Modern.Horizontal.TProgressbar',
            'length': 200,
            'mode': 'determinate'
        }
        default_kwargs.update(kwargs)
        
        progressbar = ttk.Progressbar(parent, **default_kwargs)
        return progressbar
        
    def create_treeview(self, parent: tk.Widget, columns: tuple, **kwargs) -> ttk.Treeview:
        """Create a modern styled treeview"""
        default_kwargs = {
            'style': 'Modern.Treeview',
            'show': 'headings',
            'selectmode': 'browse'
        }
        default_kwargs.update(kwargs)
        
        # Create treeview with scrollbar
        tree_frame = self.create_frame(parent)
        
        tree = ttk.Treeview(tree_frame, columns=columns, **default_kwargs)
        
        # Configure columns
        for col in columns:
            tree.heading(col, text=col, anchor='w')
            tree.column(col, width=100, anchor='w')
            
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack components
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        tree_frame.pack(fill='both', expand=True)
        
        return tree
        
    def create_text_widget(self, parent: tk.Widget, **kwargs) -> tk.Text:
        """Create a modern styled text widget"""
        default_kwargs = {
            'bg': self.colors['bg_secondary'],
            'fg': self.colors['fg_primary'],
            'font': ('Arial', 10),
            'relief': 'flat',
            'bd': 1,
            'wrap': 'word',
            'padx': 10,
            'pady': 10
        }
        default_kwargs.update(kwargs)
        
        text_widget = tk.Text(parent, **default_kwargs)
        return text_widget
        
    def create_entry(self, parent: tk.Widget, **kwargs) -> tk.Entry:
        """Create a modern styled entry widget"""
        default_kwargs = {
            'bg': self.colors['bg_tertiary'],
            'fg': self.colors['fg_primary'],
            'font': ('Arial', 10),
            'relief': 'flat',
            'bd': 1,
            'insertbackground': self.colors['fg_primary']
        }
        default_kwargs.update(kwargs)
        
        entry = tk.Entry(parent, **default_kwargs)
        return entry
        
    def create_separator(self, parent: tk.Widget, **kwargs) -> ttk.Separator:
        """Create a separator line"""
        default_kwargs = {
            'orient': 'horizontal'
        }
        default_kwargs.update(kwargs)
        
        separator = ttk.Separator(parent, **default_kwargs)
        return separator
        
    def show_tooltip(self, widget: tk.Widget, text: str):
        """Add tooltip to a widget"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(tooltip, text=text,
                           background=self.colors['bg_tertiary'],
                           foreground=self.colors['fg_primary'],
                           font=('Arial', 9),
                           relief='solid',
                           borderwidth=1,
                           padx=5, pady=3)
            label.pack()
            
            widget.tooltip = tooltip
            
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
                
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        
    def create_status_indicator(self, parent: tk.Widget, status: str = 'active') -> tk.Label:
        """Create a status indicator"""
        status_colors = {
            'active': self.colors['accent'],
            'warning': self.colors['warning'],
            'error': self.colors['error'],
            'info': self.colors['info']
        }
        
        status_texts = {
            'active': '● Active',
            'warning': '⚠ Warning',
            'error': '● Error',
            'info': '● Info'
        }
        
        indicator = self.create_label(
            parent,
            status_texts.get(status, '● Unknown'),
            fg=status_colors.get(status, self.colors['fg_secondary']),
            font=('Arial', 10, 'bold')
        )
        
        return indicator