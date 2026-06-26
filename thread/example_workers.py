"""
Example Worker Functions
Examples of how to create worker functions that integrate with the threading system.
"""
import time
import random
from datetime import datetime


def example_split_worker(thread, input_file: str, output_dir: str, pages_per_file: int):
    """
    Example worker function for split documents
    
    Args:
        thread: WorkerThread instance (automatically passed)
        input_file: Input file path
        output_dir: Output directory
        pages_per_file: Pages per file
        
    Returns:
        Dictionary with results
    """
    thread.log(f"Starting split operation: {input_file}", "INFO")
    thread.update_progress(0, "Loading document...")
    
    # Simulate loading document
    time.sleep(1)
    if thread.should_stop():
        return None
        
    total_pages = 100  # Example
    num_files = total_pages // pages_per_file
    
    thread.log(f"Document has {total_pages} pages, will create {num_files} files", "INFO")
    thread.update_progress(10, "Document loaded")
    
    files_created = []
    
    for i in range(num_files):
        if thread.should_stop():
            thread.log("Operation stopped by user", "WARNING")
            return {'files_created': files_created, 'stopped': True}
            
        # Update main progress
        main_progress = 10 + (i / num_files) * 80
        thread.update_progress(main_progress, f"Creating file {i+1}/{num_files}")
        
        # Simulate processing pages with sub-progress
        for page in range(pages_per_file):
            if thread.should_stop():
                return {'files_created': files_created, 'stopped': True}
                
            sub_progress = (page / pages_per_file) * 100
            thread.update_sub_progress(sub_progress, f"Processing page {page+1}/{pages_per_file}")
            
            time.sleep(0.05)  # Simulate work
            
        output_file = f"{output_dir}/output_part_{i+1}.docx"
        files_created.append(output_file)
        thread.log(f"Created: {output_file}", "SUCCESS")
        
    thread.update_progress(90, "Finalizing...")
    time.sleep(0.5)
    
    thread.update_progress(100, "Complete!")
    thread.log(f"Split operation completed. Created {len(files_created)} files", "SUCCESS")
    
    return {
        'files_created': files_created,
        'total_pages': total_pages,
        'stopped': False
    }


def example_merge_worker(thread, input_files: list, output_file: str):
    """
    Example worker function for merge documents
    
    Args:
        thread: WorkerThread instance
        input_files: List of input file paths
        output_file: Output file path
        
    Returns:
        Dictionary with results
    """
    thread.log(f"Starting merge operation: {len(input_files)} files", "INFO")
    thread.update_progress(0, "Initializing merge...")
    
    time.sleep(0.5)
    
    total_files = len(input_files)
    merged_pages = 0
    
    for i, file_path in enumerate(input_files):
        if thread.should_stop():
            thread.log("Merge stopped by user", "WARNING")
            return {'output_file': output_file, 'merged_pages': merged_pages, 'stopped': True}
            
        # Update main progress
        main_progress = (i / total_files) * 90
        thread.update_progress(main_progress, f"Merging file {i+1}/{total_files}")
        thread.log(f"Processing: {file_path}", "INFO")
        
        # Simulate reading and merge pages
        pages_in_file = random.randint(5, 15)
        for page in range(pages_in_file):
            if thread.should_stop():
                return {'output_file': output_file, 'merged_pages': merged_pages, 'stopped': True}
                
            sub_progress = (page / pages_in_file) * 100
            thread.update_sub_progress(sub_progress, f"Merging page {page+1}/{pages_in_file}")
            
            time.sleep(0.03)
            merged_pages += 1
            
        thread.log(f"Merged {pages_in_file} pages from {file_path}", "SUCCESS")
        
    thread.update_progress(95, "Saving merged document...")
    time.sleep(1)
    
    thread.update_progress(100, "Complete!")
    thread.log(f"Merge completed. Output: {output_file}, Total pages: {merged_pages}", "SUCCESS")
    
    return {
        'output_file': output_file,
        'merged_pages': merged_pages,
        'stopped': False
    }


def example_naming_worker(thread, directory: str, files: list, pattern: str):
    """
    Example worker function for file name
    
    Args:
        thread: WorkerThread instance
        directory: Target directory
        files: List of files to rename
        pattern: Naming pattern
        
    Returns:
        Dictionary with results
    """
    thread.log(f"Starting name operation: {len(files)} files", "INFO")
    thread.update_progress(0, "Preparing to rename files...")
    
    time.sleep(0.3)
    
    renamed_count = 0
    failed_count = 0
    
    for i, file_info in enumerate(files):
        if thread.should_stop():
            thread.log("Naming operation stopped by user", "WARNING")
            return {'renamed': renamed_count, 'failed': failed_count, 'stopped': True}
            
        progress = (i / len(files)) * 100
        thread.update_progress(progress, f"Renaming file {i+1}/{len(files)}")
        
        old_name = file_info.get('name', '')
        new_name = file_info.get('new_name', '')
        
        thread.log(f"Renaming: {old_name} -> {new_name}", "INFO")
        
        # Simulate rename operation
        thread.update_sub_progress(50, "Checking file...")
        time.sleep(0.1)
        
        # Simulate some failures
        if random.random() < 0.1:  # 10% failure rate for demo
            thread.log(f"Failed to rename: {old_name}", "ERROR")
            failed_count += 1
        else:
            thread.update_sub_progress(100, "Renaming...")
            time.sleep(0.1)
            thread.log(f"Successfully renamed: {old_name} -> {new_name}", "SUCCESS")
            renamed_count += 1
            
    thread.update_progress(100, "Complete!")
    thread.log(f"Naming operation completed. Renamed: {renamed_count}, Failed: {failed_count}", "SUCCESS")
    
    return {
        'renamed': renamed_count,
        'failed': failed_count,
        'stopped': False
    }


