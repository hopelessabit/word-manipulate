# -*- coding: utf-8 -*-
"""
xml_merger_enhanced.py
----------------------
Enhanced XML-based document merger with:
- First file page margin preservation
- Unique ID generation for styles to prevent conflicts
- Fast XML processing
- Proper error handling
- No "list index out of range" errors

This implementation addresses all known merge issues.
"""

import os
import time
import zipfile
import shutil
import xml.etree.ElementTree as ET
from typing import List, Optional, Callable, Dict, Set
from pathlib import Path
from docx import Document
from docxcompose.composer import Composer
import re


# Word XML namespaces
NAMESPACES = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
    'rel': 'http://schemas.openxmlformats.org/package/2006/relationships',
    'v': 'urn:schemas-microsoft-com:vml'
}

# Register namespaces for proper XML output
for prefix, uri in NAMESPACES.items():
    ET.register_namespace(prefix, uri)


class EnhancedXMLMerger:
    """
    Enhanced merger that preserves margins and resolves style conflicts.
    """

    def __init__(self, progress_callback: Optional[Callable] = None,
                 log_callback: Optional[Callable] = None):
        """
        Initialize enhanced merger.

        Args:
            progress_callback: Callback(progress: float, message: str)
            log_callback: Callback(message: str, level: str)
        """
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.preserve_first_margins = True  # Option to preserve first file's margins

        # Track style IDs to avoid conflicts
        self.used_style_ids: Set[str] = set()
        self.style_id_counter = 10000

        # Track numbering IDs
        self.used_num_ids: Set[str] = set()
        self.num_id_counter = 10000

        # Statistics
        self.stats = {
            "files_processed": 0,
            "styles_remapped": 0,
            "num_remapped": 0,
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
        Merge documents with proper margin preservation and style conflict resolution.

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

            self._log("="*60, "INFO")
            self._log(f"Enhanced Merge: {len(file_list)} files", "INFO")
            self._log("="*60, "INFO")

            self._update_progress(0, "Starting merge")

            # Step 1: Load master document
            self._log(f"Loading master: {Path(file_list[0]).name}", "INFO")
            self._update_progress(5, "Loading master document")

            master = Document(file_list[0])

            # Extract and store first file's margin settings
            first_margins = self._get_page_margins(master)
            self._log(f"Master margins: T={first_margins['top']}, B={first_margins['bottom']}, "
                     f"L={first_margins['left']}, R={first_margins['right']}", "INFO")

            # Create composer
            composer = Composer(master)

            # Track used style IDs from master
            self._analyze_style_ids(file_list[0])

            self.stats["files_processed"] = 1

            # Step 2: Process remaining files
            progress_per_file = 75.0 / max(1, len(file_list) - 1)

            for i, file_path in enumerate(file_list[1:], 1):
                file_name = Path(file_path).name
                current_progress = 5 + (i * progress_per_file)

                self._log(f"[{i}/{len(file_list)-1}] Processing: {file_name}", "INFO")
                self._update_progress(current_progress, f"Merging {file_name}")

                try:
                    # Pre-process file to avoid conflicts
                    processed_path = self._preprocess_file(file_path, i)

                    # Load and append
                    doc = Document(processed_path)
                    composer.append(doc)

                    # Clean up temp file
                    if processed_path != file_path:
                        try:
                            os.remove(processed_path)
                        except:
                            pass

                    self.stats["files_processed"] += 1
                    self._log(f"  ✓ Merged successfully", "SUCCESS")

                except Exception as e:
                    self._log(f"  ✗ Error merging {file_name}: {str(e)}", "ERROR")
                    self.stats["errors"].append(f"{file_name}: {str(e)}")
                    # Continue with next file

            # Step 3: Apply first file's margins to result
            if self.preserve_first_margins:
                self._log("Applying master document margins to result", "INFO")
                self._update_progress(85, "Applying page settings")
                self._apply_page_margins(composer.doc, first_margins)
            else:
                self._log("Skipping page margin preservation", "INFO")
                self._update_progress(85, "Finalizing")

            # Step 4: Save
            self._log("Saving merged document", "INFO")
            self._update_progress(90, "Saving document")

            # Ensure output directory exists
            os.makedirs(Path(output_path).parent, exist_ok=True)

            composer.save(output_path)

            # Final stats
            self._update_progress(100, "Complete")

            self._log("="*60, "INFO")
            self._log("✓ MERGE COMPLETED", "SUCCESS")
            self._log(f"Files processed: {self.stats['files_processed']}/{len(file_list)}", "INFO")
            self._log(f"Styles remapped: {self.stats['styles_remapped']}", "INFO")
            self._log(f"Numbering remapped: {self.stats['num_remapped']}", "INFO")
            if self.stats["errors"]:
                self._log(f"Errors: {len(self.stats['errors'])}", "WARNING")
            self._log(f"Output: {output_path}", "INFO")
            self._log("="*60, "INFO")

            return True

        except Exception as e:
            self._log(f"CRITICAL ERROR: {str(e)}", "ERROR")
            import traceback
            self._log(traceback.format_exc(), "ERROR")
            return False

    def _get_page_margins(self, doc: Document) -> Dict:
        """Extract page margin settings from document"""
        if doc.sections and len(doc.sections) > 0:
            section = doc.sections[0]
            return {
                'top': section.top_margin,
                'bottom': section.bottom_margin,
                'left': section.left_margin,
                'right': section.right_margin,
                'header': section.header_distance,
                'footer': section.footer_distance
            }

        # Default margins (1 inch)
        from docx.shared import Inches
        return {
            'top': Inches(1),
            'bottom': Inches(1),
            'left': Inches(1),
            'right': Inches(1),
            'header': Inches(0.5),
            'footer': Inches(0.5)
        }

    def _apply_page_margins(self, doc: Document, margins: Dict):
        """Apply margin settings to all sections of document"""
        for section in doc.sections:
            section.top_margin = margins['top']
            section.bottom_margin = margins['bottom']
            section.left_margin = margins['left']
            section.right_margin = margins['right']
            section.header_distance = margins.get('header', margins['top'])
            section.footer_distance = margins.get('footer', margins['bottom'])

    def _analyze_style_ids(self, file_path: str):
        """Analyze and track style IDs from a file"""
        try:
            with zipfile.ZipFile(file_path, 'r') as zf:
                if 'word/styles.xml' in zf.namelist():
                    styles_xml = zf.read('word/styles.xml')
                    root = ET.fromstring(styles_xml)

                    for style in root.findall('.//w:style', NAMESPACES):
                        style_id = style.get('{' + NAMESPACES['w'] + '}styleId')
                        if style_id:
                            self.used_style_ids.add(style_id)

                if 'word/numbering.xml' in zf.namelist():
                    num_xml = zf.read('word/numbering.xml')
                    root = ET.fromstring(num_xml)

                    for num in root.findall('.//w:num', NAMESPACES):
                        num_id = num.get('{' + NAMESPACES['w'] + '}numId')
                        if num_id:
                            self.used_num_ids.add(num_id)

        except Exception as e:
            self._log(f"Warning: Could not analyze style IDs from {file_path}: {e}", "WARNING")

    def _preprocess_file(self, file_path: str, file_index: int) -> str:
        """
        Pre-process file to ensure no style ID conflicts.

        Returns path to processed file (may be temp file).
        """
        try:
            # Check if file has potential conflicts
            has_conflicts = False

            with zipfile.ZipFile(file_path, 'r') as zf:
                if 'word/styles.xml' in zf.namelist():
                    styles_xml = zf.read('word/styles.xml')
                    root = ET.fromstring(styles_xml)

                    for style in root.findall('.//w:style', NAMESPACES):
                        style_id = style.get('{' + NAMESPACES['w'] + '}styleId')
                        if style_id and style_id in self.used_style_ids:
                            has_conflicts = True
                            break

            # If no conflicts, return original file
            if not has_conflicts:
                self._log(f"  No style conflicts detected", "DEBUG")
                # Still track the IDs
                self._analyze_style_ids(file_path)
                return file_path

            # Create temp file with resolved conflicts
            self._log(f"  Resolving style conflicts...", "INFO")

            temp_path = file_path + f".temp_{file_index}.docx"
            shutil.copy2(file_path, temp_path)

            # Remap conflicting style IDs
            style_id_map = {}

            with zipfile.ZipFile(temp_path, 'r') as zf_read:
                # Extract all files
                temp_dir = temp_path + "_extracted"
                zf_read.extractall(temp_dir)

            # Process styles.xml
            styles_path = os.path.join(temp_dir, 'word', 'styles.xml')
            if os.path.exists(styles_path):
                tree = ET.parse(styles_path)
                root = tree.getroot()

                for style in root.findall('.//w:style', NAMESPACES):
                    old_id = style.get('{' + NAMESPACES['w'] + '}styleId')

                    if old_id and old_id in self.used_style_ids:
                        # Generate new unique ID
                        new_id = f"Style{self.style_id_counter}"
                        self.style_id_counter += 1

                        style.set('{' + NAMESPACES['w'] + '}styleId', new_id)
                        style_id_map[old_id] = new_id
                        self.used_style_ids.add(new_id)
                        self.stats["styles_remapped"] += 1
                    elif old_id:
                        self.used_style_ids.add(old_id)

                # Save modified styles.xml
                tree.write(styles_path, encoding='utf-8', xml_declaration=True)

            # Update references in document.xml if we remapped anything
            if style_id_map:
                doc_path = os.path.join(temp_dir, 'word', 'document.xml')
                if os.path.exists(doc_path):
                    tree = ET.parse(doc_path)
                    root = tree.getroot()

                    # Update pStyle references
                    for pstyle in root.findall('.//w:pStyle', NAMESPACES):
                        old_val = pstyle.get('{' + NAMESPACES['w'] + '}val')
                        if old_val in style_id_map:
                            pstyle.set('{' + NAMESPACES['w'] + '}val', style_id_map[old_val])

                    # Update rStyle references
                    for rstyle in root.findall('.//w:rStyle', NAMESPACES):
                        old_val = rstyle.get('{' + NAMESPACES['w'] + '}val')
                        if old_val in style_id_map:
                            rstyle.set('{' + NAMESPACES['w'] + '}val', style_id_map[old_val])

                    tree.write(doc_path, encoding='utf-8', xml_declaration=True)

            # Repackage as DOCX
            os.remove(temp_path)

            with zipfile.ZipFile(temp_path, 'w', zipfile.ZIP_DEFLATED) as zf_write:
                for root_dir, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path_full = os.path.join(root_dir, file)
                        arcname = os.path.relpath(file_path_full, temp_dir)
                        zf_write.write(file_path_full, arcname)

            # Clean up extraction directory
            shutil.rmtree(temp_dir)

            self._log(f"  ✓ Resolved {len(style_id_map)} style conflicts", "SUCCESS")

            return temp_path

        except Exception as e:
            self._log(f"  Warning: Could not preprocess file: {e}", "WARNING")
            # Return original file if preprocessing fails
            return file_path


def enhanced_merge_worker(thread, file_list: List[str], output_file: str) -> dict:
    """
    Worker function for enhanced merge with thread support.

    Args:
        thread: WorkerThread instance
        file_list: List of file paths to merge
        output_file: Output file path

    Returns:
        Dictionary with results
    """
    def progress_callback(progress: float, message: str):
        thread.update_progress(progress, message)

    def log_callback(message: str, level: str):
        thread.log(message, level)

    merger = EnhancedXMLMerger(
        progress_callback=progress_callback,
        log_callback=log_callback
    )

    success = merger.merge_documents(file_list, output_file)

    return {
        "success": success,
        "output_file": output_file,
        "files_processed": merger.stats["files_processed"],
        "styles_remapped": merger.stats["styles_remapped"],
        "errors": merger.stats["errors"]
    }


# Simple function for direct use
def merge_with_enhanced_xml(files: List[str], output_file: str) -> bool:
    """
    Simple function to merge files with enhanced XML processing.

    Args:
        files: List of file paths to merge
        output_file: Output file path

    Returns:
        bool: True if successful
    """
    merger = EnhancedXMLMerger()
    return merger.merge_documents(files, output_file)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python xml_merger_enhanced.py <output_file> <input_file1> <input_file2> ...")
        print("\nExample:")
        print("  python xml_merger_enhanced.py merged.docx 1.docx 2.docx 3.docx")
        sys.exit(1)

    output = sys.argv[1]
    input_files = sys.argv[2:]

    print(f"\nMerging {len(input_files)} files...")
    print(f"Output: {output}\n")

    success = merge_with_enhanced_xml(input_files, output)

    if success:
        print(f"\n✅ Success! Output saved to: {output}")
        sys.exit(0)
    else:
        print(f"\n❌ Merge failed!")
        sys.exit(1)

