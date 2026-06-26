"""
Split Document Dialog
Provides UI for splitting DOCX documents with advanced options
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List, Dict, Optional
import os


class SplitRange:
    """Represents a split range with from/to keywords"""

    def __init__(self, from_keyword: str = "", to_keyword: str = "",
                 from_include_all: bool = False, to_include_all: bool = False,
                 from_start: bool = False, to_end: bool = False):
        self.from_keyword = from_keyword
        self.to_keyword = to_keyword
        self.from_include_all = from_include_all
        self.to_include_all = to_include_all
        self.from_start = from_start
        self.to_end = to_end


class SplitRangeWidget(ttk.Frame):
    """Widget for configuring a single split range"""

    def __init__(self, parent, range_num: int, on_remove_callback):
        super().__init__(parent, relief=tk.RIDGE, borderwidth=2, padding=10)
        self.range_num = range_num
        self.on_remove_callback = on_remove_callback

        self._create_widgets()

    def _create_widgets(self):
        """Create all widgets for this range"""
        # Header with range number and remove button
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(header_frame, text=f"📄 Range #{self.range_num}",
                 font=('TkDefaultFont', 10, 'bold')).pack(side=tk.LEFT)

        ttk.Button(header_frame, text="❌ Remove",
                  command=lambda: self.on_remove_callback(self),
                  width=10).pack(side=tk.RIGHT)

        # From section
        from_frame = ttk.LabelFrame(self, text="From (Start)", padding=10)
        from_frame.pack(fill=tk.X, pady=(0, 10))

        # From keyword or document start
        from_option_frame = ttk.Frame(from_frame)
        from_option_frame.pack(fill=tk.X, pady=(0, 5))

        self.from_start_var = tk.BooleanVar(value=False)
        self.from_start_check = ttk.Checkbutton(from_option_frame,
                                                text="📍 From document start",
                                                variable=self.from_start_var,
                                                command=self._on_from_start_toggle)
        self.from_start_check.pack(anchor=tk.W)

        # Keyword entry
        from_keyword_frame = ttk.Frame(from_frame)
        from_keyword_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(from_keyword_frame, text="Keyword:").pack(side=tk.LEFT, padx=(0, 5))
        self.from_keyword_var = tk.StringVar()
        self.from_keyword_entry = ttk.Entry(from_keyword_frame,
                                            textvariable=self.from_keyword_var,
                                            width=40)
        self.from_keyword_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Include all paragraphs with keyword
        self.from_include_all_var = tk.BooleanVar(value=False)
        self.from_include_all_check = ttk.Checkbutton(from_frame,
                                                      text="✅ Include all paragraphs containing this keyword",
                                                      variable=self.from_include_all_var)
        self.from_include_all_check.pack(anchor=tk.W)

        # To section
        to_frame = ttk.LabelFrame(self, text="To (End)", padding=10)
        to_frame.pack(fill=tk.X)

        # To keyword or document end
        to_option_frame = ttk.Frame(to_frame)
        to_option_frame.pack(fill=tk.X, pady=(0, 5))

        self.to_end_var = tk.BooleanVar(value=False)
        self.to_end_check = ttk.Checkbutton(to_option_frame,
                                           text="📍 To document end",
                                           variable=self.to_end_var,
                                           command=self._on_to_end_toggle)
        self.to_end_check.pack(anchor=tk.W)

        # Keyword entry
        to_keyword_frame = ttk.Frame(to_frame)
        to_keyword_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(to_keyword_frame, text="Keyword:").pack(side=tk.LEFT, padx=(0, 5))
        self.to_keyword_var = tk.StringVar()
        self.to_keyword_entry = ttk.Entry(to_keyword_frame,
                                         textvariable=self.to_keyword_var,
                                         width=40)
        self.to_keyword_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Include all paragraphs with keyword
        self.to_include_all_var = tk.BooleanVar(value=False)
        self.to_include_all_check = ttk.Checkbutton(to_frame,
                                                   text="✅ Include all paragraphs containing this keyword",
                                                   variable=self.to_include_all_var)
        self.to_include_all_check.pack(anchor=tk.W)

    def _on_from_start_toggle(self):
        """Toggle from keyword entry state"""
        if self.from_start_var.get():
            self.from_keyword_entry.config(state='disabled')
            self.from_include_all_check.config(state='disabled')
        else:
            self.from_keyword_entry.config(state='normal')
            self.from_include_all_check.config(state='normal')

    def _on_to_end_toggle(self):
        """Toggle to keyword entry state"""
        if self.to_end_var.get():
            self.to_keyword_entry.config(state='disabled')
            self.to_include_all_check.config(state='disabled')
        else:
            self.to_keyword_entry.config(state='normal')
            self.to_include_all_check.config(state='normal')

    def get_range(self) -> SplitRange:
        """Get the configured split range"""
        return SplitRange(
            from_keyword=self.from_keyword_var.get(),
            to_keyword=self.to_keyword_var.get(),
            from_include_all=self.from_include_all_var.get(),
            to_include_all=self.to_include_all_var.get(),
            from_start=self.from_start_var.get(),
            to_end=self.to_end_var.get()
        )

    def validate(self) -> tuple[bool, str]:
        """Validate the range configuration"""
        if not self.from_start_var.get() and not self.from_keyword_var.get().strip():
            return False, f"Range #{self.range_num}: Please specify 'From' keyword or select 'From document start'"

        if not self.to_end_var.get() and not self.to_keyword_var.get().strip():
            return False, f"Range #{self.range_num}: Please specify 'To' keyword or select 'To document end'"

        return True, ""


class SplitDocumentDialog(tk.Toplevel):
    """Dialog for configuring document split operations"""

    def __init__(self, parent, selected_files: List[str], theme_manager=None):
        super().__init__(parent)

        self.selected_files = selected_files
        self.result = None
        self.range_widgets: List[SplitRangeWidget] = []
        self.range_counter = 0
        self.theme_manager = theme_manager

        self.title("Split Documents")
        self.geometry("850x800")  # Increased height
        self.minsize(850, 700)  # Set minimum size to ensure buttons are visible
        self.resizable(True, True)  # Allow resizing

        # Make dialog modal
        self.transient(parent)
        self.grab_set()

        self._create_widgets()
        self._apply_theme()

        # Center on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def _create_widgets(self):
        """Create all dialog widgets"""
        # Main container with fixed structure
        outer_container = ttk.Frame(self)
        outer_container.pack(fill=tk.BOTH, expand=True)

        # Scrollable content area
        scroll_canvas = tk.Canvas(outer_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer_container, orient=tk.VERTICAL, command=scroll_canvas.yview)

        main_container = ttk.Frame(scroll_canvas, padding=15)

        # Configure scrolling
        main_container.bind(
            "<Configure>",
            lambda e: scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))
        )

        scroll_canvas.create_window((0, 0), window=main_container, anchor="nw")
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
        title_frame = ttk.Frame(main_container)
        title_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(title_frame, text="✂️ Split Document Configuration",
                 font=('TkDefaultFont', 14, 'bold')).pack(side=tk.LEFT)

        # File info
        info_text = f"Splitting {len(self.selected_files)} document(s)"
        ttk.Label(title_frame, text=info_text,
                 font=('TkDefaultFont', 9, 'italic')).pack(side=tk.RIGHT)

        # Split mode selection
        mode_frame = ttk.LabelFrame(main_container, text="Split Mode", padding=10)
        mode_frame.pack(fill=tk.X, pady=(0, 15))

        self.split_mode_var = tk.StringVar(value="keyword")

        ttk.Radiobutton(mode_frame, text="🔑 Split by keyword (DE/GIAI) - Default",
                       variable=self.split_mode_var, value="keyword",
                       command=self._on_mode_change).pack(anchor=tk.W, pady=2)

        ttk.Label(mode_frame, text="   Split before 'HƯỚNG DẪN GIẢI CHI TIẾT' keyword",
                 font=('TkDefaultFont', 8, 'italic'),
                 foreground='gray').pack(anchor=tk.W, padx=(20, 0))

        ttk.Radiobutton(mode_frame, text="✂️ Split in half (2 equal parts)",
                       variable=self.split_mode_var, value="half",
                       command=self._on_mode_change).pack(anchor=tk.W, pady=2)

        ttk.Radiobutton(mode_frame, text="🎯 Split by custom ranges (advanced)",
                       variable=self.split_mode_var, value="custom",
                       command=self._on_mode_change).pack(anchor=tk.W, pady=2)

        # Part selection frame (for keyword mode)
        self.part_selection_frame = ttk.LabelFrame(main_container, text="Parts to Save", padding=10)
        self.part_selection_frame.pack(fill=tk.X, pady=(0, 15))

        self.save_de_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.part_selection_frame, text="📄 Save Part 1 (DE - Before keyword)",
                       variable=self.save_de_var).pack(anchor=tk.W, pady=2)

        self.save_giai_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.part_selection_frame, text="📝 Save Part 2 (GIAI - From keyword to end)",
                       variable=self.save_giai_var).pack(anchor=tk.W, pady=2)

        # Options frame
        options_frame = ttk.LabelFrame(main_container, text="Split Options", padding=10)
        options_frame.pack(fill=tk.X, pady=(0, 15))

        self.remove_header_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="🚫 Remove headers",
                       variable=self.remove_header_var).pack(anchor=tk.W, pady=2)

        self.remove_footer_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="🚫 Remove footers",
                       variable=self.remove_footer_var).pack(anchor=tk.W, pady=2)

        self.remove_page_numbers_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="🚫 Remove page numbers",
                       variable=self.remove_page_numbers_var).pack(anchor=tk.W, pady=2)

        self.remove_first_shape_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="🚫 Remove first shape/watermark (keep sectPr)",
                       variable=self.remove_first_shape_var).pack(anchor=tk.W, pady=2)

        self.preserve_margins_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="📏 Preserve page margins from source document",
                       variable=self.preserve_margins_var).pack(anchor=tk.W, pady=2)

        # Custom ranges container (only visible in custom mode)
        self.ranges_container_frame = ttk.Frame(main_container)
        self.ranges_container_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Canvas with scrollbar for ranges
        canvas_frame = ttk.Frame(self.ranges_container_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.ranges_canvas = tk.Canvas(canvas_frame, highlightthickness=0, height=200)
        ranges_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL,
                                        command=self.ranges_canvas.yview)
        self.ranges_scrollable_frame = ttk.Frame(self.ranges_canvas)

        self.ranges_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.ranges_canvas.configure(scrollregion=self.ranges_canvas.bbox("all"))
        )

        self.ranges_canvas.create_window((0, 0), window=self.ranges_scrollable_frame, anchor="nw")
        self.ranges_canvas.configure(yscrollcommand=ranges_scrollbar.set)

        self.ranges_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ranges_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Add range button
        add_range_frame = ttk.Frame(self.ranges_container_frame)
        add_range_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(add_range_frame, text="➕ Add Range",
                  command=self._add_range).pack(side=tk.LEFT)

        ttk.Label(add_range_frame,
                 text="💡 Add multiple ranges to extract different sections",
                 font=('TkDefaultFont', 8, 'italic')).pack(side=tk.LEFT, padx=(10, 0))

        # Output directory selection
        output_frame = ttk.LabelFrame(main_container, text="Output Directory", padding=10)
        output_frame.pack(fill=tk.X, pady=(0, 15))

        output_dir_frame = ttk.Frame(output_frame)
        output_dir_frame.pack(fill=tk.X)

        self.output_dir_var = tk.StringVar(value=os.path.dirname(self.selected_files[0]) if self.selected_files else "")
        ttk.Entry(output_dir_frame, textvariable=self.output_dir_var,
                 width=60).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(output_dir_frame, text="📁 Browse",
                  command=self._browse_output_dir).pack(side=tk.RIGHT)

        # Fixed button bar at bottom (outside scrollable area)
        button_container = ttk.Frame(self, padding=(15, 10, 15, 15))
        button_container.pack(fill=tk.X, side=tk.BOTTOM)

        # Separator line
        ttk.Separator(button_container, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(0, 10))

        button_frame = ttk.Frame(button_container)
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="✂️ Split Documents",
                  command=self._on_split).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel",
                  command=self._on_cancel).pack(side=tk.RIGHT)

        # Initialize UI state
        self._on_mode_change()

    def _on_mode_change(self):
        """Handle split mode change"""
        mode = self.split_mode_var.get()

        if mode == "keyword":
            # Show part selection, hide custom ranges
            self.part_selection_frame.pack(fill=tk.X, pady=(0, 15))
            self.ranges_container_frame.pack_forget()
        elif mode == "half":
            # Hide both part selection and custom ranges
            self.part_selection_frame.pack_forget()
            self.ranges_container_frame.pack_forget()
        else:  # custom
            # Hide part selection, show custom ranges
            self.part_selection_frame.pack_forget()
            self.ranges_container_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
            # Add default range if none exist
            if not self.range_widgets:
                self._add_range()

    def _add_range(self):
        """Add a new range widget"""
        self.range_counter += 1
        range_widget = SplitRangeWidget(self.ranges_scrollable_frame,
                                       self.range_counter,
                                       self._remove_range)
        range_widget.pack(fill=tk.X, pady=(0, 10), padx=5)
        self.range_widgets.append(range_widget)

        # Scroll to bottom
        self.ranges_canvas.update_idletasks()
        self.ranges_canvas.yview_moveto(1.0)

    def _remove_range(self, widget: SplitRangeWidget):
        """Remove a range widget"""
        if len(self.range_widgets) == 1:
            messagebox.showwarning("Cannot Remove",
                                  "At least one range is required for custom split mode")
            return

        widget.pack_forget()
        widget.destroy()
        self.range_widgets.remove(widget)

        # Renumber remaining ranges
        for i, w in enumerate(self.range_widgets, 1):
            w.range_num = i
            # Update label
            for child in w.winfo_children():
                if isinstance(child, ttk.Frame):
                    for label in child.winfo_children():
                        if isinstance(label, ttk.Label) and label.cget('text').startswith('📄'):
                            label.config(text=f"📄 Range #{i}")
                            break
                    break

    def _browse_output_dir(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.output_dir_var.get()
        )
        if directory:
            self.output_dir_var.set(directory)

    def _validate_configuration(self) -> tuple[bool, str]:
        """Validate the split configuration"""
        mode = self.split_mode_var.get()

        if mode == "custom":
            if not self.range_widgets:
                return False, "Please add at least one split range"

            # Validate each range
            for widget in self.range_widgets:
                valid, error = widget.validate()
                if not valid:
                    return False, error

        # Validate output directory
        output_dir = self.output_dir_var.get()
        if not output_dir:
            return False, "Please specify an output directory"

        if not os.path.exists(output_dir):
            return False, f"Output directory does not exist: {output_dir}"

        return True, ""

    def _on_split(self):
        """Handle split button click"""
        mode = self.split_mode_var.get()

        # Validate keyword mode part selection
        if mode == "keyword":
            if not self.save_de_var.get() and not self.save_giai_var.get():
                messagebox.showerror("Validation Error", "Please select at least one part to save")
                return

        # Validate configuration
        valid, error = self._validate_configuration()
        if not valid:
            messagebox.showerror("Validation Error", error)
            return

        # Prepare result
        self.result = {
            'mode': mode,
            'options': {
                'remove_header': self.remove_header_var.get(),
                'remove_footer': self.remove_footer_var.get(),
                'remove_page_numbers': self.remove_page_numbers_var.get(),
                'remove_first_shape': self.remove_first_shape_var.get(),
                'preserve_margins': self.preserve_margins_var.get()
            },
            'part_selection': {
                'save_de': self.save_de_var.get() if mode == 'keyword' else True,
                'save_giai': self.save_giai_var.get() if mode == 'keyword' else True
            },
            'keyword': 'HƯỚNG DẪN GIẢI CHI TIẾT' if mode == 'keyword' else None,
            'ranges': [widget.get_range() for widget in self.range_widgets] if mode == 'custom' else [],
            'output_dir': self.output_dir_var.get(),
            'files': self.selected_files
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

    def _apply_theme(self):
        """Apply theme colors to dialog widgets"""
        if not self.theme_manager:
            return

        try:
            theme = self.theme_manager.current_theme

            # Configure dialog background
            self.configure(bg=theme['bg'])

            # Create custom style for this dialog
            style = ttk.Style(self)

            # Configure Radiobutton style
            style.configure('Dialog.TRadiobutton',
                          background=theme['bg'],
                          foreground=theme['fg'])
            style.map('Dialog.TRadiobutton',
                     background=[('active', theme['hover'])],
                     foreground=[('active', theme['fg'])])

            # Configure Checkbutton style
            style.configure('Dialog.TCheckbutton',
                          background=theme['bg'],
                          foreground=theme['fg'])
            style.map('Dialog.TCheckbutton',
                     background=[('active', theme['hover'])],
                     foreground=[('active', theme['fg'])])

            # Configure Label style
            style.configure('Dialog.TLabel',
                          background=theme['bg'],
                          foreground=theme['fg'])

            # Configure LabelFrame style
            style.configure('Dialog.TLabelframe',
                          background=theme['bg'],
                          foreground=theme['fg'],
                          bordercolor=theme['border'])
            style.configure('Dialog.TLabelframe.Label',
                          background=theme['bg'],
                          foreground=theme['fg'])

            # Configure Frame style
            style.configure('Dialog.TFrame',
                          background=theme['bg'])

            # Configure Button style
            style.configure('Dialog.TButton',
                          background=theme['button_bg'],
                          foreground=theme['button_fg'],
                          bordercolor=theme['border'])
            style.map('Dialog.TButton',
                     background=[('active', theme['button_active_bg'])],
                     foreground=[('active', theme['button_fg'])])

            # Configure Entry style
            style.configure('Dialog.TEntry',
                          fieldbackground=theme['input_bg'],
                          foreground=theme['input_fg'],
                          bordercolor=theme['border'])

            # Configure canvas background
            if hasattr(self, 'ranges_canvas'):
                self.ranges_canvas.configure(bg=theme['bg'], highlightbackground=theme['border'])

            # Apply styles to existing widgets
            self._apply_styles_to_widgets(self)

        except Exception as e:
            print(f"Error applying theme to split dialog: {e}")

    def _apply_styles_to_widgets(self, widget):
        """Recursively apply Dialog styles to all ttk widgets"""
        try:
            # Apply appropriate style based on widget type
            widget_class = widget.winfo_class()

            if widget_class == 'TRadiobutton':
                widget.configure(style='Dialog.TRadiobutton')
            elif widget_class == 'TCheckbutton':
                widget.configure(style='Dialog.TCheckbutton')
            elif widget_class == 'TLabel':
                widget.configure(style='Dialog.TLabel')
            elif widget_class == 'TLabelframe':
                widget.configure(style='Dialog.TLabelframe')
            elif widget_class == 'TFrame':
                widget.configure(style='Dialog.TFrame')
            elif widget_class == 'TButton':
                widget.configure(style='Dialog.TButton')
            elif widget_class == 'TEntry':
                widget.configure(style='Dialog.TEntry')

            # Recursively apply to children
            for child in widget.winfo_children():
                self._apply_styles_to_widgets(child)

        except Exception as e:
            # Silently ignore widgets that don't support styling
            pass


def show_split_dialog(parent, selected_files: List[str], theme_manager=None) -> Optional[Dict]:
    """
    Show split document dialog

    Args:
        parent: Parent window
        selected_files: List of file paths to split
        theme_manager: Theme manager instance for styling

    Returns:
        Configuration dict if user clicked Split, None if cancelled
    """
    dialog = SplitDocumentDialog(parent, selected_files, theme_manager)
    parent.wait_window(dialog)
    return dialog.result

