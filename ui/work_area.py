"""
Work Area UI Component
Main content area that displays file lists, previews, and operation results.
"""
import tkinter as tk
from tkinter import ttk
from .thread_monitor_panel import ThreadMonitorPanel


class WorkArea(ttk.Frame):
    """Work area controller - main content display area"""

    def __init__(self, parent, main_window):
        """
        Initialize work area

        Args:
            parent: Parent window
            main_window: Reference to MainWindow instance
        """
        super().__init__(parent)
        self.main_window = main_window

        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create tabs
        self._create_file_browser_tab()
        self._create_operations_tab()
        self._create_thread_monitor_tab()
        self._create_results_tab()

        # Register for theme updates
        self.main_window.theme_manager.register_callback(self._apply_theme)

    def _apply_theme(self):
        """Apply theme to work area widgets"""
        try:
            theme = self.main_window.theme_manager.current_theme

            # Update preview text widget if it exists
            if hasattr(self, 'preview_text'):
                self.preview_text.configure(
                    background=theme['input_bg'],
                    foreground=theme['fg'],
                    insertbackground=theme['fg'],
                    selectbackground=theme['select_bg'],
                    selectforeground=theme['select_fg']
                )

            # Update results text widget if it exists
            if hasattr(self, 'results_text'):
                self.results_text.configure(
                    background=theme['input_bg'],
                    foreground=theme['fg'],
                    insertbackground=theme['fg'],
                    selectbackground=theme['select_bg'],
                    selectforeground=theme['select_fg']
                )

            # Update PanedWindow sash if file browser tab exists
            if hasattr(self, 'file_browser_paned'):
                try:
                    self.file_browser_paned.tk.call('ttk::style', 'configure', 'Sash',
                                                    '-background', theme['sash_bg'],
                                                    '-sashthickness', 4,
                                                    '-sashrelief', 'flat')
                except:
                    pass

            # Update operations paned window sash
            if hasattr(self, 'ops_paned'):
                try:
                    self.ops_paned.tk.call('ttk::style', 'configure', 'Sash',
                                           '-background', theme['sash_bg'],
                                           '-sashthickness', 4,
                                           '-sashrelief', 'flat')
                except:
                    pass
        except Exception as e:
            print(f"WorkArea theme apply error: {e}")

    def _create_file_browser_tab(self):
        """Create file browser tab"""
        file_frame = ttk.Frame(self.notebook)
        self.notebook.add(file_frame, text="File Browser")

        # Create paned window for split view
        paned = ttk.PanedWindow(file_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Store reference for theme updates
        self.file_browser_paned = paned

        # Configure sash appearance
        try:
            theme = self.main_window.theme_manager.current_theme
            paned.configure(
                style='TPanedwindow'
            )
            # Set sash color via options
            paned.tk.call('ttk::style', 'configure', 'Sash',
                         '-background', theme['sash_bg'],
                         '-sashthickness', 4,
                         '-sashrelief', 'flat')
        except Exception as e:
            print(f"Sash config error: {e}")

        # Left side - file tree
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)

        ttk.Label(left_frame, text="Files:").pack(anchor=tk.W, padx=5, pady=5)

        # Create file tree
        self.file_tree = ttk.Treeview(left_frame, columns=("Size", "Type"), show="tree headings")
        self.file_tree.heading("#0", text="Name")
        self.file_tree.heading("Size", text="Size")
        self.file_tree.heading("Type", text="Type")
        self.file_tree.column("Size", width=100)
        self.file_tree.column("Type", width=100)

        # Add scrollbars
        tree_scroll_y = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        tree_scroll_x = ttk.Scrollbar(left_frame, orient=tk.HORIZONTAL, command=self.file_tree.xview)
        self.file_tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)

        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Right side - preview
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=1)

        ttk.Label(right_frame, text="Preview:").pack(anchor=tk.W, padx=5, pady=5)

        # Preview text area
        theme = self.main_window.theme_manager.current_theme
        self.preview_text = tk.Text(right_frame, wrap=tk.WORD,
                                    background=theme['input_bg'],
                                    foreground=theme['fg'],
                                    insertbackground=theme['fg'],
                                    selectbackground=theme['select_bg'],
                                    selectforeground=theme['select_fg'])
        preview_scroll = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=preview_scroll.set)

        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preview_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def _create_operations_tab(self):
        """Create operations tab with file selection and operations"""
        from logic.file_selection_manager import get_file_selection_manager
        from tkinter import filedialog

        self.file_manager = get_file_selection_manager()

        ops_frame = ttk.Frame(self.notebook)
        self.notebook.add(ops_frame, text="📋 Operations")

        # Create paned window to split work zone into 2 parts
        self.ops_paned = ttk.PanedWindow(ops_frame, orient=tk.HORIZONTAL)
        self.ops_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # LEFT PART: File Selection
        selection_container = ttk.Frame(self.ops_paned)
        self.ops_paned.add(selection_container, weight=3)

        # File selection section with modern styling
        selection_frame = ttk.LabelFrame(selection_container, text="📁 File Selection", padding=15)
        selection_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Buttons for file selection with modern layout
        btn_container = ttk.Frame(selection_frame)
        btn_container.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(btn_container, text="📁 Add Files",
                  command=self._add_files, width=15).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btn_container, text="🗑️ Clear All",
                  command=self._clear_files, width=15).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btn_container, text="❌ Remove Selected",
                  command=self._remove_selected_files, width=18).pack(side=tk.LEFT)

        # Selection info label with modern styling
        info_container = ttk.Frame(selection_frame)
        info_container.pack(fill=tk.X, pady=(0, 8))

        self.selection_info_label = ttk.Label(info_container, text="No files selected",
                                             relief=tk.FLAT, padding=8,
                                             font=('TkDefaultFont', 9, 'bold'))
        self.selection_info_label.pack(fill=tk.X)

        # Instruction label with modern styling
        instruction_label = ttk.Label(selection_frame,
                                     text="💡 Tip: Use Ctrl+Click to select multiple files, Shift+Click for range",
                                     font=('TkDefaultFont', 8, 'italic'))
        instruction_label.pack(anchor=tk.W, pady=(0, 8))

        # File list with reorder buttons
        list_container = ttk.Frame(selection_frame)
        list_container.pack(fill=tk.BOTH, expand=True)

        # Left side - Treeview for files
        tree_container = ttk.Frame(list_container)
        tree_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        columns = ('type', 'size')
        self.file_listbox = ttk.Treeview(tree_container, columns=columns,
                                         show='tree headings', selectmode='extended')

        self.file_listbox.heading('#0', text='File Name')
        self.file_listbox.heading('type', text='Type')
        self.file_listbox.heading('size', text='Size')

        self.file_listbox.column('#0', width=400)
        self.file_listbox.column('type', width=80)
        self.file_listbox.column('size', width=100)

        # Scrollbars
        vsb = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.file_listbox.yview)
        hsb = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.file_listbox.xview)
        self.file_listbox.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.file_listbox.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        # Right side - Reorder buttons
        reorder_frame = ttk.Frame(list_container)
        reorder_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))

        ttk.Label(reorder_frame, text="Reorder", font=('TkDefaultFont', 9, 'bold')).pack(pady=(0, 5))

        self.btn_move_top = ttk.Button(reorder_frame, text="⏫ Top", width=10,
                                       command=self._move_to_top)
        self.btn_move_top.pack(pady=2)

        self.btn_move_up = ttk.Button(reorder_frame, text="⬆️ Move Up", width=10,
                                      command=self._move_up)
        self.btn_move_up.pack(pady=2)

        self.btn_move_down = ttk.Button(reorder_frame, text="⬇️ Move Down", width=10,
                                        command=self._move_down)
        self.btn_move_down.pack(pady=2)

        self.btn_move_bottom = ttk.Button(reorder_frame, text="⏬ Bottom", width=10,
                                          command=self._move_to_bottom)
        self.btn_move_bottom.pack(pady=2)

        ttk.Separator(reorder_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        ttk.Label(reorder_frame, text="💡 Tip:\nSelect file(s)\nthen click\nbuttons to\nreorder",
                 justify=tk.CENTER, foreground='gray', font=('TkDefaultFont', 8)).pack()

        # RIGHT PART: Operations
        operations_container = ttk.Frame(self.ops_paned)
        self.ops_paned.add(operations_container, weight=2)

        # Operations section with modern styling
        ops_section = ttk.LabelFrame(operations_container, text="⚡ Available Operations", padding=15)
        ops_section.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Split operation section
        split_section = ttk.LabelFrame(ops_section, text="✂️ Split Documents", padding=10)
        split_section.pack(fill=tk.X, pady=(0, 15))

        split_desc = ttk.Label(split_section,
                              text="Split documents into multiple parts based on keywords or equal halves",
                              wraplength=280, justify=tk.LEFT,
                              font=('TkDefaultFont', 8))
        split_desc.pack(anchor=tk.W, pady=(0, 8))

        self.btn_split = ttk.Button(split_section, text="✂️ Configure Split",
                                    command=self._on_split, state='disabled', width=25)
        self.btn_split.pack(fill=tk.X)

        # Merge operation section
        merge_section = ttk.LabelFrame(ops_section, text="🔗 Merge Documents", padding=10)
        merge_section.pack(fill=tk.X, pady=(0, 15))

        merge_desc = ttk.Label(merge_section,
                              text="Combine multiple documents into a single file",
                              wraplength=280, justify=tk.LEFT,
                              font=('TkDefaultFont', 8))
        merge_desc.pack(anchor=tk.W, pady=(0, 8))

        self.btn_merge = ttk.Button(merge_section, text="🔗 Merge Documents",
                                    command=self._on_merge, state='disabled', width=25)
        self.btn_merge.pack(fill=tk.X)

        # Export PDF operation section
        pdf_section = ttk.LabelFrame(ops_section, text="📄 Export to PDF", padding=10)
        pdf_section.pack(fill=tk.X, pady=(0, 15))

        pdf_desc = ttk.Label(pdf_section,
                            text="Convert selected documents to PDF format",
                            wraplength=280, justify=tk.LEFT,
                            font=('TkDefaultFont', 8))
        pdf_desc.pack(anchor=tk.W, pady=(0, 8))

        self.btn_export_pdf = ttk.Button(pdf_section, text="📄 Export to PDF",
                                        command=self._on_export_pdf, state='disabled', width=25)
        self.btn_export_pdf.pack(fill=tk.X)

        # Rename operation section
        rename_section = ttk.LabelFrame(ops_section, text="📝 Rename Files", padding=10)
        rename_section.pack(fill=tk.X, pady=(0, 15))

        rename_desc = ttk.Label(rename_section,
                               text="Batch rename files with custom patterns",
                               wraplength=280, justify=tk.LEFT,
                               font=('TkDefaultFont', 8))
        rename_desc.pack(anchor=tk.W, pady=(0, 8))

        self.btn_rename = ttk.Button(rename_section, text="📝 Rename Files",
                                     command=self._on_rename, state='disabled', width=25)
        self.btn_rename.pack(fill=tk.X)

        # Help text with modern styling
        help_frame = ttk.Frame(ops_section)
        help_frame.pack(fill=tk.X, pady=(10, 0))

        help_text = "💡 Select DOCX files to enable split, merge, and export operations. All file types support renaming."
        ttk.Label(help_frame, text=help_text, wraplength=280,
                 font=('TkDefaultFont', 8, 'italic')).pack(pady=5)

    def _add_files(self):
        """Add files to selection"""
        from tkinter import filedialog

        files = filedialog.askopenfilenames(
            title="Select Files (Ctrl+Click for multiple)",
            filetypes=[
                ("Supported Files", "*.docx *.pdf"),
                ("Word Documents", "*.docx"),
                ("PDF Files", "*.pdf"),
                ("All Files", "*.*")
            ]
        )

        if files:
            info = self.file_manager.add_files(list(files))
            self._update_file_list()
            self._update_button_states()
            self._update_selection_info(info)

    def _clear_files(self):
        """Clear all selected files"""
        self.file_manager.clear_selection()
        self._update_file_list()
        self._update_button_states()
        self._update_selection_info(None)

    def _remove_selected_files(self):
        """Remove selected files from list"""
        selection = self.file_listbox.selection()
        if not selection:
            return

        # Get file paths from selection
        files_to_remove = []
        for item_id in selection:
            file_path = self.file_listbox.set(item_id, '#0')
            # Find full path from file manager
            for file_info in self.file_manager.get_all_files_info():
                if file_info['name'] == file_path:
                    files_to_remove.append(file_info['path'])
                    break

        if files_to_remove:
            info = self.file_manager.remove_files(files_to_remove)
            self._update_file_list()
            self._update_button_states()
            self._update_selection_info(info)

    def _update_file_list(self):
        """Update the file list display"""
        # Clear current list
        for item in self.file_listbox.get_children():
            self.file_listbox.delete(item)

        # Add files
        for file_info in self.file_manager.get_all_files_info():
            # Format size
            size = file_info['size']
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024 * 1024:
                size_str = f"{size / 1024:.1f} KB"
            else:
                size_str = f"{size / (1024 * 1024):.1f} MB"

            # Color code by type
            file_type = file_info['type']
            tag = f"type_{file_type}"

            self.file_listbox.insert('', 'end',
                                    text=file_info['name'],
                                    values=(file_type.upper(), size_str),
                                    tags=(tag,))

        # Configure tags for coloring
        self.file_listbox.tag_configure('type_docx', foreground='blue')
        self.file_listbox.tag_configure('type_pdf', foreground='red')

    def _update_button_states(self):
        """Update operation button states based on selection"""
        states = self.file_manager.get_operation_button_state()

        self.btn_split['state'] = 'normal' if states['split'] else 'disabled'
        self.btn_merge['state'] = 'normal' if states['merge'] else 'disabled'
        self.btn_export_pdf['state'] = 'normal' if states['export_pdf'] else 'disabled'
        self.btn_rename['state'] = 'normal' if states['rename'] else 'disabled'

    def _update_selection_info(self, info):
        """Update selection info label"""
        if info is None:
            self.selection_info_label.config(text="No files selected")
        else:
            summary = self.file_manager.get_selection_summary()
            self.selection_info_label.config(text=summary)

    def _on_split(self):
        """Handle split button click"""
        from logic.file_selection_manager import FileOperation
        from ui.dialogs.split_document_dialog import show_split_dialog
        from logic.split.document_splitter import split_documents_worker_simple

        valid, message = self.file_manager.validate_for_operation(FileOperation.SPLIT)
        if not valid:
            from tkinter import messagebox
            messagebox.showwarning("Cannot Split", message)
            return

        # Get selected files
        selected_files = self.file_manager.selected_files.copy()

        # Show split dialog
        result = show_split_dialog(self, selected_files, self.main_window.theme_manager)

        if result:
            # User confirmed split operation
            files = result['files']
            num_files = len(files)
            self.main_window.set_status(f"Starting split operation for {num_files} file(s)...", "info")

            # Log the configuration
            self.add_log_message(f"\n=== Split Operation Started ===")
            self.add_log_message(f"Mode: {result['mode']}")
            self.add_log_message(f"Files: {num_files}")
            self.add_log_message(f"Output: {result['output_dir']}")

            if result['ranges']:
                self.add_log_message(f"Custom ranges: {len(result['ranges'])}")

            # Determine number of threads (for 3+ files, use multi-threading)
            if num_files > 2:
                num_threads = min(4, num_files)
                self.add_log_message(f"Using {num_threads} worker threads for parallel processing")

                # Create multiple worker threads with files distributed equally
                thread_ids = self.main_window.thread_manager.create_worker_threads(
                    files=files,
                    task_type="Splitting",
                    worker_func=split_documents_worker_simple,
                    config=result,
                    num_threads=num_threads
                )

                # Start all threads
                for thread_id in thread_ids:
                    self.main_window.thread_manager.start_thread(thread_id)
                    thread = self.main_window.thread_manager.get_thread(thread_id)
                    self.add_log_message(f"Started {thread.display_name} with {thread.total_tasks} files")

            else:
                # For 1-2 files, use single thread
                self.add_log_message("Using single worker thread")
                thread_ids = self.main_window.thread_manager.create_worker_threads(
                    files=files,
                    task_type="Splitting",
                    worker_func=split_documents_worker_simple,
                    config=result,
                    num_threads=1
                )
                self.main_window.thread_manager.start_thread(thread_ids[0])

            self.add_log_message("Check Thread Monitor tab for progress")

            # Switch to thread monitor tab to show progress
            self.notebook.select(2)  # Thread Monitor is the 3rd tab (index 2)

        else:
            self.main_window.set_status("Split operation cancelled", "info")

    def _on_merge(self):
        """Handle merge button click"""
        from logic.file_selection_manager import FileOperation
        from ui.dialogs.merge_document_dialog import show_merge_dialog
        from logic.merge.document_merger import merge_documents_worker

        valid, message = self.file_manager.validate_for_operation(FileOperation.MERGE)
        if not valid:
            from tkinter import messagebox
            messagebox.showwarning("Cannot Merge", message)
            return

        # Get selected files
        selected_files = self.file_manager.selected_files.copy()

        # Show merge dialog
        result = show_merge_dialog(self, selected_files, self.main_window.theme_manager)

        if result:
            # User confirmed merge operation
            files = result['files']
            num_files = len(files)
            self.main_window.set_status(f"Starting merge operation for {num_files} file(s)...", "info")

            # Log the configuration
            self.add_log_message(f"\n=== Merge Operation Started ===")
            self.add_log_message(f"Files: {num_files}")
            self.add_log_message(f"Output: {result['output_path']}")
            self.add_log_message(f"Filename: {result['output_name']}")

            # Create a single worker thread for merging
            # (Merging is done sequentially, no benefit from multi-threading)
            self.add_log_message("Creating merge worker thread")

            thread_ids = self.main_window.thread_manager.create_worker_threads(
                files=files,
                task_type="Merging",
                worker_func=merge_documents_worker,
                config=result,
                num_threads=1
            )

            # Start the thread
            self.main_window.thread_manager.start_thread(thread_ids[0])
            thread = self.main_window.thread_manager.get_thread(thread_ids[0])
            self.add_log_message(f"Started {thread.display_name} with {num_files} files")
            self.add_log_message("Check Thread Monitor tab for progress")

            # Switch to thread monitor tab to show progress
            self.notebook.select(2)  # Thread Monitor is the 3rd tab (index 2)

        else:
            self.main_window.set_status("Merge operation cancelled", "info")

    def _on_export_pdf(self):
        """Handle export to PDF button click"""
        from logic.file_selection_manager import FileOperation
        from ui.dialogs.export_pdf_dialog import show_export_pdf_dialog
        from logic.export.pdf_exporter import export_to_pdf_worker

        valid, message = self.file_manager.validate_for_operation(FileOperation.EXPORT_PDF)
        if not valid:
            from tkinter import messagebox
            messagebox.showwarning("Cannot Export", message)
            return

        # Show export dialog
        config = show_export_pdf_dialog(self, self.file_manager.selected_files, self.main_window.theme_manager)

        if not config:
            # User cancelled
            return

        # Get files to export
        files = config['files']
        output_dir = config['output_dir']
        num_files = len(files)

        # Determine number of threads based on file count
        if num_files <= 2:
            num_threads = 1
        elif num_files <= 5:
            num_threads = 2
        elif num_files <= 10:
            num_threads = 3
        else:
            num_threads = 4  # Max 4 threads for PDF export

        # Create worker threads using thread manager
        # The thread manager will automatically distribute files among threads
        thread_ids = self.main_window.thread_manager.create_worker_threads(
            files=files,
            task_type="PDF Export",
            worker_func=export_to_pdf_worker,
            config={'output_dir': output_dir},
            num_threads=num_threads,
            priority=1
        )

        # Start all threads
        for thread_id in thread_ids:
            self.main_window.thread_manager.start_thread(thread_id)

        self.main_window.set_status(f"Exporting {num_files} file(s) to PDF using {len(thread_ids)} thread(s)...", "info")

        # Add log messages
        self.add_log_message(f"Starting PDF export: {num_files} files using {len(thread_ids)} threads")
        for i, thread_id in enumerate(thread_ids, 1):
            thread = self.main_window.thread_manager.get_thread(thread_id)
            self.add_log_message(f"Started {thread.display_name} with {len(thread.assigned_files)} files")
        self.add_log_message("Check Thread Monitor tab for progress")

        # Switch to thread monitor tab to show progress
        self.notebook.select(2)  # Thread Monitor is the 3rd tab (index 2)

    def _on_rename(self):
        """Handle rename button click"""
        from logic.file_selection_manager import FileOperation

        valid, message = self.file_manager.validate_for_operation(FileOperation.RENAME)
        if not valid:
            from tkinter import messagebox
            messagebox.showwarning("Cannot Rename", message)
            return

        # TODO: Open rename dialog with selected files
        self.main_window.set_status(f"Rename: {message}", "info")
        print("Rename operation:", self.file_manager.selected_files)

    def _move_up(self):
        """Move selected file(s) up in the list"""
        selection = self.file_listbox.selection()
        if not selection:
            return

        # Get all items and their current order
        all_items = self.file_listbox.get_children()

        # For each selected item, move it up if possible
        moved = False
        for item_id in selection:
            idx = all_items.index(item_id)
            if idx > 0:
                # Move up by reordering files in manager
                self._swap_files_at_indices(idx, idx - 1)
                moved = True

        if moved:
            self._refresh_list_and_reselect(selection)

    def _move_down(self):
        """Move selected file(s) down in the list"""
        selection = self.file_listbox.selection()
        if not selection:
            return

        all_items = self.file_listbox.get_children()

        # Process in reverse to maintain relative positions
        moved = False
        for item_id in reversed(selection):
            idx = all_items.index(item_id)
            if idx < len(all_items) - 1:
                self._swap_files_at_indices(idx, idx + 1)
                moved = True

        if moved:
            self._refresh_list_and_reselect(selection)

    def _move_to_top(self):
        """Move selected file(s) to the top of the list"""
        selection = self.file_listbox.selection()
        if not selection:
            return

        # Get selected file paths
        selected_files = []
        for item_id in selection:
            file_name = self.file_listbox.item(item_id, 'text')
            for file_info in self.file_manager.get_all_files_info():
                if file_info['name'] == file_name:
                    selected_files.append(file_info['path'])
                    break

        if not selected_files:
            return

        # Reorder: selected files first, then others
        all_files = self.file_manager.selected_files.copy()
        other_files = [f for f in all_files if f not in selected_files]
        new_order = selected_files + other_files

        self.file_manager.selected_files = new_order
        self._refresh_list_and_reselect(selection)

    def _move_to_bottom(self):
        """Move selected file(s) to the bottom of the list"""
        selection = self.file_listbox.selection()
        if not selection:
            return

        # Get selected file paths
        selected_files = []
        for item_id in selection:
            file_name = self.file_listbox.item(item_id, 'text')
            for file_info in self.file_manager.get_all_files_info():
                if file_info['name'] == file_name:
                    selected_files.append(file_info['path'])
                    break

        if not selected_files:
            return

        # Reorder: others first, then selected files
        all_files = self.file_manager.selected_files.copy()
        other_files = [f for f in all_files if f not in selected_files]
        new_order = other_files + selected_files

        self.file_manager.selected_files = new_order
        self._refresh_list_and_reselect(selection)

    def _swap_files_at_indices(self, idx1, idx2):
        """Swap two files at given indices"""
        files = self.file_manager.selected_files
        files[idx1], files[idx2] = files[idx2], files[idx1]

    def _refresh_list_and_reselect(self, old_selection):
        """Refresh the file list and try to maintain selection"""
        # Get file names from old selection
        selected_names = []
        for item_id in old_selection:
            try:
                name = self.file_listbox.item(item_id, 'text')
                selected_names.append(name)
            except:
                pass

        # Refresh the list
        self._update_file_list()

        # Reselect items by name
        for item_id in self.file_listbox.get_children():
            name = self.file_listbox.item(item_id, 'text')
            if name in selected_names:
                self.file_listbox.selection_add(item_id)

    def _create_thread_monitor_tab(self):
        """Create thread monitor tab"""
        thread_frame = ttk.Frame(self.notebook)
        self.notebook.add(thread_frame, text="Thread Monitor")

        # Create enhanced thread monitor panel
        from ui.thread_monitor_enhanced import EnhancedThreadMonitorPanel
        self.thread_monitor = EnhancedThreadMonitorPanel(thread_frame, self.main_window.thread_manager)
        self.thread_monitor.pack(fill=tk.BOTH, expand=True)

    def _create_results_tab(self):
        """Create results/log tab"""
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="Results & Log")

        ttk.Label(results_frame, text="Operation Results:").pack(anchor=tk.W, padx=5, pady=5)

        # Results text area with scrollbar
        theme = self.main_window.theme_manager.current_theme
        self.results_text = tk.Text(results_frame, wrap=tk.WORD, height=10,
                                    background=theme['input_bg'],
                                    foreground=theme['fg'],
                                    insertbackground=theme['fg'],
                                    selectbackground=theme['select_bg'],
                                    selectforeground=theme['select_fg'])
        results_scroll = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=results_scroll.set)

        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        results_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # Add initial message
        self.results_text.insert(tk.END, "Welcome to Mink Mink!\n")
        self.results_text.insert(tk.END, "Operation results will appear here.\n\n")
        self.results_text.config(state=tk.DISABLED)

    def add_log_message(self, message):
        """
        Add a message to the results log

        Args:
            message: Message to add to log
        """
        self.results_text.config(state=tk.NORMAL)
        self.results_text.insert(tk.END, f"{message}\n")
        self.results_text.see(tk.END)
        self.results_text.config(state=tk.DISABLED)

