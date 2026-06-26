"""
Toolbar UI Component
Provides quick access to common operations through toolbar buttons.
"""
import tkinter as tk
from tkinter import ttk


class Toolbar(ttk.Frame):
    """Toolbar controller with quick access buttons"""

    def __init__(self, parent, main_window):
        """
        Initialize toolbar

        Args:
            parent: Parent window
            main_window: Reference to MainWindow instance
        """
        super().__init__(parent, relief=tk.RAISED, borderwidth=1)
        self.main_window = main_window

        # Create toolbar buttons
        self._create_buttons()

    def _create_buttons(self):
        """Create toolbar buttons"""
        # File operations
        self.btn_open = ttk.Button(self, text="📁 Open", command=self.on_open)
        self.btn_open.pack(side=tk.LEFT, padx=2, pady=2)

        self.btn_save = ttk.Button(self, text="💾 Save", command=self.on_save)
        self.btn_save.pack(side=tk.LEFT, padx=2, pady=2)

        # Add separator
        ttk.Separator(self, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=2)

        # Splitting operations
        self.btn_split_word = ttk.Button(self, text="✂️ Split Word", command=self.on_split_word)
        self.btn_split_word.pack(side=tk.LEFT, padx=2, pady=2)

        self.btn_split_xml = ttk.Button(self, text="✂️ Split XML", command=self.on_split_xml)
        self.btn_split_xml.pack(side=tk.LEFT, padx=2, pady=2)

        # Add separator
        ttk.Separator(self, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=2)

        # Merging operations
        self.btn_merge_word = ttk.Button(self, text="🔗 Merge Word", command=self.on_merge_word)
        self.btn_merge_word.pack(side=tk.LEFT, padx=2, pady=2)

        self.btn_merge_xml = ttk.Button(self, text="🔗 Merge XML", command=self.on_merge_xml)
        self.btn_merge_xml.pack(side=tk.LEFT, padx=2, pady=2)

        # Add separator
        ttk.Separator(self, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=2)

        # Naming tool
        self.btn_naming = ttk.Button(self, text="📝 Naming", command=self.on_naming)
        self.btn_naming.pack(side=tk.LEFT, padx=2, pady=2)

        # Add separator
        ttk.Separator(self, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=2)

        # Test thread button
        self.btn_test_thread = ttk.Button(self, text="🧪 Test Thread", command=self.on_test_thread)
        self.btn_test_thread.pack(side=tk.LEFT, padx=2, pady=2)

        # Right side buttons
        # Theme toggle button (on the right)
        self.btn_theme = ttk.Button(self, text="🌙 Dark Mode", command=self.on_toggle_theme, width=12)
        self.btn_theme.pack(side=tk.RIGHT, padx=2, pady=2)

        # Update theme button text based on current theme
        self._update_theme_button()

    def on_open(self):
        """Handle open button click"""
        self.main_window.menu_bar.on_open_file()

    def on_save(self):
        """Handle save button click"""
        self.main_window.menu_bar.on_save()

    def on_split_word(self):
        """Handle split word button click"""
        self.main_window.menu_bar.on_split_word()

    def on_split_xml(self):
        """Handle split XML button click"""
        self.main_window.menu_bar.on_split_xml()

    def on_merge_word(self):
        """Handle merge word button click"""
        self.main_window.menu_bar.on_merge_word()

    def on_merge_xml(self):
        """Handle merge XML button click"""
        self.main_window.menu_bar.on_merge_xml()

    def on_naming(self):
        """Handle name button click"""
        self.main_window.menu_bar.on_naming_tool()

    def on_test_thread(self):
        """Handle test thread button click"""
        from thread.example_workers import test_progress_worker

        # Create and start a test thread
        thread_id = self.main_window.thread_manager.create_thread(
            name="Test Progress Thread",
            target=test_progress_worker,
            args=(),
            kwargs={'task_name': 'Test Progress Task', 'duration': 20}
        )

        self.main_window.thread_manager.start_thread(thread_id)
        self.main_window.set_status(f"Started test thread: {thread_id}", "success")

    def on_toggle_theme(self):
        """Handle theme toggle button click"""
        self.main_window.toggle_theme()
        self._update_theme_button()
        self.main_window.set_status(
            f"Switched to {'dark' if self.main_window.theme_manager.is_dark() else 'light'} mode",
            "success"
        )

    def _update_theme_button(self):
        """Update theme button text based on current theme"""
        if self.main_window.theme_manager.is_dark():
            self.btn_theme.config(text="☀️ Light Mode")
        else:
            self.btn_theme.config(text="🌙 Dark Mode")


