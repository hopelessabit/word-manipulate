# -*- coding: utf-8 -*-
"""
document_merger.py
------------------
Document merger with threading support for UI integration.
Uses either optimized or safe XML merger based on user selection.
"""

import os
import time
from pathlib import Path
from typing import List, Dict
from logic.merge.xml.xml_merger_optimized import OptimizedXMLMerger
from logic.merge.xml.xml_merger_enhanced import EnhancedXMLMerger


def merge_documents_worker(thread, config: Dict):
    """
    Worker function to merge documents in a thread.

    Args:
        thread: ManagedThread instance
        config: Configuration dictionary with:
            - files: List of file paths to merge
            - output_path: Output file path
            - output_name: Base name for output file (optional)
    """
    overall_start = time.time()
    file_times = []  # Track time for each file

    try:
        files = config.get('files', [])
        output_path = config.get('output_path', '')
        output_name = config.get('output_name', 'merged_document.docx')
        merge_method = config.get('merge_method', 'optimized')  # 'optimized' or 'safe'
        preserve_first_margins = config.get('preserve_first_margins', True)

        if not files:
            thread.log("ERROR: No files to merge", "ERROR")
            return

        if not output_path:
            thread.log("ERROR: No output path specified", "ERROR")
            return

        # Ensure output directory exists
        os.makedirs(output_path, exist_ok=True)

        # Create full output file path
        full_output_path = os.path.join(output_path, output_name)

        # Log start
        thread.log("="*60)
        thread.log(f"MERGE OPERATION STARTED")
        thread.log(f"Files to merge: {len(files)}")
        thread.log(f"Method: {'Optimized (Fast)' if merge_method == 'optimized' else 'Safe (Conflict Resolution)'}")
        thread.log(f"Preserve first file margins: {'Yes' if preserve_first_margins else 'No'}")
        thread.log(f"Output: {full_output_path}")
        thread.log("="*60)

        # Update thread status
        thread.current_file = "Initializing"
        thread.current_task = "Merge Documents"
        thread.update_progress(0, "Starting merge operation")

        # Calculate total tasks for progress tracking
        # Total steps: Load master (1) + Append files (n-1) + Apply settings (1) + Save (1) = n+2
        thread.total_tasks = len(files)
        thread.processed_files = 0
        total_steps = len(files) + 2  # +2 for settings and save
        current_step = 0

        # Create merger with enhanced callbacks
        def progress_callback(progress: float, message: str):
            """Progress callback for merger"""
            thread.update_progress(progress, message)

        def log_callback(message: str, level: str = "INFO"):
            """Log callback for merger"""
            thread.log(message, level)

        # Select merger based on method
        if merge_method == 'safe':
            thread.log("Using Safe merger (with conflict resolution)", "INFO")
            merger = EnhancedXMLMerger(
                progress_callback=progress_callback,
                log_callback=log_callback
            )
        else:
            thread.log("Using Optimized merger (fast)", "INFO")
            merger = OptimizedXMLMerger(
                progress_callback=progress_callback,
                log_callback=log_callback
            )

        # Set preserve margins option
        if hasattr(merger, 'preserve_first_margins'):
            merger.preserve_first_margins = preserve_first_margins

        # Enhanced merge with per-file tracking
        thread.log("\n[Step 1/3] Loading and Merging Files...", "INFO")
        thread.current_file = Path(files[0]).name
        thread.update_sub_progress(0, "Loading master document")

        # Perform merge
        success = merger.merge_documents(files, full_output_path)

        total_time = time.time() - overall_start

        if success:
            thread.log("="*60)
            thread.log(f"✓ MERGE COMPLETED SUCCESSFULLY", "SUCCESS")
            thread.log(f"Total processing time: {total_time:.2f} seconds", "INFO")
            thread.log(f"Output: {full_output_path}", "INFO")

            # Show statistics
            if merger.stats:
                thread.log(f"\nStatistics:", "INFO")
                thread.log(f"  Files processed: {merger.stats.get('files_processed', 0)}/{len(files)}", "INFO")
                thread.log(f"  Total time: {merger.stats.get('total_time', 0):.2f}s", "INFO")

                if merger.stats.get('errors'):
                    thread.log(f"  Warnings: {len(merger.stats['errors'])}", "WARNING")
                    for err in merger.stats['errors']:
                        thread.log(f"    - {err}", "WARNING")

            thread.log("="*60)
            thread.update_progress(100, "Complete")
            # Thread will be marked as completed automatically by the run() method
        else:
            thread.log("="*60)
            thread.log("✗ MERGE FAILED", "ERROR")
            thread.log(f"Time: {total_time:.2f} seconds", "ERROR")
            thread.log("="*60)
            thread.update_progress(0, "Failed")
            # Thread will be marked as failed automatically

    except Exception as e:
        thread.log(f"CRITICAL ERROR: {str(e)}", "ERROR")
        import traceback
        thread.log(traceback.format_exc(), "ERROR")
        thread.update_progress(0, "Error")
        # Thread will be marked as failed automatically by the run() method


def merge_documents_simple(files: List[str], output_path: str) -> bool:
    """
    Simple merge function without threading support.

    Args:
        files: List of file paths to merge
        output_path: Full path to output file

    Returns:
        bool: True if successful
    """
    try:
        print(f"\n{'='*60}")
        print(f"MERGING {len(files)} FILES")
        print(f"{'='*60}\n")

        for i, f in enumerate(files, 1):
            print(f"  [{i}] {Path(f).name}")

        print(f"\nOutput: {output_path}\n")

        merger = OptimizedXMLMerger()

        start_time = time.time()
        success = merger.merge_documents(files, output_path)
        elapsed = time.time() - start_time

        if success:
            print(f"\n{'='*60}")
            print(f"✓ MERGE COMPLETED")
            print(f"Time: {elapsed:.2f} seconds")
            print(f"{'='*60}\n")
            return True
        else:
            print(f"\n{'='*60}")
            print(f"✗ MERGE FAILED")
            print(f"{'='*60}\n")
            return False

    except Exception as e:
        print(f"\nERROR: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False

