"""
Split Dialog
Dialog for configuring document split operations.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from .base_dialog import BaseDialog


class SplitDialog(BaseDialog):
    """Dialog for split documents"""

    def __init__(self, parent, doc_type="word"):
        """
        Initialize split dialog

        Args:
            parent: Parent window
            doc_type: Type of document ('word' or 'xml')
        """
        self.doc_type = doc_type
        title = f"Split {doc_type.upper()} Document"
        super().__init__(parent, title=title, width=700, height=500)

    def _create_body(self):
        """Create dialog body with split options"""
        self.body_frame = ttk.Frame(self, padding=10)
        self.body_frame.pack(fill=tk.BOTH, expand=True)

        # Input file selection
        input_frame = ttk.LabelFrame(self.body_frame, text="Input File", padding=10)
        input_frame.pack(fill=tk.X, pady=5)

        self.input_path = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.input_path, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(input_frame, text="Browse...", command=self.browse_input).pack(side=tk.LEFT, padx=5)

        # Output directory selection
        output_frame = ttk.LabelFrame(self.body_frame, text="Output Directory", padding=10)
        output_frame.pack(fill=tk.X, pady=5)

        self.output_path = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.output_path, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(output_frame, text="Browse...", command=self.browse_output).pack(side=tk.LEFT, padx=5)

        # Split options
        options_frame = ttk.LabelFrame(self.body_frame, text="Split Options", padding=10)
        options_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Split method
        ttk.Label(options_frame, text="Split by:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.split_method = tk.StringVar(value="pages")

        methods_frame = ttk.Frame(options_frame)
        methods_frame.grid(row=0, column=1, sticky=tk.W, pady=5)

        ttk.Radiobutton(methods_frame, text="Pages", variable=self.split_method,
                        value="pages", command=self.on_method_change).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(methods_frame, text="Sections", variable=self.split_method,
                        value="sections", command=self.on_method_change).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(methods_frame, text="Size", variable=self.split_method,
                        value="size", command=self.on_method_change).pack(side=tk.LEFT, padx=5)

        # Split value
        self.value_frame = ttk.Frame(options_frame)
        self.value_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)

        ttk.Label(self.value_frame, text="Pages per file:").pack(side=tk.LEFT, padx=5)
        self.split_value = tk.StringVar(value="10")
        ttk.Entry(self.value_frame, textvariable=self.split_value, width=10).pack(side=tk.LEFT, padx=5)

        # Naming pattern
        ttk.Label(options_frame, text="Output name pattern:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.naming_pattern = tk.StringVar(value="{name}_part{n}")
        ttk.Entry(options_frame, textvariable=self.naming_pattern, width=30).grid(row=2, column=1, sticky=tk.W, pady=5)

        # Preview area
        preview_frame = ttk.LabelFrame(self.body_frame, text="Preview", padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.preview_text = tk.Text(preview_frame, height=5, wrap=tk.WORD)
        preview_scroll = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=preview_scroll.set)

        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preview_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.preview_text.insert(tk.END, "Output preview will appear here...")
        self.preview_text.config(state=tk.DISABLED)

    def browse_input(self):
        """Browse for input file"""
        if self.doc_type == "word":
            filetypes = [("Word Documents", "*.docx"), ("All Files", "*.*")]
        else:
            filetypes = [("XML Files", "*.xml"), ("All Files", "*.*")]

        filename = filedialog.askopenfilename(title="Select input file", filetypes=filetypes)
        if filename:
            self.input_path.set(filename)

    def browse_output(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(title="Select output directory")
        if directory:
            self.output_path.set(directory)

    def on_method_change(self):
        """Handle split method change"""
        # Clear value frame
        for widget in self.value_frame.winfo_children():
            widget.destroy()

        method = self.split_method.get()

        if method == "pages":
            ttk.Label(self.value_frame, text="Pages per file:").pack(side=tk.LEFT, padx=5)
            self.split_value = tk.StringVar(value="10")
            ttk.Entry(self.value_frame, textvariable=self.split_value, width=10).pack(side=tk.LEFT, padx=5)
        elif method == "sections":
            ttk.Label(self.value_frame, text="Sections per file:").pack(side=tk.LEFT, padx=5)
            self.split_value = tk.StringVar(value="1")
            ttk.Entry(self.value_frame, textvariable=self.split_value, width=10).pack(side=tk.LEFT, padx=5)
        elif method == "size":
            ttk.Label(self.value_frame, text="Max size (MB):").pack(side=tk.LEFT, padx=5)
            self.split_value = tk.StringVar(value="5")
            ttk.Entry(self.value_frame, textvariable=self.split_value, width=10).pack(side=tk.LEFT, padx=5)

    def validate(self):
        """Validate dialog input"""
        if not self.input_path.get():
            messagebox.showerror("Error", "Please select an input file.")
            return False

        if not self.output_path.get():
            messagebox.showerror("Error", "Please select an output directory.")
            return False

        try:
            value = int(self.split_value.get())
            if value <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive number for split value.")
            return False

        return True

    def get_result(self):
        """Get dialog result"""
        return {
            'input_path': self.input_path.get(),
            'output_path': self.output_path.get(),
            'split_method': self.split_method.get(),
            'split_value': int(self.split_value.get()),
            'naming_pattern': self.naming_pattern.get(),
            'doc_type': self.doc_type
        }

