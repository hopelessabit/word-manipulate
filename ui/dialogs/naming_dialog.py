"""
Naming Dialog
Dialog for file name and renaming operations.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from .base_dialog import BaseDialog


class NamingDialog(BaseDialog):
    """Dialog for file name operations"""

    def __init__(self, parent):
        """
        Initialize name dialog

        Args:
            parent: Parent window
        """
        super().__init__(parent, title="File Naming Tool", width=700, height=500)

    def _create_body(self):
        """Create dialog body with name options"""
        self.body_frame = ttk.Frame(self, padding=10)
        self.body_frame.pack(fill=tk.BOTH, expand=True)

        # Directory selection
        dir_frame = ttk.LabelFrame(self.body_frame, text="Target Directory", padding=10)
        dir_frame.pack(fill=tk.X, pady=5)

        self.dir_path = tk.StringVar()
        ttk.Entry(dir_frame, textvariable=self.dir_path, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(dir_frame, text="Browse...", command=self.browse_directory).pack(side=tk.LEFT, padx=5)
        ttk.Button(dir_frame, text="Scan", command=self.scan_directory).pack(side=tk.LEFT, padx=2)

        # File list
        files_frame = ttk.LabelFrame(self.body_frame, text="Files", padding=10)
        files_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Create treeview for file list
        tree_frame = ttk.Frame(files_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("current", "new")
        self.file_tree = ttk.Treeview(tree_frame, columns=columns, show="tree headings", height=10)
        self.file_tree.heading("#0", text="Index")
        self.file_tree.heading("current", text="Current Name")
        self.file_tree.heading("new", text="New Name")
        self.file_tree.column("#0", width=50)
        self.file_tree.column("current", width=250)
        self.file_tree.column("new", width=250)

        tree_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=tree_scroll.set)

        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Naming options
        options_frame = ttk.LabelFrame(self.body_frame, text="Naming Options", padding=10)
        options_frame.pack(fill=tk.X, pady=5)

        # Naming pattern
        pattern_frame = ttk.Frame(options_frame)
        pattern_frame.pack(fill=tk.X, pady=2)

        ttk.Label(pattern_frame, text="Pattern:").pack(side=tk.LEFT, padx=5)
        self.naming_pattern = tk.StringVar(value="{name}_{index}")
        ttk.Entry(pattern_frame, textvariable=self.naming_pattern, width=30).pack(side=tk.LEFT, padx=5)
        ttk.Button(pattern_frame, text="Preview", command=self.preview_names).pack(side=tk.LEFT, padx=5)

        # Pattern help
        help_text = "Pattern variables: {name} = original name, {index} = number, {date} = date, {ext} = extension"
        ttk.Label(options_frame, text=help_text, font=("TkDefaultFont", 8)).pack(anchor=tk.W, pady=2)

        # Options
        opts_frame = ttk.Frame(options_frame)
        opts_frame.pack(fill=tk.X, pady=5)

        ttk.Label(opts_frame, text="Start index:").pack(side=tk.LEFT, padx=5)
        self.start_index = tk.StringVar(value="1")
        ttk.Entry(opts_frame, textvariable=self.start_index, width=10).pack(side=tk.LEFT, padx=5)

        ttk.Label(opts_frame, text="Zero padding:").pack(side=tk.LEFT, padx=5)
        self.zero_padding = tk.StringVar(value="3")
        ttk.Entry(opts_frame, textvariable=self.zero_padding, width=10).pack(side=tk.LEFT, padx=5)

        # Case options
        case_frame = ttk.Frame(options_frame)
        case_frame.pack(fill=tk.X, pady=2)

        ttk.Label(case_frame, text="Case:").pack(side=tk.LEFT, padx=5)
        self.case_option = tk.StringVar(value="keep")
        ttk.Radiobutton(case_frame, text="Keep", variable=self.case_option, value="keep").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(case_frame, text="Lower", variable=self.case_option, value="lower").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(case_frame, text="Upper", variable=self.case_option, value="upper").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(case_frame, text="Title", variable=self.case_option, value="title").pack(side=tk.LEFT, padx=5)

        # Store file data
        self.files_data = []

    def browse_directory(self):
        """Browse for directory"""
        directory = filedialog.askdirectory(title="Select directory")
        if directory:
            self.dir_path.set(directory)

    def scan_directory(self):
        """Scan directory for files"""
        import os
        directory = self.dir_path.get()
        if not directory:
            messagebox.showwarning("Warning", "Please select a directory first.")
            return

        if not os.path.isdir(directory):
            messagebox.showerror("Error", "Invalid directory path.")
            return

        # Clear current list
        self.file_tree.delete(*self.file_tree.get_children())
        self.files_data.clear()

        # Scan directory
        for index, filename in enumerate(sorted(os.listdir(directory)), start=1):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                self.files_data.append({'path': filepath, 'name': filename})
                self.file_tree.insert("", tk.END, text=str(index), values=(filename, ""))

        messagebox.showinfo("Success", f"Found {len(self.files_data)} files.")

    def preview_names(self):
        """Preview new names based on pattern"""
        if not self.files_data:
            messagebox.showwarning("Warning", "No files loaded. Please scan a directory first.")
            return

        try:
            start_idx = int(self.start_index.get())
            padding = int(self.zero_padding.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid start index or padding value.")
            return

        pattern = self.naming_pattern.get()
        case = self.case_option.get()

        # Update tree with new names
        for idx, (item, file_data) in enumerate(zip(self.file_tree.get_children(), self.files_data)):
            import os
            from datetime import datetime

            # Parse original name
            original_name = file_data['name']
            name_without_ext = os.path.splitext(original_name)[0]
            ext = os.path.splitext(original_name)[1]

            # Generate new name
            index_str = str(start_idx + idx).zfill(padding)
            date_str = datetime.now().strftime("%Y%m%d")

            new_name = pattern.replace("{name}", name_without_ext)
            new_name = new_name.replace("{index}", index_str)
            new_name = new_name.replace("{date}", date_str)
            new_name = new_name.replace("{ext}", ext.lstrip('.'))
            new_name += ext

            # Apply case transformation
            if case == "lower":
                new_name = new_name.lower()
            elif case == "upper":
                new_name = new_name.upper()
            elif case == "title":
                new_name = new_name.title()

            # Update tree
            self.file_tree.item(item, values=(original_name, new_name))
            file_data['new_name'] = new_name

    def validate(self):
        """Validate dialog input"""
        if not self.files_data:
            messagebox.showwarning("Warning", "No files to rename.")
            return False

        # Check if preview was generated
        if not any('new_name' in f for f in self.files_data):
            messagebox.showwarning("Warning", "Please click 'Preview' to generate new names first.")
            return False

        return True

    def get_result(self):
        """Get dialog result"""
        return {
            'directory': self.dir_path.get(),
            'files': self.files_data.copy(),
            'pattern': self.naming_pattern.get(),
            'case': self.case_option.get()
        }

