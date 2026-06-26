"""
Base Dialog Class
Base class for all dialog windows in the application.
"""
import tkinter as tk
from tkinter import ttk


class BaseDialog(tk.Toplevel):
    """Base dialog class with common functionality"""

    def __init__(self, parent, title="Dialog", width=600, height=400):
        """
        Initialize base dialog

        Args:
            parent: Parent window
            title: Dialog title
            width: Dialog width
            height: Dialog height
        """
        super().__init__(parent)

        self.parent = parent
        self.result = None

        # Configure dialog
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.minsize(400, 300)

        # Make dialog modal
        self.transient(parent)
        self.grab_set()

        # Center dialog on parent
        self.center_on_parent()

        # Create UI elements
        self._create_body()
        self._create_button_box()

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

    def center_on_parent(self):
        """Center the dialog on the parent window"""
        self.update_idletasks()

        # Get parent position and size
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()

        # Get dialog size
        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()

        # Calculate position
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2

        self.geometry(f"+{x}+{y}")

    def _create_body(self):
        """Create dialog body - to be overridden by subclasses"""
        self.body_frame = ttk.Frame(self, padding=10)
        self.body_frame.pack(fill=tk.BOTH, expand=True)

    def _create_button_box(self):
        """Create OK and Cancel buttons"""
        button_frame = ttk.Frame(self, padding=10)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        ttk.Button(button_frame, text="Cancel", command=self.on_cancel).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="OK", command=self.on_ok, default=tk.ACTIVE).pack(side=tk.RIGHT)

    def on_ok(self):
        """Handle OK button click"""
        if self.validate():
            self.result = self.get_result()
            self.destroy()

    def on_cancel(self):
        """Handle Cancel button click"""
        self.result = None
        self.destroy()

    def validate(self):
        """
        Validate dialog input - to be overridden by subclasses

        Returns:
            True if valid, False otherwise
        """
        return True

    def get_result(self):
        """
        Get dialog result - to be overridden by subclasses

        Returns:
            Dialog result data
        """
        return None

