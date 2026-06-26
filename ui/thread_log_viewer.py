"""
Thread Log Viewer
Window for viewing detailed logs of a specific thread.
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
from datetime import datetime
from thread.thread_manager import WorkerThread


class ThreadLogViewer(tk.Toplevel):
    """Window for viewing thread logs"""

    def __init__(self, parent, thread: WorkerThread):
        """
        Initialize thread log viewer

        Args:
            parent: Parent window
            thread: WorkerThread to display logs for
        """
        super().__init__(parent)

        self.thread = thread

        # Get theme manager from parent hierarchy
        self.theme_manager = None
        try:
            # Try direct parent first
            if hasattr(parent, 'theme_manager'):
                self.theme_manager = parent.theme_manager
            # Try parent's main_window
            elif hasattr(parent, 'main_window') and hasattr(parent.main_window, 'theme_manager'):
                self.theme_manager = parent.main_window.theme_manager
            # Try traversing up the widget hierarchy
            elif hasattr(parent, 'master'):
                current = parent.master
                for _ in range(5):  # Try up to 5 levels
                    if hasattr(current, 'theme_manager'):
                        self.theme_manager = current.theme_manager
                        break
                    if hasattr(current, 'master'):
                        current = current.master
                    else:
                        break

            # If still not found, try to get global theme manager
            if self.theme_manager is None:
                from ui.theme_manager import get_theme_manager
                self.theme_manager = get_theme_manager()

        except Exception as e:
            print(f"Error getting theme manager: {e}")
            # Last resort: try global theme manager
            try:
                from ui.theme_manager import get_theme_manager
                self.theme_manager = get_theme_manager()
            except:
                pass

        # Window configuration
        self.title(f"Thread Logs - {thread.display_name}")
        self.geometry("800x600")
        self.minsize(600, 400)

        # Apply theme to window
        if self.theme_manager:
            theme = self.theme_manager.current_theme
            self.configure(background=theme['bg'])

        # Make window modal
        self.transient(parent)
        self.grab_set()

        # Create UI
        self._create_ui()

        # Load logs
        self._load_logs()

        # Start update loop
        self._update_logs()

    def _create_ui(self):
        """Create UI components"""
        # Main frame
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Thread info section
        info_frame = ttk.LabelFrame(main_frame, text="Thread Information", padding=10)
        info_frame.pack(fill=tk.X, pady=(0, 10))

        info_grid = ttk.Frame(info_frame)
        info_grid.pack(fill=tk.X)

        # Thread details
        row = 0
        ttk.Label(info_grid, text="Thread ID:", font=('TkDefaultFont', 9, 'bold')).grid(
            row=row, column=0, sticky=tk.W, padx=(0, 10))
        self.thread_id_label = ttk.Label(info_grid, text=self.thread.thread_id)
        self.thread_id_label.grid(row=row, column=1, sticky=tk.W)

        row += 1
        ttk.Label(info_grid, text="Status:", font=('TkDefaultFont', 9, 'bold')).grid(
            row=row, column=0, sticky=tk.W, padx=(0, 10))
        self.status_label = ttk.Label(info_grid, text=self.thread.status.value)
        self.status_label.grid(row=row, column=1, sticky=tk.W)

        row += 1
        ttk.Label(info_grid, text="Overall Progress:", font=('TkDefaultFont', 9, 'bold')).grid(
            row=row, column=0, sticky=tk.W, padx=(0, 10))
        progress_frame = ttk.Frame(info_grid)
        progress_frame.grid(row=row, column=1, sticky=tk.EW)
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=200)
        self.progress_bar.pack(side=tk.LEFT, padx=(0, 10))
        self.progress_label = ttk.Label(progress_frame, text=f"{self.thread.progress:.1f}%")
        self.progress_label.pack(side=tk.LEFT)

        row += 1
        ttk.Label(info_grid, text="Current Step:", font=('TkDefaultFont', 9, 'bold')).grid(
            row=row, column=0, sticky=tk.W, padx=(0, 10))
        sub_progress_frame = ttk.Frame(info_grid)
        sub_progress_frame.grid(row=row, column=1, sticky=tk.EW)
        self.sub_progress_bar = ttk.Progressbar(sub_progress_frame, mode='determinate', length=200)
        self.sub_progress_bar.pack(side=tk.LEFT, padx=(0, 10))
        self.sub_progress_label = ttk.Label(sub_progress_frame, text=f"{self.thread.sub_progress:.1f}%")
        self.sub_progress_label.pack(side=tk.LEFT)

        row += 1
        ttk.Label(info_grid, text="Current Task:", font=('TkDefaultFont', 9, 'bold')).grid(
            row=row, column=0, sticky=tk.W, padx=(0, 10))
        self.task_label = ttk.Label(info_grid, text=self.thread.current_task, wraplength=500)
        self.task_label.grid(row=row, column=1, sticky=tk.W)

        row += 1
        ttk.Label(info_grid, text="Sub Task:", font=('TkDefaultFont', 9, 'bold')).grid(
            row=row, column=0, sticky=tk.W, padx=(0, 10))
        self.sub_task_label = ttk.Label(info_grid, text=self.thread.sub_task or "N/A", wraplength=500)
        self.sub_task_label.grid(row=row, column=1, sticky=tk.W)

        row += 1
        ttk.Label(info_grid, text="Elapsed Time:", font=('TkDefaultFont', 9, 'bold')).grid(
            row=row, column=0, sticky=tk.W, padx=(0, 10))
        self.elapsed_label = ttk.Label(info_grid, text="0s")
        self.elapsed_label.grid(row=row, column=1, sticky=tk.W)

        # Log filter section
        filter_frame = ttk.Frame(main_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(filter_frame, text="Filter:").pack(side=tk.LEFT, padx=(0, 5))

        self.filter_var = tk.StringVar(value="ALL")
        ttk.Radiobutton(filter_frame, text="All", variable=self.filter_var,
                       value="ALL", command=self._filter_logs).pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(filter_frame, text="Info", variable=self.filter_var,
                       value="INFO", command=self._filter_logs).pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(filter_frame, text="Warning", variable=self.filter_var,
                       value="WARNING", command=self._filter_logs).pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(filter_frame, text="Error", variable=self.filter_var,
                       value="ERROR", command=self._filter_logs).pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(filter_frame, text="Success", variable=self.filter_var,
                       value="SUCCESS", command=self._filter_logs).pack(side=tk.LEFT, padx=2)

        ttk.Button(filter_frame, text="Clear Logs", command=self._clear_display).pack(
            side=tk.RIGHT, padx=(5, 0))
        ttk.Button(filter_frame, text="Refresh", command=self._load_logs).pack(
            side=tk.RIGHT)

        # Log display
        log_frame = ttk.LabelFrame(main_frame, text="Logs", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True)

        # Create scrolled text widget for logs
        if self.theme_manager:
            theme = self.theme_manager.current_theme
            print(f"Applying theme to log viewer: {theme['name']}, bg={theme['input_bg']}, fg={theme['fg']}")
            self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD,
                                                       font=('Courier', 9),
                                                       background=theme['input_bg'],
                                                       foreground=theme['fg'],
                                                       insertbackground=theme['fg'],
                                                       selectbackground=theme['select_bg'],
                                                       selectforeground=theme['select_fg'])
        else:
            print("Warning: No theme manager found, using default colors")
            self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD,
                                                       font=('Courier', 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Configure text tags for different log levels
        if self.theme_manager:
            theme = self.theme_manager.current_theme
            self.log_text.tag_configure('INFO', foreground=theme['info'])
            self.log_text.tag_configure('WARNING', foreground=theme['warning'])
            self.log_text.tag_configure('ERROR', foreground=theme['error'], font=('Courier', 9, 'bold'))
            self.log_text.tag_configure('SUCCESS', foreground=theme['success'], font=('Courier', 9, 'bold'))
            self.log_text.tag_configure('timestamp', foreground=theme['text_secondary'])
        else:
            self.log_text.tag_configure('INFO', foreground='black')
            self.log_text.tag_configure('WARNING', foreground='orange')
            self.log_text.tag_configure('ERROR', foreground='red', font=('Courier', 9, 'bold'))
            self.log_text.tag_configure('SUCCESS', foreground='green', font=('Courier', 9, 'bold'))
            self.log_text.tag_configure('timestamp', foreground='gray')

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(button_frame, text="Close", command=self.destroy).pack(side=tk.RIGHT)

        if self.thread.is_alive():
            ttk.Button(button_frame, text="Stop Thread",
                      command=self._stop_thread).pack(side=tk.RIGHT, padx=(0, 5))

    def _load_logs(self):
        """Load all logs from thread"""
        self._clear_display()

        for log_entry in self.thread.logs:
            self._append_log(log_entry)

        # Auto-scroll to bottom
        self.log_text.see(tk.END)

    def _filter_logs(self):
        """Filter logs by level"""
        filter_level = self.filter_var.get()

        self._clear_display()

        for log_entry in self.thread.logs:
            if filter_level == "ALL" or log_entry['level'] == filter_level:
                self._append_log(log_entry)

        self.log_text.see(tk.END)

    def _append_log(self, log_entry: dict):
        """Append a log entry to the display"""
        timestamp = log_entry['timestamp'].strftime("%H:%M:%S.%f")[:-3]
        level = log_entry['level']
        message = log_entry['message']
        progress = log_entry['progress']

        # Format log line
        log_line = f"[{timestamp}] [{level:8s}] [{progress:5.1f}%] {message}\n"

        # Insert with appropriate tag
        self.log_text.insert(tk.END, log_line, level)

    def _clear_display(self):
        """Clear the log display"""
        self.log_text.delete(1.0, tk.END)

    def _update_logs(self):
        """Update logs and thread info periodically"""
        # Update thread info
        self.status_label.config(text=self.thread.status.value)
        self.progress_bar['value'] = self.thread.progress
        self.progress_label.config(text=f"{self.thread.progress:.1f}%")
        self.sub_progress_bar['value'] = self.thread.sub_progress
        self.sub_progress_label.config(text=f"{self.thread.sub_progress:.1f}%")
        self.task_label.config(text=self.thread.current_task)
        self.sub_task_label.config(text=self.thread.sub_task or "N/A")

        elapsed = self.thread.get_elapsed_time()
        if elapsed:
            self.elapsed_label.config(text=f"{elapsed:.1f}s")

        # Check for new logs
        try:
            while True:
                log_entry = self.thread.log_queue.get_nowait()
                filter_level = self.filter_var.get()
                if filter_level == "ALL" or log_entry['level'] == filter_level:
                    self._append_log(log_entry)
                    self.log_text.see(tk.END)
        except:
            pass

        # Schedule next update
        if self.winfo_exists():
            self.after(500, self._update_logs)

    def _stop_thread(self):
        """Stop the thread"""
        self.thread.stop()

