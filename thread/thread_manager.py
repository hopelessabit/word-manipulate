"""
Thread Manager
Manages worker threads with progress tracking, logging, and status monitoring.
"""
import threading
import queue
import os
import glob
from enum import Enum
from typing import Callable, Dict, List, Any, Optional
from datetime import datetime


class ThreadStatus(Enum):
    """Thread status enumeration"""
    PENDING = "Pending"
    RUNNING = "Running"
    PAUSED = "Paused"
    COMPLETED = "Completed"
    FAILED = "Failed"
    STOPPED = "Stopped"
    RELEASED = "Released"


class WorkerThread(threading.Thread):
    """
    Worker thread with progress tracking and logging capabilities
    """
    
    def __init__(self, thread_id: str, name: str, target: Callable, 
                 args: tuple = (), kwargs: dict = None):
        """
        Initialize worker thread
        
        Args:
            thread_id: Unique thread identifier
            name: Thread display name
            target: Function to execute
            args: Function arguments
            kwargs: Function keyword arguments
        """
        super().__init__(name=name, daemon=False)
        
        self.thread_id = thread_id
        self.display_name = name
        self.target_func = target
        self.args = args
        self.kwargs = kwargs or {}
        
        # Status tracking
        self.status = ThreadStatus.PENDING
        self.progress = 0.0  # 0.0 to 100.0
        self.current_task = "Initializing..."
        self.error_message = None
        self.result = None
        
        # Control flags
        self._stop_flag = threading.Event()
        self._pause_flag = threading.Event()
        self._pause_flag.set()  # Initially not paused

        # Logging
        self.log_queue = queue.Queue()
        self.logs: List[Dict[str, Any]] = []
        
        # Timestamps
        self.start_time = None
        self.end_time = None
        self.pause_time = None
        self.total_paused_time = 0.0

        # Sub-progress tracking (for operations with multiple steps)
        self.sub_progress = 0.0
        self.sub_task = ""
        
        # Task assignment tracking
        self.assigned_files = []  # List of files assigned to this thread
        self.total_tasks = 0  # Total number of tasks assigned
        self.processed_files = 0  # Number of files processed
        self.current_file = None  # Current file being processed
        self.can_accept_tasks = True  # Whether this thread can accept new tasks

        # Priority (1=highest, 5=lowest, 3=normal)
        self.priority = 3

        # File completion tracking
        self.completed_files = {}  # {file_path: {'time': seconds, 'timestamp': datetime}}

    def run(self):
        """Execute the worker thread"""
        try:
            self.status = ThreadStatus.RUNNING
            self.start_time = datetime.now()
            self.log("Thread started", "INFO")
            
            # Execute target function with progress callback
            self.result = self.target_func(
                self,  # Pass self for progress updates
                *self.args,
                **self.kwargs
            )
            
            if not self._stop_flag.is_set():
                self.status = ThreadStatus.COMPLETED
                self.progress = 100.0
                self.current_task = "Completed"
                self.log("Thread completed successfully", "SUCCESS")
            else:
                self.status = ThreadStatus.STOPPED
                self.log("Thread stopped by user", "WARNING")
                
        except Exception as e:
            self.status = ThreadStatus.FAILED
            self.error_message = str(e)
            self.log(f"Thread failed: {str(e)}", "ERROR")
            
        finally:
            self.end_time = datetime.now()

    def mark_file_completed(self, file_path: str, elapsed_time: float):
        """Mark a file as completed with timing info"""
        self.completed_files[file_path] = {
            'time': elapsed_time,
            'timestamp': datetime.now(),
            'thread_id': self.thread_id,
            'thread_name': self.display_name
        }

        # Also update the global file_status in thread manager if available
        if hasattr(self, '_manager') and self._manager:
            self._manager.file_status[file_path] = {
                'status': 'completed',
                'thread_id': self.thread_id,
                'time': elapsed_time
            }

    def mark_file_error(self, file_path: str, error_message: str):
        """Mark a file as having an error during processing"""
        self.log(f"File error: {os.path.basename(file_path)} - {error_message}", "ERROR")

        # Update the global file_status in thread manager if available
        if hasattr(self, '_manager') and self._manager:
            self._manager.file_status[file_path] = {
                'status': 'error',
                'thread_id': self.thread_id,
                'time': None,
                'error': error_message
            }

    def log(self, message: str, level: str = "INFO"):
        """
        Add log entry
        
        Args:
            message: Log message
            level: Log level (INFO, WARNING, ERROR, SUCCESS)
        """
        log_entry = {
            'timestamp': datetime.now(),
            'level': level,
            'message': message,
            'progress': self.progress
        }
        self.logs.append(log_entry)
        self.log_queue.put(log_entry)
        
    def update_progress(self, progress: float, task: str = None):
        """
        Update thread progress
        
        Args:
            progress: Progress percentage (0-100)
            task: Current task description
        """
        self.progress = max(0.0, min(100.0, progress))
        if task:
            self.current_task = task
            self.log(f"Progress: {self.progress:.1f}% - {task}", "INFO")
            
    def update_sub_progress(self, sub_progress: float, sub_task: str = None):
        """
        Update sub-task progress
        
        Args:
            sub_progress: Sub-progress percentage (0-100)
            sub_task: Sub-task description
        """
        self.sub_progress = max(0.0, min(100.0, sub_progress))
        if sub_task:
            self.sub_task = sub_task
            
    def stop(self):
        """Request thread to stop"""
        self.log("Stop requested", "WARNING")
        self._stop_flag.set()
        
    def should_stop(self) -> bool:
        """Check if thread should stop"""
        return self._stop_flag.is_set()

    def pause(self):
        """Pause the thread"""
        if self.status == ThreadStatus.RUNNING:
            self.status = ThreadStatus.PAUSED
            self.pause_time = datetime.now()
            self._pause_flag.clear()
            self.log("Thread paused", "INFO")

    def resume(self):
        """Resume the thread"""
        if self.status == ThreadStatus.PAUSED:
            self.status = ThreadStatus.RUNNING
            if self.pause_time:
                pause_duration = (datetime.now() - self.pause_time).total_seconds()
                self.total_paused_time += pause_duration
                self.pause_time = None
            self._pause_flag.set()
            self.log("Thread resumed", "INFO")

    def release(self):
        """Release thread: stop work, mark as released/inactive, set UI-inactive state"""
        self.log("Release requested", "WARNING")
        self._stop_flag.set()
        self.can_accept_tasks = False
        self.status = ThreadStatus.RELEASED
        self.current_task = "Released"
        # Keep current progress value but mark as inactive (UI will use progress_color)
        if self.progress is None:
            self.progress = 0.0
        self.log("Thread released and marked inactive", "INFO")
        if self.status == ThreadStatus.PAUSED:
            self.status = ThreadStatus.RUNNING
            if self.pause_time:
                pause_duration = (datetime.now() - self.pause_time).total_seconds()
                self.total_paused_time += pause_duration
                self.pause_time = None
            self._pause_flag.set()
            self.log("Thread resumed", "INFO")

    def wait_if_paused(self):
        """Wait if thread is paused - call this in worker loops"""
        if self.status == ThreadStatus.PAUSED:
            self._pause_flag.wait()

    def get_elapsed_time(self) -> Optional[float]:
        """Get elapsed time in seconds"""
        if self.start_time:
            end = self.end_time or datetime.now()
            return (end - self.start_time).total_seconds()
        return None
        
    def get_status_dict(self) -> Dict[str, Any]:
        """Get thread status as dictionary (includes UI color hint)"""
        # Determine progress color based on status
        if self.status in (ThreadStatus.RELEASED, ThreadStatus.STOPPED):
            progress_color = "gray"
        elif self.status == ThreadStatus.COMPLETED:
            progress_color = "green"
        elif self.status == ThreadStatus.FAILED:
            progress_color = "red"
        elif self.status == ThreadStatus.PAUSED:
            progress_color = "orange"
        else:
            progress_color = "blue"

        return {
            'thread_id': self.thread_id,
            'name': self.display_name,
            'status': self.status.value,
            'progress': self.progress,
            'sub_progress': self.sub_progress,
            'current_task': self.current_task,
            'sub_task': self.sub_task,
            'current_file': self.current_file or '',
            'total_tasks': self.total_tasks,
            'processed_files': self.processed_files,
            'error': self.error_message,
            'elapsed_time': self.get_elapsed_time(),
            'is_alive': self.is_alive(),
            'progress_color': progress_color
        }


