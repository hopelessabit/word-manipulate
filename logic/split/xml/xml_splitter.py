# -*- coding: utf-8 -*-
"""
xml_splitter.py
---------------
XML-based document splitter for split exam documents into:
 - DE (Question) files
 - GIAI (Solution) files

Optimized with progress tracking and logging support for multi-threaded execution.
"""

from docx import Document
import os
import copy
import re
from typing import List, Optional, Callable
from pathlib import Path


class XMLDocumentSplitter:
    """
    Handles split of exam documents into question and solution files.
    Supports progress callbacks and detailed logging.
    """

    def __init__(self, progress_callback: Optional[Callable] = None,
                 log_callback: Optional[Callable] = None):
        """
        Initialize the XML document splitter.

        Args:
            progress_callback: Callback function(progress: float, message: str)
            log_callback: Callback function(message: str, level: str)
        """
        self.progress_callback = progress_callback
        self.log_callback = log_callback

        # Configuration
        self.split_marker = "HƯỚNG DẪN GIẢI CHI TIẾT"
        self.header_markers = ["BÀI:", "ĐỀ TEST"]

    def log(self, message: str, level: str = "INFO"):
        """Log a message if callback is provided"""
        if self.log_callback:
            self.log_callback(message, level)
        else:
            print(f"[{level}] {message}")

    def update_progress(self, progress: float, message: str = ""):
        """Update progress if callback is provided"""
        if self.progress_callback:
            self.progress_callback(progress, message)

    @staticmethod
    def get_full_text(element) -> str:
        """
        Extract all text from an element (paragraph/table).
        Returns uppercase for easier searching.

        Args:
            element: XML element to extract text from

        Returns:
            Concatenated text in uppercase
        """
        texts = []
        for node in element.iter():
            if node.text:
                texts.append(node.text)
        return "".join(texts).upper()

    def clean_first_paragraph_deeply(self, doc: Document) -> None:
        """
        Remove garbage shapes from the first paragraph while preserving section info.

        - If first paragraph contains <w:sectPr> (section info), only clean content
        - If no sectPr, remove entire first paragraph

        Args:
            doc: Document to clean
        """
        body = doc.element.body

        if len(body) == 0:
            self.log("Document body is empty, skipping cleanup", "WARNING")
            return

        first_p = body[0]

        # Only process paragraph elements
        if not first_p.tag.endswith('p'):
            self.log("First element is not a paragraph, skipping", "INFO")
            return

        xml_str = first_p.xml

        # Check if paragraph contains section properties
        if "w:sectPr" in xml_str:
            self.log("First paragraph contains <w:sectPr>, preserving section info", "INFO")

            # Keep paragraph but clean content
            children = list(first_p)

            # Find and remove relationship IDs for images/shapes
            rids = re.findall(r'(?:r:id|r:embed)="([^"]+)"', xml_str)
            if rids:
                self.log(f"Found {len(rids)} embedded objects to remove", "INFO")
                for rid in rids:
                    try:
                        if rid in doc.part.rels:
                            doc.part.rels.pop(rid)
                            self.log(f"Removed relationship: {rid}", "DEBUG")
                    except Exception as e:
                        self.log(f"Could not remove rId {rid}: {e}", "WARNING")

            # Remove all children except sectPr
            for child in children:
                if not child.tag.endswith("sectPr"):
                    first_p.remove(child)

            self.log("Cleaned first paragraph content (preserved sectPr)", "SUCCESS")
            return

        # Normal case: remove entire first paragraph
        rids = re.findall(r'(?:r:id|r:embed)="([^"]+)"', xml_str)
        if rids:
            self.log(f"Found {len(rids)} embedded objects in header", "INFO")
            for rid in rids:
                try:
                    if rid in doc.part.rels:
                        doc.part.rels.pop(rid)
                except Exception as e:
                    self.log(f"Warning: Could not remove rId {rid}: {e}", "WARNING")

        body.remove(first_p)
        self.log("Removed first paragraph (no sectPr)", "SUCCESS")

    def build_question_file(self, master_doc: Document, output_path: str) -> bool:
        """
        Create question (DE) file from master document.

        Keeps: Beginning -> before solution marker
        Removes: Solution section

        Args:
            master_doc: Source document
            output_path: Output file path

        Returns:
            True if successful, False otherwise
        """
        try:
            self.log("Creating question file...", "INFO")
            self.update_progress(10, "Copying document for question file")

            doc_de = copy.deepcopy(master_doc)

            self.update_progress(20, "Cleaning embedded objects")
            self.clean_first_paragraph_deeply(doc_de)

            self.update_progress(40, "Locating solution marker")

            # Remove solution section
            body_de = doc_de.element.body
            found_split = False
            to_delete: List = []

            for element in body_de.iterchildren():
                if found_split:
                    to_delete.append(element)
                    continue

                if element.tag.endswith('p') or element.tag.endswith('tbl'):
                    xml_text = self.get_full_text(element)
                    if self.split_marker in xml_text:
                        found_split = True
                        # Remove this marker line from question file
                        to_delete.append(element)

            if not found_split:
                self.log(f"Solution marker '{self.split_marker}' not found - "
                        "question file may contain solution", "WARNING")

            self.update_progress(60, f"Removing {len(to_delete)} solution elements")

            for el in to_delete:
                body_de.remove(el)

            self.update_progress(80, "Saving question file")
            doc_de.save(output_path)

            self.update_progress(100, "Question file created")
            self.log(f"Successfully saved question file: {output_path}", "SUCCESS")
            return True

        except Exception as e:
            self.log(f"Error creating question file: {e}", "ERROR")
            return False

    def build_solution_file(self, master_doc: Document, output_path: str) -> bool:
        """
        Create solution (GIAI) file from master document.

        Keeps: Header + solution section
        Removes: Question content between header and solution

        Args:
            master_doc: Source document
            output_path: Output file path

        Returns:
            True if successful, False otherwise
        """
        try:
            self.log("Creating solution file...", "INFO")
            self.update_progress(10, "Copying document for solution file")

            doc_giai = copy.deepcopy(master_doc)

            self.update_progress(20, "Cleaning embedded objects")
            self.clean_first_paragraph_deeply(doc_giai)

            self.update_progress(40, "Identifying content regions")

            # Identify regions to remove
            body_giai = doc_giai.element.body
            children = list(body_giai.iterchildren())

            start_delete_idx = -1
            end_delete_idx = -1

            for i, element in enumerate(children):
                xml_text = self.get_full_text(element)

                # Find header to start deletion AFTER it
                for marker in self.header_markers:
                    if marker in xml_text:
                        start_delete_idx = i + 1
                        self.log(f"Found header marker '{marker}' at index {i}", "DEBUG")
                        break

                # Find solution marker to stop deletion BEFORE it
                if self.split_marker in xml_text:
                    end_delete_idx = i
                    self.log(f"Found solution marker at index {i}", "DEBUG")
                    break

            if start_delete_idx > 0 and end_delete_idx > start_delete_idx:
                nodes_to_remove = children[start_delete_idx:end_delete_idx]
                count = len(nodes_to_remove)

                self.log(f"Removing question content: indices {start_delete_idx} to {end_delete_idx - 1}", "INFO")
                self.update_progress(60, f"Removing {count} question elements")

                for node in nodes_to_remove:
                    body_giai.remove(node)
            else:
                self.log("Could not identify regions to remove (document structure may differ)", "WARNING")

            self.update_progress(80, "Saving solution file")
            doc_giai.save(output_path)

            self.update_progress(100, "Solution file created")
            self.log(f"Successfully saved solution file: {output_path}", "SUCCESS")
            return True

        except Exception as e:
            self.log(f"Error creating solution file: {e}", "ERROR")
            return False

    def split_exam_file(self, input_path: str, output_dir: Optional[str] = None) -> dict:
        """
        Split an exam file into question and solution files.

        Args:
            input_path: Path to input file
            output_dir: Output directory (default: same as input)

        Returns:
            Dictionary with results:
                - success: bool
                - question_file: str (path)
                - solution_file: str (path)
                - error: str (if failed)
        """
        try:
            self.log(f"Starting split process for: {input_path}", "INFO")
            self.update_progress(0, "Initializing split process")

            # Validate input
            if not os.path.exists(input_path):
                error_msg = f"Input file not found: {input_path}"
                self.log(error_msg, "ERROR")
                return {"success": False, "error": error_msg}

            # Prepare output paths
            input_file = Path(input_path)
            base_name = input_file.stem

            if output_dir is None:
                output_dir = str(input_file.parent)

            output_dir_path = Path(output_dir)
            output_dir_path.mkdir(parents=True, exist_ok=True)

            path_de = output_dir_path / f"DE_{base_name}.docx"
            path_giai = output_dir_path / f"GIAI_{base_name}.docx"

            self.log(f"Output directory: {output_dir}", "INFO")
            self.log(f"Question file: {path_de.name}", "INFO")
            self.log(f"Solution file: {path_giai.name}", "INFO")

            # Load master document
            self.update_progress(5, "Loading master document")
            master_doc = Document(input_path)
            self.log("Master document loaded successfully", "SUCCESS")

            # Create question file
            self.update_progress(10, "Creating question file")
            success_de = self.build_question_file(master_doc, str(path_de))

            if not success_de:
                return {
                    "success": False,
                    "error": "Failed to create question file"
                }

            # Create solution file
            self.update_progress(50, "Creating solution file")
            success_giai = self.build_solution_file(master_doc, str(path_giai))

            if not success_giai:
                return {
                    "success": False,
                    "error": "Failed to create solution file"
                }

            self.update_progress(100, "Split process completed")
            self.log("Split process completed successfully", "SUCCESS")

            return {
                "success": True,
                "question_file": str(path_de),
                "solution_file": str(path_giai),
                "files_created": [str(path_de), str(path_giai)]
            }

        except Exception as e:
            error_msg = f"Error during split process: {e}"
            self.log(error_msg, "ERROR")
            return {
                "success": False,
                "error": error_msg
            }


# Worker function for threading integration
def xml_split_worker(thread, input_file: str, output_dir: Optional[str] = None) -> dict:
    """
    Worker function for split XML documents with thread support.

    Args:
        thread: WorkerThread instance
        input_file: Path to input file
        output_dir: Output directory

    Returns:
        Dictionary with results
    """
    def progress_callback(progress: float, message: str):
        thread.update_progress(progress, message)

    def log_callback(message: str, level: str):
        thread.log(message, level)

    splitter = XMLDocumentSplitter(
        progress_callback=progress_callback,
        log_callback=log_callback
    )

    return splitter.split_exam_file(input_file, output_dir)