def test_progress_worker(thread, task_name: str = "Test Task", duration: int = 20):
    """
    Test worker function that increases progress by 10% every 2 seconds with detailed logging.

    Args:
        thread: WorkerThread instance
        task_name: Name of the test task
        duration: Total duration in seconds (default: 20 seconds for 10 steps)

    Returns:
        Dictionary with test results
    """
    thread.log(f"Starting test task: {task_name}", "INFO")
    thread.log(f"Duration: {duration} seconds", "INFO")
    thread.log(f"Progress will increase by 10% every 2 seconds", "INFO")
    thread.update_progress(0, "Initializing test task...")

    start_time = datetime.now()
    thread.log(f"Task started at: {start_time.strftime('%H:%M:%S')}", "INFO")

    # Simulate work with 10 steps (0% to 100%)
    num_steps = 10
    interval = 2.0  # 2 seconds between each step

    for step in range(num_steps + 1):
        # Check if stop was requested
        if thread.should_stop():
            thread.log("Test task stopped by user", "WARNING")
            elapsed = (datetime.now() - start_time).total_seconds()
            thread.log(f"Task stopped after {elapsed:.1f} seconds at {step * 10}% progress", "WARNING")
            return {
                'completed': False,
                'stopped': True,
                'final_progress': step * 10,
                'elapsed_time': elapsed
            }

        # Update progress
        progress = step * 10
        thread.update_progress(progress, f"Processing step {step}/{num_steps}")

        # Log detailed information for each step
        current_time = datetime.now()
        elapsed = (current_time - start_time).total_seconds()

        thread.log(f"Step {step}/{num_steps} completed", "INFO")
        thread.log(f"Current progress: {progress}%", "INFO")
        thread.log(f"Time elapsed: {elapsed:.1f}s", "INFO")
        thread.log(f"Current time: {current_time.strftime('%H:%M:%S')}", "INFO")

        # Simulate sub-tasks within each step
        if step < num_steps:  # Don't simulate sub-tasks on the last step
            thread.log(f"Starting sub-tasks for step {step + 1}...", "INFO")

            for sub_step in range(5):
                if thread.should_stop():
                    break

                sub_progress = (sub_step + 1) * 20
                thread.update_sub_progress(sub_progress, f"Sub-task {sub_step + 1}/5")

                # Log sub-task details
                if sub_step == 0:
                    thread.log("  → Sub-task 1: Preparing data...", "INFO")
                elif sub_step == 1:
                    thread.log("  → Sub-task 2: Processing data...", "INFO")
                elif sub_step == 2:
                    thread.log("  → Sub-task 3: Validating results...", "INFO")
                elif sub_step == 3:
                    thread.log("  → Sub-task 4: Optimizing...", "INFO")
                elif sub_step == 4:
                    thread.log("  → Sub-task 5: Finalizing...", "SUCCESS")

                # Sleep for a fraction of the interval
                time.sleep(interval / 5)

            # Reset sub-progress after completing all sub-tasks
            thread.update_sub_progress(0, "")

            # Log step completion
            if step % 3 == 0 and step > 0:
                thread.log(f"Milestone reached! {progress}% complete!", "SUCCESS")

    # Final completion
    end_time = datetime.now()
    total_elapsed = (end_time - start_time).total_seconds()

    thread.log("=" * 50, "INFO")
    thread.log("Test task completed successfully!", "SUCCESS")
    thread.log(f"Start time: {start_time.strftime('%H:%M:%S')}", "INFO")
    thread.log(f"End time: {end_time.strftime('%H:%M:%S')}", "INFO")
    thread.log(f"Total elapsed time: {total_elapsed:.2f} seconds", "SUCCESS")
    thread.log(f"Average time per step: {total_elapsed/num_steps:.2f} seconds", "INFO")
    thread.log("=" * 50, "INFO")

    return {
        'completed': True,
        'stopped': False,
        'final_progress': 100,
        'elapsed_time': total_elapsed,
        'num_steps': num_steps,
        'task_name': task_name
    }
