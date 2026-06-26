"""
Thread Monitor Panel
UI component for monitoring and managing worker threads.
"""
import tkinter as tk
from tkinter import ttk
import os
from typing import Optional, Dict
from thread.thread_manager import ThreadManager, WorkerThread, ThreadStatus


class ThreadMonitorPanel(ttk.Frame):
    """Panel for monitoring worker threads"""

    def __init__(self, parent, thread_manager: ThreadManager):
        """
        Initialize thread monitor panel

        Args:
            parent: Parent widget
            thread_manager: ThreadManager instance
        """
        super().__init__(parent)
        self.thread_manager = thread_manager
        self.selected_thread_id = None
        self.selected_file_item = None

        # Store file order and keep track of items
        self.file_items_map: Dict[str, str] = {}  # file_path -> item_id
        self.file_order = []  # stable ordered list of file paths

        # Get theme manager reference
        try:
            self.theme_manager = parent.master.master.theme_manager if hasattr(parent.master.master, 'theme_manager') else None
        except:
            self.theme_manager = None

        # Create UI
        self._create_ui()

        # Start update loop
        self._update_display()

    def _create_ui(self):
        """Create the UI components"""
        # Main container with paned window for 60/40 split
        main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # LEFT SIDE (60%): Thread monitoring
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=60)

        # Overall progress section
        overall_frame = ttk.LabelFrame(left_frame, text="Overall Progress", padding=10)
        overall_frame.pack(fill=tk.X, pady=(0, 10))

        self.overall_progress = ttk.Progressbar(overall_frame, mode='determinate', length=400)
        self.overall_progress.pack(fill=tk.X)

        self.overall_label = ttk.Label(overall_frame, text="0 active / 0 total | 0% complete")
        self.overall_label.pack(pady=(5, 0))

        # Thread list section
        list_frame = ttk.LabelFrame(left_frame, text="Active Threads", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Create treeview for threads
        columns = ('status', 'task', 'current_file', 'progress')
        self.thread_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', height=8)

        self.thread_tree.heading('#0', text='Thread Name')
        self.thread_tree.heading('status', text='Status')
        self.thread_tree.heading('task', text='Current Task')
        self.thread_tree.heading('current_file', text='Current File')
        self.thread_tree.heading('progress', text='Progress')

        self.thread_tree.column('#0', width=150)
        self.thread_tree.column('status', width=100)
        self.thread_tree.column('task', width=150)
        self.thread_tree.column('current_file', width=180)
        self.thread_tree.column('progress', width=80)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.thread_tree.yview)
        self.thread_tree.configure(yscrollcommand=scrollbar.set)

        self.thread_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind events
        self.thread_tree.bind('<Double-Button-1>', self._on_thread_double_click)
        self.thread_tree.bind('<<TreeviewSelect>>', self._on_selection_changed)

        # Thread Control section with progress bars
        control_frame = ttk.LabelFrame(left_frame, text="Thread Control", padding=10)
        control_frame.pack(fill=tk.X)

        # Create two columns: left for buttons, right for progress bars
        button_column = ttk.Frame(control_frame)
        button_column.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))

        progress_column = ttk.Frame(control_frame)
        progress_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Left column: Buttons
        ttk.Label(button_column, text="Actions:", font=('TkDefaultFont', 9, 'bold')).pack(anchor=tk.W, pady=(0, 5))

        btn_row1 = ttk.Frame(button_column)
        btn_row1.pack(fill=tk.X, pady=(0, 3))

        self.btn_view_logs = ttk.Button(btn_row1, text="📋 View Logs",
                                        command=self._view_thread_logs)
        self.btn_view_logs.pack(side=tk.LEFT, padx=(0, 5))
        self.btn_view_logs.state(['disabled'])

        self.btn_stop = ttk.Button(btn_row1, text="⏹️ Stop Thread",
                                   command=self._stop_thread)
        self.btn_stop.pack(side=tk.LEFT)
        self.btn_stop.state(['disabled'])

        btn_row2 = ttk.Frame(button_column)
        btn_row2.pack(fill=tk.X, pady=(0, 3))

        ttk.Button(btn_row2, text="🧹 Cleanup",
                  command=self._cleanup_completed).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(btn_row2, text="⏸️ Stop All",
                  command=self._stop_all).pack(side=tk.LEFT)

        btn_row3 = ttk.Frame(button_column)
        btn_row3.pack(fill=tk.X)

        ttk.Button(btn_row3, text="🛑 Stop All & Release",
                  command=self._stop_all_and_release).pack(side=tk.LEFT)

        # Right column: Progress bars for selected thread
        ttk.Label(progress_column, text="Selected Thread Progress:", font=('TkDefaultFont', 9, 'bold')).pack(anchor=tk.W, pady=(0, 5))

        # Main Progress
        progress_container1 = ttk.Frame(progress_column)
        progress_container1.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(progress_container1, text="Main:").pack(side=tk.LEFT, padx=(0, 5))
        self.selected_progress = ttk.Progressbar(progress_container1, mode='determinate', length=200)
        self.selected_progress.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.selected_progress_label = ttk.Label(progress_container1, text="0%", width=6)
        self.selected_progress_label.pack(side=tk.LEFT, padx=(5, 0))

        # Sub-progress
        progress_container2 = ttk.Frame(progress_column)
        progress_container2.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(progress_container2, text="Sub:").pack(side=tk.LEFT, padx=(0, 5))
        self.selected_sub_progress = ttk.Progressbar(progress_container2, mode='determinate', length=200)
        self.selected_sub_progress.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.selected_sub_progress_label = ttk.Label(progress_container2, text="0%", width=6)
        self.selected_sub_progress_label.pack(side=tk.LEFT, padx=(5, 0))

        # Task info
        self.selected_task_label = ttk.Label(progress_column, text="No thread selected",
                                            wraplength=300, justify=tk.LEFT,
                                            font=('TkDefaultFont', 8))
        self.selected_task_label.pack(fill=tk.X, pady=(5, 0))

        # RIGHT SIDE (40%): File status tracking
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=40)

        # File statistics
        stats_frame = ttk.LabelFrame(right_frame, text="File Statistics", padding=10)
        stats_frame.pack(fill=tk.X, pady=(0, 10))

        self.file_stats_label = ttk.Label(stats_frame, text="Pending: 0 | Processing: 0 | Completed: 0")
        self.file_stats_label.pack()

        # File status list
        file_list_frame = ttk.LabelFrame(right_frame, text="File Status", padding=10)
        file_list_frame.pack(fill=tk.BOTH, expand=True)

        # Treeview for files
        file_columns = ('status', 'thread', 'time')
        self.file_tree = ttk.Treeview(file_list_frame, columns=file_columns, show='tree headings', height=15)

        self.file_tree.heading('#0', text='File Name')
        self.file_tree.heading('status', text='Status')
        self.file_tree.heading('thread', text='Thread')
        self.file_tree.heading('time', text='Time (s)')

        self.file_tree.column('#0', width=200)
        self.file_tree.column('status', width=90)
        self.file_tree.column('thread', width=100)
        self.file_tree.column('time', width=70)

        file_scrollbar = ttk.Scrollbar(file_list_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=file_scrollbar.set)
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        file_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind file tree selection
        self.file_tree.bind('<<TreeviewSelect>>', self._on_file_selection_changed)

    def _update_display(self):
        """Update both thread and file displays"""
        self._update_thread_display()
        self._update_file_display()
        self.after(500, self._update_display)

    def _update_thread_display(self):
        """Update the thread monitoring display"""
        # Update overall progress
        threads = self.thread_manager.get_all_threads()
        active_threads = self.thread_manager.get_active_threads()
        overall_progress = self.thread_manager.get_overall_progress()

        total_threads = len(threads)
        active_count = len(active_threads)

        self.overall_progress['value'] = overall_progress
        self.overall_label.config(
            text=f"{active_count} active / {total_threads} total | {overall_progress:.1f}% complete"
        )

        # Remember current selection by thread_id (not item_id)
        current_selection = self.thread_tree.selection()
        selected_thread_id = None
        if current_selection:
            selected_item_id = current_selection[0]
            if hasattr(self, '_item_to_thread'):
                selected_thread_id = self._item_to_thread.get(selected_item_id)

        # Clear tree
        for item in self.thread_tree.get_children():
            self.thread_tree.delete(item)

        # Reset mapping
        self._item_to_thread = {}
        self._thread_to_item = {}

        # Populate tree
        new_selected_item = None
        for thread in threads:
            status_dict = thread.get_status_dict()

            # Map status to simplified labels
            status_label = self._map_status_label(status_dict['status'])

            # Color code by status
            tag = self._get_status_tag(status_label)

            # Truncate long text
            current_task = status_dict['current_task']
            if len(current_task) > 35:
                current_task = current_task[:32] + '...'

            current_file = status_dict.get('current_file', '')
            if current_file:
                file_name = os.path.basename(current_file)
                if len(file_name) > 40:
                    file_name = file_name[:37] + '...'
            else:
                file_name = ''

            item_id = self.thread_tree.insert(
                '', 'end',
                text=thread.display_name,
                values=(
                    status_label,
                    current_task,
                    file_name,
                    f"{status_dict['progress']:.1f}%"
                ),
                tags=(tag,)
            )

            # Map item to thread_id and vice versa
            self._item_to_thread[item_id] = thread.thread_id
            self._thread_to_item[thread.thread_id] = item_id

            # Check if this is the previously selected thread
            if selected_thread_id and thread.thread_id == selected_thread_id:
                new_selected_item = item_id

        # Configure tags for status colors with theme awareness
        is_dark = self.theme_manager and self.theme_manager.is_dark()

        if is_dark:
            # Dark theme colors
            self.thread_tree.tag_configure('initialized', background='#2D3B00', foreground='#E5E7EB')
            self.thread_tree.tag_configure('processing', background='#0D3B2A', foreground='#E5E7EB')
            self.thread_tree.tag_configure('paused', background='#3B3100', foreground='#E5E7EB')
            self.thread_tree.tag_configure('completed', background='#0A2F3F', foreground='#E5E7EB')
            self.thread_tree.tag_configure('released', background='#1F2937', foreground='#9CA3AF')
            self.thread_tree.tag_configure('stopped', background='#2D2D2D', foreground='#9CA3AF')
            self.thread_tree.tag_configure('failed', background='#3B0A0A', foreground='#E5E7EB')
        else:
            # Light theme colors
            self.thread_tree.tag_configure('initialized', background='#f0f4c3', foreground='#0F3057')
            self.thread_tree.tag_configure('processing', background='#c8e6c9', foreground='#0F3057')
            self.thread_tree.tag_configure('paused', background='#fff9c4', foreground='#0F3057')
            self.thread_tree.tag_configure('completed', background='#b3e5fc', foreground='#0F3057')
            self.thread_tree.tag_configure('released', background='#d0d0d0', foreground='#555555')
            self.thread_tree.tag_configure('stopped', background='#e0e0e0', foreground='#555555')
            self.thread_tree.tag_configure('failed', background='#ffcdd2', foreground='#0F3057')

        # Restore selection if item still exists
        if new_selected_item:
            self.thread_tree.selection_set(new_selected_item)
            self.thread_tree.see(new_selected_item)

        # Update selected thread details
        self._update_selected_thread()

    def _update_file_display(self):
        """Update the file tracking display with stable ordering"""
        # Remember current file selection
        current_file_selection = self.file_tree.selection()
        selected_file_item_id = current_file_selection[0] if current_file_selection else None
        selected_file_path = None

        # Get the file path from the selected item
        if selected_file_item_id and selected_file_item_id in self.file_items_map.values():
            for path, item in self.file_items_map.items():
                if item == selected_file_item_id:
                    selected_file_path = path
                    break

        # Get file status from thread manager
        pending_count = 0
        processing_count = 0
        completed_count = 0
        released_count = 0

        # Collect all file information
        all_files_info = {}
        file_status_dict = getattr(self.thread_manager, 'file_status', {})

        # First, get files from thread manager's file_status
        for file_path, status_info in file_status_dict.items():
            status = status_info.get('status', 'pending')
            thread_id = status_info.get('thread_id')
            thread = self.thread_manager.get_thread(thread_id) if thread_id else None

            all_files_info[file_path] = {
                'status': status,
                'thread': thread.display_name if thread else '',
                'time': status_info.get('time')
            }

        # Augment with info from threads
        for thread in self.thread_manager.get_all_threads():
            # Get files from assigned_files
            for file_path in getattr(thread, 'assigned_files', []):
                if file_path not in all_files_info:
                    all_files_info[file_path] = {
                        'status': 'pending',
                        'thread': '',
                        'time': None
                    }

            # Update with current file
            current_file = getattr(thread, 'current_file', None)
            if current_file and current_file in all_files_info:
                if all_files_info[current_file]['status'] in ['pending', 'processing']:
                    all_files_info[current_file] = {
                        'status': 'processing',
                        'thread': thread.display_name,
                        'time': all_files_info[current_file].get('time')
                    }

        # Update file order (only add new files, maintain existing order)
        for file_path in all_files_info.keys():
            if file_path not in self.file_order:
                self.file_order.append(file_path)

        # Clear tree but maintain mapping
        old_items_map = self.file_items_map.copy()
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        self.file_items_map = {}

        # Insert files in stable order
        new_selected_item = None
        for file_path in self.file_order:
            if file_path not in all_files_info:
                continue

            info = all_files_info[file_path]
            file_name = os.path.basename(file_path)
            status = info['status']

            # Count status
            if status == 'pending':
                pending_count += 1
                tag = 'pending'
            elif status == 'processing':
                processing_count += 1
                tag = 'processing'
            elif status == 'released':
                released_count += 1
                tag = 'released'
            else:  # completed
                completed_count += 1
                tag = 'completed'

            time_str = f"{info['time']:.2f}" if info['time'] is not None else ''

            item_id = self.file_tree.insert(
                '', 'end',
                text=file_name,
                values=(
                    status.capitalize(),
                    info['thread'],
                    time_str
                ),
                tags=(tag,)
            )

            self.file_items_map[file_path] = item_id

            # Restore selection if this was the selected file
            if selected_file_path and file_path == selected_file_path:
                new_selected_item = item_id

        # Configure tags with theme awareness
        is_dark = self.theme_manager and self.theme_manager.is_dark()

        if is_dark:
            self.file_tree.tag_configure('pending', foreground='#9CA3AF')
            self.file_tree.tag_configure('processing', foreground='#60A5FA', font=('TkDefaultFont', 9, 'bold'))
            self.file_tree.tag_configure('completed', foreground='#22C55E', font=('TkDefaultFont', 9, 'bold'))
            self.file_tree.tag_configure('released', foreground='#6B7280', font=('TkDefaultFont', 9, 'italic'))
        else:
            self.file_tree.tag_configure('pending', foreground='gray')
            self.file_tree.tag_configure('processing', foreground='blue', font=('TkDefaultFont', 9, 'bold'))
            self.file_tree.tag_configure('completed', foreground='green', font=('TkDefaultFont', 9, 'bold'))
            self.file_tree.tag_configure('released', foreground='#808080', font=('TkDefaultFont', 9, 'italic'))

        # Restore file selection
        if new_selected_item:
            self.file_tree.selection_set(new_selected_item)
            self.file_tree.see(new_selected_item)

        # Update stats
        stats_text = f"Pending: {pending_count} | Processing: {processing_count} | Completed: {completed_count}"
        if released_count > 0:
            stats_text += f" | Released: {released_count}"
        self.file_stats_label.config(text=stats_text)

    def _map_status_label(self, status: str) -> str:
        """Map thread status to simplified label"""
        status_lower = status.lower()
        if 'pending' in status_lower:
            return 'initialized'
        elif 'running' in status_lower:
            return 'processing'
        elif 'paused' in status_lower:
            return 'paused'
        elif 'completed' in status_lower:
            return 'completed'
        elif 'released' in status_lower:
            return 'released'
        elif 'stopped' in status_lower:
            return 'stopped'
        elif 'failed' in status_lower:
            return 'failed'
        return status

    def _get_status_tag(self, status_label: str) -> str:
        """Get tag for thread status"""
        return status_label

    def _update_selected_thread(self):
        """Update the selected thread details"""
        selection = self.thread_tree.selection()
        if not selection:
            self.selected_task_label.config(text="No thread selected")
            self.selected_progress['value'] = 0
            self.selected_progress_label.config(text="0%")
            self.selected_sub_progress['value'] = 0
            self.selected_sub_progress_label.config(text="0%")
            self.btn_view_logs.state(['disabled'])
            self.btn_stop.state(['disabled'])
            return

        item_id = selection[0]
        thread_id = self._item_to_thread.get(item_id)
        if not thread_id:
            return

        thread = self.thread_manager.get_thread(thread_id)
        if not thread:
            return

        self.selected_thread_id = thread_id

        # Update progress bars
        self.selected_progress['value'] = thread.progress
        self.selected_progress_label.config(text=f"{thread.progress:.1f}%")

        self.selected_sub_progress['value'] = thread.sub_progress
        self.selected_sub_progress_label.config(text=f"{thread.sub_progress:.1f}%")

        # Update task label with file info
        task_text = f"Task: {thread.current_task}"
        if thread.current_file:
            task_text += f"\nCurrent file: {os.path.basename(thread.current_file)}"
        if thread.total_tasks > 0:
            task_text += f"\nFiles assigned: {thread.total_tasks} | Processed: {thread.processed_files}"
        if thread.sub_task:
            task_text += f"\nSub-task: {thread.sub_task}"
        if thread.get_elapsed_time():
            task_text += f"\nElapsed: {thread.get_elapsed_time():.1f}s"

        self.selected_task_label.config(text=task_text)

        # Enable/disable buttons
        self.btn_view_logs.state(['!disabled'])
        if thread.status == ThreadStatus.RUNNING:
            self.btn_stop.state(['!disabled'])
        else:
            self.btn_stop.state(['disabled'])

    def _on_selection_changed(self, event):
        """Handle selection change event"""
        # Update selected thread details when selection changes
        self._update_selected_thread()

    def _on_file_selection_changed(self, event):
        """Handle file tree selection change"""
        pass  # File selection doesn't need special handling

    def _on_thread_double_click(self, event):
        """Handle double-click on thread"""
        # Get the clicked item
        selection = self.thread_tree.selection()
        if not selection:
            return

        item_id = selection[0]
        thread_id = self._item_to_thread.get(item_id)
        if not thread_id:
            return

        thread = self.thread_manager.get_thread(thread_id)
        if not thread:
            return

        # Open log viewer for this thread
        from ui.thread_log_viewer import ThreadLogViewer
        ThreadLogViewer(self, thread)

    def _view_thread_logs(self):
        """Open thread log viewer"""
        if not self.selected_thread_id:
            return

        thread = self.thread_manager.get_thread(self.selected_thread_id)
        if not thread:
            return

        # Import here to avoid circular import
        from ui.thread_log_viewer import ThreadLogViewer
        ThreadLogViewer(self, thread)

    def _stop_thread(self):
        """Stop the selected thread"""
        if not self.selected_thread_id:
            return

        self.thread_manager.stop_thread(self.selected_thread_id)

    def _stop_all(self):
        """Stop all threads"""
        self.thread_manager.stop_all()

    def _stop_all_and_release(self):
        """Stop all threads and release resources with cleanup"""
        from tkinter import messagebox

        # Confirm with user
        result = messagebox.askyesno(
            "Confirm Stop & Release",
            "This will stop all running threads, clean up temporary files, and release all resources.\n\n"
            "Are you sure you want to continue?",
            icon='warning'
        )

        if result:
            # Call thread manager's stop_all_and_release
            self.thread_manager.stop_all_and_release()
            messagebox.showinfo(
                "Stop & Release Complete",
                "All threads have been stopped and resources released.\n"
                "Temporary files have been cleaned up."
            )

    def _cleanup_completed(self):
        """Cleanup completed threads"""
        self.thread_manager.cleanup_completed()

