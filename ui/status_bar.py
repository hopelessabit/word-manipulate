"""
Status Bar UI Component
Displays status messages and application state information at the bottom of the window.
"""
import tkinter as tk
from tkinter import ttk


class StatusBar(ttk.Frame):
    """Status bar controller"""

    def __init__(self, parent, main_window):
        """
        Initialize status bar

        Args:
            parent: Parent window
            main_window: Reference to MainWindow instance
        """
        super().__init__(parent, relief=tk.SUNKEN, borderwidth=1)
        self.main_window = main_window

        # Status message label
        self.status_label = ttk.Label(self, text="Ready", anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=2)

        # Progress bar (hidden by default)
        self.progress = ttk.Progressbar(self, mode='indeterminate', length=100)

        # Additional info label (e.g., file count, size)
        self.info_label = ttk.Label(self, text="", anchor=tk.E, width=30)
        self.info_label.pack(side=tk.RIGHT, padx=5, pady=2)

    def set_message(self, message, status_type="info"):
        """
        Set status message

        Args:
            message: Message to display
            status_type: Type of status ('info', 'warning', 'error', 'success')
        """
        self.status_label.config(text=message)

        # You can add color coding based on status_type if needed
        # For now, just display the message

    def set_info(self, info_text):
        """
        Set additional info text

        Args:
            info_text: Information text to display on the right
        """
        self.info_label.config(text=info_text)

    def show_progress(self):
        """Show and start progress bar"""
        self.progress.pack(side=tk.RIGHT, padx=5, pady=2, before=self.info_label)
        self.progress.start()

    def hide_progress(self):
        """Hide and stop progress bar"""
        self.progress.stop()
        self.progress.pack_forget()

