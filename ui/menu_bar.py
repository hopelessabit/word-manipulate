"""
Menu Bar UI Component
Manages the application menu bar with File, Edit, Tools, and Help menus.
"""
import tkinter as tk
from tkinter import filedialog
from .dialogs import SplitDialog, MergeDialog, NamingDialog


class MenuBar:
    """Menu bar controller"""

    def __init__(self, parent, main_window):
        """
        Initialize menu bar

        Args:
            parent: Parent window
            main_window: Reference to MainWindow instance
        """
        self.parent = parent
        self.main_window = main_window

        # Create menu bar
        self.menubar = tk.Menu(parent)
        parent.config(menu=self.menubar)

        # Store menu references for theming
        self.menus = []

        # Create menus
        self._create_file_menu()
        self._create_edit_menu()
        self._create_tools_menu()
        self._create_help_menu()

        # Apply initial theme
        self._apply_theme()

    def _apply_theme(self):
        """Apply current theme to menu bar"""
        try:
            theme = self.main_window.theme_manager.current_theme

            # Apply to menubar
            self.menubar.configure(
                background=theme['menu_bg'],
                foreground=theme['menu_fg'],
                activebackground=theme['menu_active_bg'],
                activeforeground=theme['menu_active_fg'],
                relief='flat',
                borderwidth=0
            )

            # Apply to all menus
            for menu in self.menus:
                menu.configure(
                    background=theme['menu_bg'],
                    foreground=theme['menu_fg'],
                    activebackground=theme['menu_active_bg'],
                    activeforeground=theme['menu_active_fg'],
                    selectcolor=theme['accent'],
                    relief='flat',
                    borderwidth=1
                )
        except Exception as e:
            print(f"Menu theme error: {e}")

    def _create_file_menu(self):
        """Create File menu"""
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)
        self.menus.append(file_menu)

        file_menu.add_command(label="Open File...", command=self.on_open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Open Folder...", command=self.on_open_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=self.on_save, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.on_save_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.main_window.on_closing, accelerator="Alt+F4")

    def _create_edit_menu(self):
        """Create Edit menu"""
        edit_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Edit", menu=edit_menu)
        self.menus.append(edit_menu)

        edit_menu.add_command(label="Undo", command=self.on_undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.on_redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Preferences...", command=self.on_preferences)

    def _create_tools_menu(self):
        """Create Tools menu"""
        tools_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Tools", menu=tools_menu)
        self.menus.append(tools_menu)

        # Splitting submenu
        splitting_menu = tk.Menu(tools_menu, tearoff=0)
        tools_menu.add_cascade(label="Splitting", menu=splitting_menu)
        self.menus.append(splitting_menu)
        splitting_menu.add_command(label="Split Word Document", command=self.on_split_word)
        splitting_menu.add_command(label="Split XML Document", command=self.on_split_xml)

        # Merging submenu
        merging_menu = tk.Menu(tools_menu, tearoff=0)
        tools_menu.add_cascade(label="Merging", menu=merging_menu)
        self.menus.append(merging_menu)
        merging_menu.add_command(label="Merge Word Documents", command=self.on_merge_word)
        merging_menu.add_command(label="Merge XML Documents", command=self.on_merge_xml)

        # Naming tools
        tools_menu.add_separator()
        tools_menu.add_command(label="Naming Tool...", command=self.on_naming_tool)

    def _create_help_menu(self):
        """Create Help menu"""
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        self.menus.append(help_menu)

        help_menu.add_command(label="Documentation", command=self.on_documentation)
        help_menu.add_command(label="About", command=self.on_about)

    # File menu handlers
    def on_open_file(self):
        """Handle open file action"""
        filename = filedialog.askopenfilename(
            title="Select a file",
            filetypes=[("All Files", "*.*"), ("Word Documents", "*.docx"), ("XML Files", "*.xml")]
        )
        if filename:
            self.main_window.set_status(f"Opened: {filename}")
            # TODO: Load file logic

    def on_open_folder(self):
        """Handle open folder action"""
        folder = filedialog.askdirectory(title="Select a folder")
        if folder:
            self.main_window.set_status(f"Opened folder: {folder}")
            # TODO: Load folder logic

    def on_save(self):
        """Handle save action"""
        self.main_window.set_status("Save functionality not yet implemented")

    def on_save_as(self):
        """Handle save as action"""
        filename = filedialog.asksaveasfilename(
            title="Save file as",
            defaultextension=".docx",
            filetypes=[("Word Documents", "*.docx"), ("XML Files", "*.xml"), ("All Files", "*.*")]
        )
        if filename:
            self.main_window.set_status(f"Saved as: {filename}")
            # TODO: Save file logic

    # Edit menu handlers
    def on_undo(self):
        """Handle undo action"""
        self.main_window.set_status("Undo functionality not yet implemented")

    def on_redo(self):
        """Handle redo action"""
        self.main_window.set_status("Redo functionality not yet implemented")

    def on_preferences(self):
        """Handle preferences action"""
        self.main_window.set_status("Preferences dialog not yet implemented")

    # Tools menu handlers
    def on_split_word(self):
        """Handle split word document action"""
        dialog = SplitDialog(self.parent, doc_type="word")
        self.parent.wait_window(dialog)
        if dialog.result:
            self.main_window.set_status(f"Ready to split: {dialog.result['input_path']}")
            # TODO: Call actual split logic
            self.main_window.show_info("Split Operation", "Split logic not yet implemented.")

    def on_split_xml(self):
        """Handle split XML document action"""
        dialog = SplitDialog(self.parent, doc_type="xml")
        self.parent.wait_window(dialog)
        if dialog.result:
            self.main_window.set_status(f"Ready to split: {dialog.result['input_path']}")
            # TODO: Call actual split logic
            self.main_window.show_info("Split Operation", "Split logic not yet implemented.")

    def on_merge_word(self):
        """Handle merge word documents action"""
        dialog = MergeDialog(self.parent, doc_type="word")
        self.parent.wait_window(dialog)
        if dialog.result:
            self.main_window.set_status(f"Ready to merge {len(dialog.result['input_files'])} files")
            # TODO: Call actual merge logic
            self.main_window.show_info("Merge Operation", "Merge logic not yet implemented.")

    def on_merge_xml(self):
        """Handle merge XML documents action"""
        dialog = MergeDialog(self.parent, doc_type="xml")
        self.parent.wait_window(dialog)
        if dialog.result:
            self.main_window.set_status(f"Ready to merge {len(dialog.result['input_files'])} files")
            # TODO: Call actual merge logic
            self.main_window.show_info("Merge Operation", "Merge logic not yet implemented.")

    def on_naming_tool(self):
        """Handle name tool action"""
        dialog = NamingDialog(self.parent)
        self.parent.wait_window(dialog)
        if dialog.result:
            self.main_window.set_status(f"Ready to rename {len(dialog.result['files'])} files")
            # TODO: Call actual name logic
            self.main_window.show_info("Naming Operation", "Naming logic not yet implemented.")

    # Help menu handlers
    def on_documentation(self):
        """Handle documentation action"""
        self.main_window.show_info("Documentation", "Documentation will be available soon.")

    def on_about(self):
        """Handle about action"""
        self.main_window.show_info("About", "Wording Tool v1.0\n\nA tool for managing Word and XML documents.")

