"""
Main Window UI Control
This is the main UI controller that manages the application window and coordinates all UI components.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from .menu_bar import MenuBar
from .toolbar import Toolbar
from .status_bar import StatusBar
from .work_area import WorkArea
from .theme_manager import get_theme_manager
from thread import ThreadManager


class MainWindow:
    """Main application window controller"""

    def __init__(self):
        """Initialize the main window"""
        self.root = tk.Tk()
        self.root.title("Wording Tool")
        self.root.geometry("1200x800")

        # Set minimum window size
        self.root.minsize(800, 600)

        # Initialize theme manager
        self.theme_manager = get_theme_manager()
        self.theme_manager.register_callback(self._apply_theme)

        # Initialize thread manager
        self.thread_manager = ThreadManager()

        # Configure ttk styles
        self._setup_styles()

        # Initialize UI components
        self._init_components()

        # Apply initial theme
        self._apply_theme()

        # Configure window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _setup_styles(self):
        """Setup ttk styles for theming"""
        self.style = ttk.Style()
        # Use 'clam' theme as base for better customization
        try:
            self.style.theme_use('clam')
        except:
            pass

    def _apply_theme(self):
        """Apply current theme to all widgets"""
        theme = self.theme_manager.current_theme

        # Apply to root window
        self.root.configure(background=theme['bg'])

        # Apply to menu bar (if it exists)
        try:
            menu = self.root['menu']
            if menu:
                self._apply_menu_theme(menu, theme)
        except:
            pass

        # Apply ttk styles
        style_config = self.theme_manager.get_ttk_style()

        for style_name, config in style_config.items():
            self.style.configure(style_name, **config)

        # Special styling for selected tabs
        self.style.map('TNotebook.Tab',
            background=[('selected', theme['accent'])],
            foreground=[('selected', theme['select_fg'])],
            expand=[('selected', [1, 1, 1, 0])]
        )

        # Button hover effects with smooth transitions
        self.style.map('TButton',
            background=[
                ('active', theme['button_active_bg']),
                ('pressed', theme['border']),
                ('disabled', theme['frame_bg'])
            ],
            foreground=[
                ('active', theme['button_fg']),
                ('disabled', theme['text_secondary'])
            ],
            bordercolor=[('active', theme['accent'])]
        )

        # Treeview styling with hover
        self.style.map('Treeview',
            background=[('selected', theme['select_bg'])],
            foreground=[('selected', theme['select_fg'])]
        )

        # Treeview heading hover
        self.style.map('Treeview.Heading',
            background=[('active', theme['button_active_bg'])],
            foreground=[('active', theme['accent'])]
        )

        # Entry field focus
        self.style.map('TEntry',
            bordercolor=[('focus', theme['accent'])],
            lightcolor=[('focus', theme['accent'])]
        )

        # LabelFrame styling
        self.style.configure('TLabelframe',
            background=theme['frame_bg'],
            bordercolor=theme['border'],
            relief='flat',
            borderwidth=1
        )

        self.style.configure('TLabelframe.Label',
            background=theme['frame_bg'],
            foreground=theme['accent'],
            font=('Segoe UI', 10, 'bold')
        )

        # Scrollbar disabled state (when content doesn't scroll)
        self.style.map('TScrollbar',
            background=[('disabled', theme['scrollbar_disabled_fg'])],
            troughcolor=[('disabled', theme['scrollbar_disabled_bg'])]
        )

        # PanedWindow sash (separator) styling
        self.style.configure('TPanedwindow',
            background=theme['frame_bg']
        )

        # Configure sash color for PanedWindow
        try:
            # This needs to be done on the root window level
            self.root.option_add('*Sash.background', theme['sash_bg'])
            self.root.option_add('*Sash.relief', 'flat')
        except:
            pass

        # Remove focus outline (gray dotted box) on buttons and widgets
        try:
            # Disable the default focus ring/highlight
            self.style.configure('TButton', focuscolor='none')
            self.style.configure('TEntry', focuscolor='none')
            self.style.configure('TCombobox', focuscolor='none')
            self.style.configure('TRadiobutton', focuscolor='none')

            # For tk widgets, set highlightthickness to 0
            self.root.option_add('*highlightThickness', '0')
            self.root.option_add('*Button.highlightThickness', '0')
            self.root.option_add('*Entry.highlightThickness', '0')
        except:
            pass

        # Radiobutton styling with proper colors for both themes
        self.style.configure('TRadiobutton',
            background=theme['frame_bg'],
            foreground=theme['fg'],
            indicatorbackground=theme['input_bg'],
            indicatorforeground=theme['accent'],
            bordercolor=theme['border'],
            focuscolor=''
        )

        # Radiobutton hover and selection states
        self.style.map('TRadiobutton',
            background=[
                ('active', theme['frame_bg']),
                ('selected', theme['frame_bg'])
            ],
            foreground=[
                ('active', theme['accent']),
                ('selected', theme['accent'])
            ],
            indicatorforeground=[
                ('selected', theme['accent']),
                ('active', theme['accent'])
            ]
        )

    def _apply_menu_theme(self, menu, theme):
        """Recursively apply theme to menu and submenus"""
        try:
            menu.configure(
                background=theme['menu_bg'],
                foreground=theme['menu_fg'],
                activebackground=theme['menu_active_bg'],
                activeforeground=theme['menu_active_fg'],
                relief='flat',
                borderwidth=0
            )

            # Apply to all submenus
            for i in range(menu.index('end') + 1 if menu.index('end') is not None else 0):
                try:
                    submenu = menu.entrycget(i, 'menu')
                    if submenu:
                        submenu_obj = self.root.nametowidget(submenu)
                        self._apply_menu_theme(submenu_obj, theme)
                except:
                    continue
        except:
            pass

    def toggle_theme(self):
        """Toggle between light and dark theme"""
        self.theme_manager.toggle_theme()
        # Theme is applied via callback

    def _init_components(self):
        """Initialize all UI components"""
        # Create menu bar
        self.menu_bar = MenuBar(self.root, self)

        # Register menu bar for theme updates
        self.theme_manager.register_callback(lambda: self.menu_bar._apply_theme())

        # Create toolbar
        self.toolbar = Toolbar(self.root, self)
        self.toolbar.pack(side=tk.TOP, fill=tk.X, padx=2, pady=2)

        # Create work area (main content)
        self.work_area = WorkArea(self.root, self)
        self.work_area.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create status bar
        self.status_bar = StatusBar(self.root, self)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def run(self):
        """Start the application main loop"""
        self.root.mainloop()

    def on_closing(self):
        """Handle window closing event"""
        if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
            self.root.destroy()

    def set_status(self, message, status_type="info"):
        """
        Set status bar message

        Args:
            message: Status message to display
            status_type: Type of status ('info', 'warning', 'error', 'success')
        """
        self.status_bar.set_message(message, status_type)

    def show_error(self, title, message):
        """Show error dialog"""
        messagebox.showerror(title, message)

    def show_info(self, title, message):
        """Show info dialog"""
        messagebox.showinfo(title, message)

    def show_warning(self, title, message):
        """Show warning dialog"""
        messagebox.showwarning(title, message)
