# -*- coding: utf-8 -*-
"""
xml_merger_optimized.py
-----------------------
Optimized XML-based document merger that prioritizes speed while maintaining format.
Uses docxcompose for the core merge operation which the user confirmed works well.
"""

import os
import time
from typing import List, Optional, Callable, Dict
from pathlib import Path
from docx import Document
from docxcompose.composer import Composer


class OptimizedXMLMerger:
    """
    Optimized merger using docxcompose which user confirmed works best.
    Focuses on speed and format preservation.
    """

    def __init__(self, progress_callback: Optional[Callable] = None,
                 log_callback: Optional[Callable] = None):
        """
        Initialize optimized merger.

        Args:
            progress_callback: Callback(progress: float, message: str)
            log_callback: Callback(message: str, level: str)
        """
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.preserve_first_margins = True  # Option to preserve first file's margins

        # Statistics
        self.stats = {
            "files_processed": 0,
            "total_time": 0,
            "errors": []
        }

    def _log(self, message: str, level: str = "INFO"):
        """Log a message"""
        if self.log_callback:
            self.log_callback(message, level)
        else:
            print(f"[{level}] {message}")

    def _update_progress(self, progress: float, message: str = ""):
        """Update progress"""
        if self.progress_callback:
            self.progress_callback(progress, message)

    def merge_documents(self, file_list: List[str], output_path: str) -> bool:
        """
        Merge documents using docxcompose (confirmed working by user).

        Args:
            file_list: List of DOCX files to merge
            output_path: Output file path

        Returns:
            bool: True if successful
        """
        try:
            if not file_list or len(file_list) == 0:
                self._log("No files to merge", "ERROR")
                return False

            if len(file_list) == 1:
                self._log("Only one file provided, copying to output", "INFO")
                import shutil
                shutil.copy2(file_list[0], output_path)
                return True

            start_time = time.time()

            self._log("="*60, "INFO")
            self._log(f"MERGING {len(file_list)} FILES", "INFO")
            self._log("="*60, "INFO")

            self._update_progress(0, "Starting merge")

            # Step 1: Load master document (5%)
            self._log(f"\n[Step 1/{len(file_list)+2}] Loading master document", "INFO")
            self._log(f"  File: {Path(file_list[0]).name}", "INFO")
            self._update_progress(5, "Loading master document")

            load_start = time.time()
            master = Document(file_list[0])
            load_time = time.time() - load_start
            self._log(f"  ✓ Loaded in {load_time:.3f}s", "SUCCESS")

            # Extract and store first file's page settings
            first_section = master.sections[0] if master.sections else None

            # Create composer
            composer = Composer(master)
            self.stats["files_processed"] = 1

            # Step 2: Append remaining files (5% to 85%)
            progress_per_file = 80.0 / max(1, len(file_list) - 1)
            file_times = []

            for i, file_path in enumerate(file_list[1:], 1):
                file_name = Path(file_path).name
                current_progress = 5 + (i * progress_per_file)

                self._log(f"\n[Step {i+1}/{len(file_list)+2}] Merging file {i}/{len(file_list)-1}", "INFO")
                self._log(f"  File: {file_name}", "INFO")
                self._update_progress(current_progress, f"Merging {file_name}")

                try:
                    append_start = time.time()
                    
                    # Load document
                    self._log(f"  [1/2] Loading document...", "INFO")
                    doc = Document(file_path)
                    load_time_sub = time.time() - append_start
                    self._log(f"        Loaded in {load_time_sub:.3f}s", "DEBUG")

                    # Append using composer
                    self._log(f"  [2/2] Appending to master...", "INFO")
                    append_op_start = time.time()
                    composer.append(doc)
                    append_time_sub = time.time() - append_op_start
                    self._log(f"        Appended in {append_time_sub:.3f}s", "DEBUG")

                    total_file_time = time.time() - append_start
                    file_times.append((file_name, total_file_time))
                    self._log(f"  ✓ Completed in {total_file_time:.3f}s", "SUCCESS")

                    self.stats["files_processed"] += 1

                except Exception as e:
                    self._log(f"  ✗ ERROR: {str(e)}", "ERROR")
                    self.stats["errors"].append(f"{file_name}: {str(e)}")
                    # Continue with next file even if one fails

            # Step 3: Apply first file's page settings (85% to 90%)
            self._log(f"\n[Step {len(file_list)+1}/{len(file_list)+2}] Applying page settings", "INFO")

            if self.preserve_first_margins and first_section:
                self._log("  Preserving margins from first file", "INFO")
                self._update_progress(90, "Applying page settings")

                settings_start = time.time()
                for idx, section in enumerate(composer.doc.sections):
                    try:
                        section.top_margin = first_section.top_margin
                        section.bottom_margin = first_section.bottom_margin
                        section.left_margin = first_section.left_margin
                        section.right_margin = first_section.right_margin
                        section.header_distance = first_section.header_distance
                        section.footer_distance = first_section.footer_distance
                    except:
                        pass  # Continue even if some settings fail

                settings_time = time.time() - settings_start
                self._log(f"  ✓ Applied to {len(composer.doc.sections)} section(s) in {settings_time:.3f}s", "SUCCESS")
            else:
                self._log("  Skipping page margin preservation (user option)", "INFO")
                self._update_progress(90, "Finalizing")

            # Step 4: Save (90% to 100%)
            self._log(f"\n[Step {len(file_list)+2}/{len(file_list)+2}] Saving merged document", "INFO")
            self._log(f"  Output: {output_path}", "INFO")
            self._update_progress(95, "Saving document")

            # Ensure output directory exists
            os.makedirs(Path(output_path).parent, exist_ok=True)

            save_start = time.time()
            composer.save(output_path)
            save_time = time.time() - save_start
            self._log(f"  ✓ Saved in {save_time:.3f}s", "SUCCESS")

            # Complete
            self._update_progress(100, "Complete")
            
            total_time = time.time() - start_time
            self.stats["total_time"] = total_time

            # Final summary
            self._log("\n" + "="*60, "INFO")
            self._log("✓ MERGE COMPLETED SUCCESSFULLY", "SUCCESS")
            self._log("="*60, "INFO")
            self._log(f"Files merged: {self.stats['files_processed']}/{len(file_list)}", "INFO")
            self._log(f"Total time: {total_time:.3f}s", "INFO")
            self._log(f"Average time per file: {(total_time/len(file_list)):.3f}s", "INFO")
            self._log(f"Output: {output_path}", "INFO")
            
            # Show per-file timing
            if file_times:
                self._log(f"\nPer-file timing:", "INFO")
                for fname, ftime in file_times:
                    self._log(f"  • {fname}: {ftime:.3f}s", "INFO")

            if self.stats["errors"]:
                self._log(f"\n⚠ Errors encountered: {len(self.stats['errors'])}", "WARNING")
                for err in self.stats["errors"]:
                    self._log(f"  - {err}", "WARNING")
            
            self._log("="*60, "INFO")

            return True

        except Exception as e:
            self._log(f"CRITICAL ERROR: {str(e)}", "ERROR")
            import traceback
            self._log(traceback.format_exc(), "ERROR")
            return False