class ThreadManager:
    """Manager for worker thread pool"""

    def __init__(self, max_pool_size: int = 4):
        """
        Initialize thread manager

        Args:
            max_pool_size: Maximum number of concurrent threads
        """
        self.threads: Dict[str, WorkerThread] = {}
        self._next_id = 1
        self._lock = threading.Lock()
        self.max_pool_size = max_pool_size

        # File tracking across all threads
        self.file_status = {}  # {file_path: {'status': 'pending'|'processing'|'completed', 'thread_id': str, 'time': float}}
        self.all_files = []  # All files to process

        # Task queue for pooling
        self.pending_tasks = queue.Queue()
        self.completed_files_list = []  # List of completed file info

    def create_thread(self, name: str, target: Callable,
                     args: tuple = (), kwargs: dict = None) -> str:
        """
        Create a new worker thread
        
        Args:
            name: Thread name
            target: Function to execute
            args: Function arguments
            kwargs: Function keyword arguments
            
        Returns:
            Thread ID
        """
        with self._lock:
            thread_id = f"thread_{self._next_id}"
            self._next_id += 1
            
            thread = WorkerThread(thread_id, name, target, args, kwargs)
            thread._manager = self  # Give thread a reference to manager for file status updates
            self.threads[thread_id] = thread
            
            return thread_id

    def create_worker_threads(self, files: List[str], task_type: str, worker_func: Callable,
                            config: dict, num_threads: Optional[int] = None,
                            priority: int = 3) -> List[str]:
        """
        Create multiple worker threads and distribute files among them

        Args:
            files: List of file paths to process
            task_type: Type of task (e.g., "Splitting", "Merging")
            worker_func: Worker function to execute
            config: Configuration dictionary to pass to worker
            num_threads: Number of threads to create (default: min(pool_size, len(files)))
            priority: Thread priority (1=highest, 5=lowest, 3=normal)

        Returns:
            List of created thread IDs
        """
        # Determine optimal number of threads
        if num_threads is None:
            num_threads = min(self.max_pool_size, len(files))
        else:
            num_threads = min(num_threads, self.max_pool_size)

        thread_ids = []

        with self._lock:
            # Distribute files round-robin among threads
            for i in range(num_threads):
                # Get files for this thread (round-robin distribution)
                thread_files = files[i::num_threads]

                if thread_files:
                    thread_id = f"thread_{self._next_id}"
                    self._next_id += 1

                    # Create config for this thread
                    thread_config = config.copy()
                    thread_config['files'] = thread_files

                    # Create thread
                    thread = WorkerThread(
                        thread_id=thread_id,
                        name=f"{task_type} Worker {i+1}",
                        target=worker_func,
                        args=(),
                        kwargs={'config': thread_config}
                    )

                    # Give thread a reference to manager for file status updates
                    thread._manager = self

                    # Set up task tracking
                    thread.assigned_files = thread_files
                    thread.total_tasks = len(thread_files)
                    thread.processed_files = 0
                    thread.current_task = task_type
                    thread.can_accept_tasks = False
                    thread.priority = priority

                    # Register files in file_status
                    for file_path in thread_files:
                        self.file_status[file_path] = {
                            'status': 'pending',
                            'thread_id': thread_id,
                            'time': None
                        }

                    self.threads[thread_id] = thread
                    thread_ids.append(thread_id)

        return thread_ids

    def start_thread(self, thread_id: str):
        """Start a thread"""
        thread = self.threads.get(thread_id)
        if thread and not thread.is_alive():
            thread.start()
            
    def stop_thread(self, thread_id: str):
        """Stop a thread"""
        thread = self.threads.get(thread_id)
        if thread:
            thread.stop()
            
    def get_thread(self, thread_id: str) -> Optional[WorkerThread]:
        """Get thread by ID"""
        return self.threads.get(thread_id)
        
    def get_all_threads(self) -> List[WorkerThread]:
        """Get all threads"""
        return list(self.threads.values())
        
    def get_active_threads(self) -> List[WorkerThread]:
        """Get active (running or pending) threads"""
        return [t for t in self.threads.values() 
                if t.status in [ThreadStatus.PENDING, ThreadStatus.RUNNING]]
                
    def get_overall_progress(self) -> float:
        """Calculate overall progress across all threads"""
        threads = self.get_all_threads()
        if not threads:
            return 0.0
        return sum(t.progress for t in threads) / len(threads)
        
    def stop_all(self):
        """Stop all running threads"""
        for thread in self.threads.values():
            if thread.is_alive():
                thread.stop()

    def pause_thread(self, thread_id: str):
        """Pause a specific thread"""
        thread = self.threads.get(thread_id)
        if thread:
            thread.pause()

    def resume_thread(self, thread_id: str):
        """Resume a specific thread"""
        thread = self.threads.get(thread_id)
        if thread:
            thread.resume()

    def pause_all(self):
        """Pause all running threads"""
        for thread in self.threads.values():
            if thread.status == ThreadStatus.RUNNING:
                thread.pause()

    def resume_all(self):
        """Resume all paused threads"""
        for thread in self.threads.values():
            if thread.status == ThreadStatus.PAUSED:
                thread.resume()

    def set_thread_priority(self, thread_id: str, priority: int):
        """Set thread priority (1=highest, 5=lowest)"""
        thread = self.threads.get(thread_id)

    def _remove_temp_files(self, file_path: str, suffixes: List[str]) -> None:
        """Attempt to remove temp variants of a file using provided suffixes"""
        base_dir = os.path.dirname(file_path)
        base_name = os.path.basename(file_path)
        name_without_ext = os.path.splitext(base_name)[0]

        for s in suffixes:
            # Try exact path + suffix
            candidate = f"{file_path}{s}"
            try:
                if os.path.exists(candidate):
                    os.remove(candidate)
                    print(f"Removed temp file: {candidate}")
            except Exception as e:
                print(f"Failed to remove {candidate}: {e}")

            # Try pattern matching for related temp files
            pattern = os.path.join(base_dir, f"{name_without_ext}*{s}")
            try:
                for temp_file in glob.glob(pattern):
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                        print(f"Removed temp file: {temp_file}")
            except Exception as e:
                print(f"Failed to remove temp files with pattern {pattern}: {e}")

    def stop_all_and_release(self,
                             temp_cleanup_func: Optional[Callable[[str], None]] = None,
                             temp_file_suffixes: Optional[List[str]] = None,
                             join_timeout: float = 2.0) -> None:
        """
        Stop all running threads, remove temp files for unfinished files,
        and mark threads/files as released (UI should render progress bars gray).

        Args:
            temp_cleanup_func: optional callback(file_path) to remove temp artifacts
            temp_file_suffixes: list of suffixes to try when removing temp files
                               (default: ['.tmp', '.part', '.bak', '_temp', '_processing'])
            join_timeout: seconds to wait for each thread to join
        """
        if temp_file_suffixes is None:
            temp_file_suffixes = ['.tmp', '.part', '.bak', '_temp', '_processing', '.temp']

        print(f"\n{'='*60}")
        print("STOP AND RELEASE - Starting cleanup process")
        print(f"{'='*60}")

        # 1) Request stop for all threads
        print("\n[1/4] Stopping all threads...")
        for thread in list(self.threads.values()):
            if thread.is_alive() or thread.status in (ThreadStatus.PENDING, ThreadStatus.RUNNING, ThreadStatus.PAUSED):
                thread.log("Global stop_and_release requested", "WARNING")
                thread.stop()
                print(f"  - Stopped: {thread.display_name}")

        # 2) Wait briefly for threads to respond
        print("\n[2/4] Waiting for threads to finish (timeout: {:.1f}s)...".format(join_timeout))
        for thread in list(self.threads.values()):
            try:
                if thread.is_alive():
                    thread.join(join_timeout)
                    if thread.is_alive():
                        print(f"  - Warning: {thread.display_name} still running after timeout")
                    else:
                        print(f"  - Joined: {thread.display_name}")
            except Exception as e:
                print(f"  - Error joining {thread.display_name}: {e}")

        # 3) Cleanup unfinished files (remove temp artifacts) and mark as released
        print("\n[3/4] Cleaning up temp files for unfinished tasks...")
        cleaned_count = 0
        for file_path, info in list(self.file_status.items()):
            if info.get('status') not in ['completed', 'released']:
                print(f"  - Cleaning: {os.path.basename(file_path)}")
                # attempt cleanup
                try:
                    if temp_cleanup_func:
                        temp_cleanup_func(file_path)
                    else:
                        self._remove_temp_files(file_path, temp_file_suffixes)
                    cleaned_count += 1
                except Exception as e:
                    print(f"    Error cleaning {file_path}: {e}")

                # mark file as released
                self.file_status[file_path] = {
                    'status': 'released',
                    'thread_id': None,
                    'time': None
                }

        print(f"  Total files cleaned: {cleaned_count}")

        # 4) Mark threads as released and set inactive UI hints
        print("\n[4/4] Releasing all threads...")
        with self._lock:
            for thread in list(self.threads.values()):
                if thread.status not in (ThreadStatus.COMPLETED, ThreadStatus.FAILED):
                    try:
                        thread.release()
                        print(f"  - Released: {thread.display_name}")
                    except Exception as e:
                        # fallback: set minimal released fields
                        print(f"  - Force-releasing {thread.display_name}: {e}")
                        thread._stop_flag.set()
                        thread.can_accept_tasks = False
                        thread.status = ThreadStatus.RELEASED
                        thread.current_task = "Released"
                        thread.log("Forced release applied", "WARNING")

        print(f"\n{'='*60}")
        print("STOP AND RELEASE - Cleanup complete")
        print(f"{'='*60}\n")

    def cleanup_completed(self):
        """Remove completed/failed threads from the thread pool"""
        with self._lock:
            completed_threads = [
                thread_id for thread_id, thread in self.threads.items()
                if thread.status in (ThreadStatus.COMPLETED, ThreadStatus.FAILED, ThreadStatus.RELEASED)
                and not thread.is_alive()
            ]

            for thread_id in completed_threads:
                thread = self.threads[thread_id]
                print(f"Cleaning up thread: {thread.display_name} (Status: {thread.status.value})")
                del self.threads[thread_id]

            if completed_threads:
                print(f"Cleaned up {len(completed_threads)} completed thread(s)")
            else:
                print("No completed threads to clean up")
