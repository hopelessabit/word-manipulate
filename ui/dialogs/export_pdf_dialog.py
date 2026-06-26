"""
Export PDF Dialog
Provides UI for exporting DOCX documents to PDF
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List, Dict, Optional
import os
from pathlib import Path


def show_export_pdf_dialog(parent, files: List[str], theme_manager) -> Optional[Dict]:
    """
    Show export PDF dialog

    Args:
        parent: Parent window
        files: List of DOCX file paths to export
        theme_manager: Theme manager instance

    Returns:
        Dict with export configuration or None if cancelled
    """
    dialog = ExportPdfDialog(parent, files, theme_manager)
    return dialog.result


class ExportPdfDialog(tk.Toplevel):
    """Dialog for configuring PDF export operation"""

    def __init__(self, parent, files: List[str], theme_manager):
        super().__init__(parent)

        self.files = files
        self.theme_manager = theme_manager
        self.result = None

        # Configure window
        self.title(f"Export to PDF - {len(files)} Files")
        self.geometry("800x850")  # Increased height for better visibility
        self.resizable(True, True)
        self.minsize(700, 750)  # Ensure buttons are always visible

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Create UI
        self._create_widgets()

        # Apply theme
        self._apply_theme()

        # Center on parent
        self._center_on_parent(parent)

        # Wait for dialog to close
        self.wait_window()

    def _create_widgets(self):
        """Create all widgets"""
        # Outer container for scroll area
        outer_container = ttk.Frame(self)
        outer_container.pack(fill=tk.BOTH, expand=True)

        # Create scrollable canvas
        scroll_canvas = tk.Canvas(outer_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer_container, orient=tk.VERTICAL, command=scroll_canvas.yview)

        main_frame = ttk.Frame(scroll_canvas, padding=20)

        # Configure scrolling
        main_frame.bind(
            "<Configure>",
            lambda e: scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))
        )

        scroll_canvas.create_window((0, 0), window=main_frame, anchor="nw")
        scroll_canvas.configure(yscrollcommand=scrollbar.set)

        # Pack scrollable area
        scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            try:
                scroll_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except tk.TclError:
                # Canvas destroyed, unbind event
                pass

        # Store for cleanup
        self._mousewheel_handler = _on_mousewheel
        scroll_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Bind cleanup on dialog close
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Title
        title_label = ttk.Label(main_frame,
                               text="📄 Export to PDF",
                               font=('TkDefaultFont', 14, 'bold'))
        title_label.pack(pady=(0, 20))

        # Info section
        info_frame = ttk.LabelFrame(main_frame, text="ℹ️ Export Information", padding=15)
        info_frame.pack(fill=tk.X, pady=(0, 20))

        info_text = f"• Total files to export: {len(self.files)}\n"
        info_text += f"• All files will be converted to PDF format\n"
        info_text += f"• Original formatting will be preserved\n"
        info_text += f"• Output files will have the same name with .pdf extension\n"
        info_text += f"• Multi-threaded processing for faster conversion"

        info_label = ttk.Label(info_frame, text=info_text, justify=tk.LEFT)
        info_label.pack(anchor=tk.W)

        # File list section
        list_frame = ttk.LabelFrame(main_frame, text="📑 Files to Export", padding=10)
        list_frame.pack(fill=tk.X, pady=(0, 20))

        # Create treeview with scrollbar
        tree_frame = ttk.Frame(list_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbar
        file_scrollbar = ttk.Scrollbar(tree_frame)
        file_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview
        self.file_tree = ttk.Treeview(tree_frame,
                                     columns=('file', 'size', 'output'),
                                     show='tree headings',
                                     yscrollcommand=file_scrollbar.set,
                                     height=10)
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        file_scrollbar.config(command=self.file_tree.yview)

        # Configure columns
        self.file_tree.heading('#0', text='#')
        self.file_tree.heading('file', text='Source File')
        self.file_tree.heading('size', text='Size')
        self.file_tree.heading('output', text='Output Name')

        self.file_tree.column('#0', width=50, minwidth=50)
        self.file_tree.column('file', width=300, minwidth=200)
        self.file_tree.column('size', width=100, minwidth=80)
        self.file_tree.column('output', width=300, minwidth=200)

        # Populate file list
        for i, file_path in enumerate(self.files, 1):
            file_name = Path(file_path).name
            output_name = f"{Path(file_path).stem}.pdf"

            try:
                file_size = os.path.getsize(file_path)
                size_kb = file_size / 1024
                size_str = f"{size_kb:.1f} KB"
            except:
                size_str = "Unknown"

            self.file_tree.insert('', tk.END, text=str(i),
                                 values=(file_name, size_str, output_name))

        # Export options section
        options_frame = ttk.LabelFrame(main_frame, text="⚙️ Export Options", padding=15)
        options_frame.pack(fill=tk.X, pady=(0, 20))

        # Quality note
        quality_label = ttk.Label(options_frame,
                                 text="📌 Export Quality:",
                                 font=('TkDefaultFont', 9, 'bold'))
        quality_label.pack(anchor=tk.W, pady=(0, 5))

        quality_note = ttk.Label(options_frame,
                                text="• Format preservation is prioritized for best results\n"
                                     "• Tables, images, and formatting will be maintained\n"
                                     "• Page layout and margins will be preserved",
                                justify=tk.LEFT,
                                font=('TkDefaultFont', 8))
        quality_note.pack(anchor=tk.W, padx=(15, 0), pady=(0, 10))

        # Threading info
        thread_label = ttk.Label(options_frame,
                                text="🚀 Multi-threading enabled for faster processing",
                                font=('TkDefaultFont', 8, 'italic'))
        thread_label.pack(anchor=tk.W)

        # Output section
        output_frame = ttk.LabelFrame(main_frame, text="💾 Output Settings", padding=15)
        output_frame.pack(fill=tk.X, pady=(0, 20))

        # Output directory
        dir_frame = ttk.Frame(output_frame)
        dir_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(dir_frame, text="Output Directory:").pack(side=tk.LEFT, padx=(0, 10))

        self.output_dir_var = tk.StringVar()
        # Default to parent directory of first file
        default_dir = str(Path(self.files[0]).parent)
        self.output_dir_var.set(default_dir)

        output_dir_entry = ttk.Entry(dir_frame, textvariable=self.output_dir_var)
        output_dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        ttk.Button(dir_frame, text="📁 Browse...",
                  command=self._browse_output_dir).pack(side=tk.LEFT)

        # Info label
        info_label = ttk.Label(output_frame,
                              text="💡 PDF files will be created with the same name as source files",
                              font=('TkDefaultFont', 8, 'italic'))
        info_label.pack(anchor=tk.W)

        # Fixed button bar at bottom (outside scrollable area)
        button_container = ttk.Frame(self, padding=(20, 10, 20, 15))
        button_container.pack(fill=tk.X, side=tk.BOTTOM)

        # Separator line
        ttk.Separator(button_container, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(0, 10))

        button_frame = ttk.Frame(button_container)
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="✅ Export to PDF",
                  command=self._on_export,
                  style='Accent.TButton').pack(side=tk.RIGHT, padx=(5, 0))

        ttk.Button(button_frame, text="❌ Cancel",
                  command=self._on_cancel).pack(side=tk.RIGHT)

    def _apply_theme(self):
        """Apply current theme to dialog"""
        try:
            theme = self.theme_manager.current_theme

            # Configure window background
            self.configure(bg=theme['bg'])

            # Update file tree colors
            style = ttk.Style()
            style.configure('Treeview',
                          background=theme['input_bg'],
                          foreground=theme['fg'],
                          fieldbackground=theme['input_bg'])
            style.map('Treeview',
                     background=[('selected', theme['select_bg'])],
                     foreground=[('selected', theme['select_fg'])])
        except Exception as e:
            print(f"Theme apply error in export PDF dialog: {e}")

    def _center_on_parent(self, parent):
        """Center dialog on parent window"""
        self.update_idletasks()

        # Get parent position and size
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        # Get dialog size
        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()

        # Calculate position
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2

        self.geometry(f"+{x}+{y}")

    def _browse_output_dir(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.output_dir_var.get()
        )

        if directory:
            self.output_dir_var.set(directory)

    def _validate_output(self) -> bool:
        """Validate output settings"""
        output_dir = self.output_dir_var.get().strip()

        if not output_dir:
            messagebox.showerror("Invalid Output",
                               "Please specify an output directory.",
                               parent=self)
            return False

        # Check if output directory exists or can be created
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Invalid Output",
                               f"Cannot create output directory:\n{str(e)}",
                               parent=self)
            return False

        # Check if any output files already exist
        existing_files = []
        for file_path in self.files:
            output_name = f"{Path(file_path).stem}.pdf"
            output_path = os.path.join(output_dir, output_name)
            if os.path.exists(output_path):
                existing_files.append(output_name)

        if existing_files:
            file_list = "\n".join(existing_files[:5])
            if len(existing_files) > 5:
                file_list += f"\n... and {len(existing_files) - 5} more"

            response = messagebox.askyesno("Files Exist",
                                          f"{len(existing_files)} PDF file(s) already exist:\n\n"
                                          f"{file_list}\n\n"
                                          "Do you want to overwrite them?",
                                          parent=self)
            if not response:
                return False

        return True

    def _on_export(self):
        """Handle export button click"""
        if not self._validate_output():
            return

        # Build result configuration
        self.result = {
            'files': self.files.copy(),
            'output_dir': self.output_dir_var.get().strip()
        }

        self._cleanup()
        self.destroy()

    def _on_cancel(self):
        """Handle cancel button click"""
        self.result = None
        self._cleanup()
        self.destroy()

    def _on_close(self):
        """Handle window close button"""
        self.result = None
        self._cleanup()
        self.destroy()

    def _cleanup(self):
        """Cleanup event bindings"""
        try:
            if hasattr(self, '_mousewheel_handler'):
                self.unbind_all("<MouseWheel>")
        except:
            pass

