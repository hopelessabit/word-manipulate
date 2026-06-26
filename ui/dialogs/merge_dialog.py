"""
Merge Dialog
Dialog for configuring document merge operations.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from .base_dialog import BaseDialog


class MergeDialog(BaseDialog):
    """Dialog for merge documents"""

    def __init__(self, parent, doc_type="word"):
        """
        Initialize merge dialog

        Args:
            parent: Parent window
            doc_type: Type of document ('word' or 'xml')
        """
        self.doc_type = doc_type
        title = f"Merge {doc_type.upper()} Documents"
        super().__init__(parent, title=title, width=700, height=500)

    def _create_body(self):
        """Create dialog body with merge options"""
        self.body_frame = ttk.Frame(self, padding=10)
        self.body_frame.pack(fill=tk.BOTH, expand=True)

        # Input files selection
        input_frame = ttk.LabelFrame(self.body_frame, text="Input Files", padding=10)
        input_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Listbox with files
        list_frame = ttk.Frame(input_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        self.file_listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED)
        list_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        self.file_listbox.configure(yscrollcommand=list_scroll.set)

        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Buttons for file list management
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(fill=tk.X, pady=5)

        ttk.Button(button_frame, text="Add Files...", command=self.add_files).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Add Folder...", command=self.add_folder).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Remove Selected", command=self.remove_files).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Move Up", command=self.move_up).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Move Down", command=self.move_down).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Clear All", command=self.clear_all).pack(side=tk.LEFT, padx=2)

        # Output file selection
        output_frame = ttk.LabelFrame(self.body_frame, text="Output File", padding=10)
        output_frame.pack(fill=tk.X, pady=5)

        self.output_path = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.output_path, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(output_frame, text="Browse...", command=self.browse_output).pack(side=tk.LEFT, padx=5)

        # Merge options
        options_frame = ttk.LabelFrame(self.body_frame, text="Merge Options", padding=10)
        options_frame.pack(fill=tk.X, pady=5)

        self.add_page_breaks = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Add page breaks between documents",
                        variable=self.add_page_breaks).pack(anchor=tk.W, pady=2)

        self.keep_formatting = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Keep original formatting",
                        variable=self.keep_formatting).pack(anchor=tk.W, pady=2)

        self.add_toc = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Generate table of contents",
                        variable=self.add_toc).pack(anchor=tk.W, pady=2)

        # Store file paths
        self.file_paths = []

    def add_files(self):
        """Add files to merge list"""
        if self.doc_type == "word":
            filetypes = [("Word Documents", "*.docx"), ("All Files", "*.*")]
        else:
            filetypes = [("XML Files", "*.xml"), ("All Files", "*.*")]

        filenames = filedialog.askopenfilenames(title="Select files to merge", filetypes=filetypes)
        for filename in filenames:
            if filename not in self.file_paths:
                self.file_paths.append(filename)
                self.file_listbox.insert(tk.END, filename)

    def add_folder(self):
        """Add all files from a folder"""
        import os
        directory = filedialog.askdirectory(title="Select folder")
        if directory:
            ext = ".docx" if self.doc_type == "word" else ".xml"
            for filename in sorted(os.listdir(directory)):
                if filename.endswith(ext):
                    filepath = os.path.join(directory, filename)
                    if filepath not in self.file_paths:
                        self.file_paths.append(filepath)
                        self.file_listbox.insert(tk.END, filepath)

    def remove_files(self):
        """Remove selected files"""
        selection = self.file_listbox.curselection()
        for index in reversed(selection):
            del self.file_paths[index]
            self.file_listbox.delete(index)

    def move_up(self):
        """Move selected file up"""
        selection = self.file_listbox.curselection()
        if selection and selection[0] > 0:
            index = selection[0]
            # Swap in list
            self.file_paths[index], self.file_paths[index-1] = self.file_paths[index-1], self.file_paths[index]
            # Update listbox
            item = self.file_listbox.get(index)
            self.file_listbox.delete(index)
            self.file_listbox.insert(index-1, item)
            self.file_listbox.selection_set(index-1)

    def move_down(self):
        """Move selected file down"""
        selection = self.file_listbox.curselection()
        if selection and selection[0] < len(self.file_paths) - 1:
            index = selection[0]
            # Swap in list
            self.file_paths[index], self.file_paths[index+1] = self.file_paths[index+1], self.file_paths[index]
            # Update listbox
            item = self.file_listbox.get(index)
            self.file_listbox.delete(index)
            self.file_listbox.insert(index+1, item)
            self.file_listbox.selection_set(index+1)

    def clear_all(self):
        """Clear all files"""
        self.file_paths.clear()
        self.file_listbox.delete(0, tk.END)

    def browse_output(self):
        """Browse for output file"""
        if self.doc_type == "word":
            filetypes = [("Word Documents", "*.docx"), ("All Files", "*.*")]
            default_ext = ".docx"
        else:
            filetypes = [("XML Files", "*.xml"), ("All Files", "*.*")]
            default_ext = ".xml"

        filename = filedialog.asksaveasfilename(
            title="Save merged file as",
            defaultextension=default_ext,
            filetypes=filetypes
        )
        if filename:
            self.output_path.set(filename)

    def validate(self):
        """Validate dialog input"""
        if len(self.file_paths) < 2:
            messagebox.showerror("Error", "Please select at least 2 files to merge.")
            return False

        if not self.output_path.get():
            messagebox.showerror("Error", "Please specify an output file.")
            return False

        return True

    def get_result(self):
        """Get dialog result"""
        return {
            'input_files': self.file_paths.copy(),
            'output_path': self.output_path.get(),
            'add_page_breaks': self.add_page_breaks.get(),
            'keep_formatting': self.keep_formatting.get(),
            'add_toc': self.add_toc.get(),
            'doc_type': self.doc_type
        }

