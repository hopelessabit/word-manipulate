"""
File Selection Manager
Handles file selection and determines available operations based on file types
"""

from pathlib import Path
from typing import List, Set, Optional, Dict
from enum import Enum


class FileType(Enum):
    """Supported file types"""
    DOCX = "docx"
    PDF = "pdf"
    UNKNOWN = "unknown"


class FileOperation(Enum):
    """Available file operations"""
    SPLIT = "split"
    MERGE = "merge"
    EXPORT_PDF = "export_pdf"
    RENAME = "rename"


class FileSelectionManager:
    """
    Manages file selection and determines which operations are available
    based on selected file types.
    """

    def __init__(self):
        """Initialize the file selection manager"""
        self.selected_files: List[str] = []
        self.file_types: Set[FileType] = set()
        self.available_operations: Set[FileOperation] = set()

    def set_files(self, file_paths: List[str]) -> Dict:
        """
        Set selected files and analyze their types.

        Args:
            file_paths: List of file paths

        Returns:
            Dictionary with selection info:
                - total_files: int
                - docx_count: int
                - pdf_count: int
                - unknown_count: int
                - available_operations: List[str]
                - all_docx: bool
                - has_pdf: bool
        """
        self.selected_files = [str(Path(f).resolve()) for f in file_paths]
        self.file_types.clear()

        # Analyze file types
        docx_count = 0
        pdf_count = 0
        unknown_count = 0

        for file_path in self.selected_files:
            file_type = self._get_file_type(file_path)
            self.file_types.add(file_type)

            if file_type == FileType.DOCX:
                docx_count += 1
            elif file_type == FileType.PDF:
                pdf_count += 1
            else:
                unknown_count += 1

        # Determine available operations
        self._update_available_operations()

        # Prepare result
        all_docx = docx_count == len(self.selected_files) and docx_count > 0
        has_pdf = pdf_count > 0

        return {
            'total_files': len(self.selected_files),
            'docx_count': docx_count,
            'pdf_count': pdf_count,
            'unknown_count': unknown_count,
            'available_operations': [op.value for op in self.available_operations],
            'all_docx': all_docx,
            'has_pdf': has_pdf,
            'file_types': list(set(ft.value for ft in self.file_types if ft != FileType.UNKNOWN))
        }

    def _get_file_type(self, file_path: str) -> FileType:
        """
        Determine file type from extension.

        Args:
            file_path: Path to file

        Returns:
            FileType enum value
        """
        path = Path(file_path)
        extension = path.suffix.lower()

        if extension == '.docx':
            return FileType.DOCX
        elif extension == '.pdf':
            return FileType.PDF
        else:
            return FileType.UNKNOWN

    def _update_available_operations(self):
        """
        Update available operations based on selected file types.

        Rules:
        - All files are DOCX: Enable all operations (split, merge, export_pdf, rename)
        - Mixed or PDF files: Only enable rename
        """
        self.available_operations.clear()

        # No files selected
        if not self.selected_files:
            return

        # Check if all files are DOCX
        all_docx = (len(self.file_types) == 1 and
                   FileType.DOCX in self.file_types)

        if all_docx:
            # All files are DOCX - enable all operations
            self.available_operations.add(FileOperation.SPLIT)
            self.available_operations.add(FileOperation.MERGE)
            self.available_operations.add(FileOperation.EXPORT_PDF)
            self.available_operations.add(FileOperation.RENAME)
        else:
            # Mixed types or PDF files - only rename available
            self.available_operations.add(FileOperation.RENAME)

    def is_operation_available(self, operation: FileOperation) -> bool:
        """
        Check if an operation is available for current selection.

        Args:
            operation: FileOperation to check

        Returns:
            True if operation is available
        """
        return operation in self.available_operations

    def get_file_info(self, file_path: str) -> Dict:
        """
        Get information about a specific file.

        Args:
            file_path: Path to file

        Returns:
            Dictionary with file info:
                - path: str
                - name: str
                - extension: str
                - type: str
                - size: int (bytes)
                - exists: bool
        """
        path = Path(file_path)

        return {
            'path': str(path.resolve()),
            'name': path.name,
            'stem': path.stem,
            'extension': path.suffix,
            'type': self._get_file_type(str(path)).value,
            'size': path.stat().st_size if path.exists() else 0,
            'exists': path.exists(),
            'parent': str(path.parent)
        }

    def get_all_files_info(self) -> List[Dict]:
        """
        Get information about all selected files.

        Returns:
            List of file info dictionaries
        """
        return [self.get_file_info(f) for f in self.selected_files]

    def clear_selection(self):
        """Clear all selected files"""
        self.selected_files.clear()
        self.file_types.clear()
        self.available_operations.clear()

    def add_files(self, file_paths: List[str]) -> Dict:
        """
        Add files to current selection.

        Args:
            file_paths: List of file paths to add

        Returns:
            Updated selection info
        """
        current = set(self.selected_files)
        new_files = [str(Path(f).resolve()) for f in file_paths]
        current.update(new_files)

        return self.set_files(list(current))

    def remove_files(self, file_paths: List[str]) -> Dict:
        """
        Remove files from current selection.

        Args:
            file_paths: List of file paths to remove

        Returns:
            Updated selection info
        """
        to_remove = set(str(Path(f).resolve()) for f in file_paths)
        remaining = [f for f in self.selected_files if f not in to_remove]

        return self.set_files(remaining)

    def validate_for_operation(self, operation: FileOperation) -> tuple:
        """
        Validate if current selection is valid for an operation.

        Args:
            operation: Operation to validate

        Returns:
            Tuple of (is_valid: bool, message: str)
        """
        if not self.selected_files:
            return False, "No files selected"

        if not self.is_operation_available(operation):
            return False, f"Operation '{operation.value}' is not available for current selection"

        # Operation-specific validation
        if operation == FileOperation.SPLIT:
            if len(self.selected_files) == 0:
                return False, "Select at least one file to split"
            # All must be DOCX (already checked by is_operation_available)
            return True, f"Ready to split {len(self.selected_files)} file(s)"

        elif operation == FileOperation.MERGE:
            if len(self.selected_files) < 2:
                return False, "Select at least 2 files to merge"
            return True, f"Ready to merge {len(self.selected_files)} files"

        elif operation == FileOperation.EXPORT_PDF:
            if len(self.selected_files) == 0:
                return False, "Select at least one file to export"
            return True, f"Ready to export {len(self.selected_files)} file(s) to PDF"

        elif operation == FileOperation.RENAME:
            if len(self.selected_files) == 0:
                return False, "Select at least one file to rename"
            return True, f"Ready to rename {len(self.selected_files)} file(s)"

        return True, "Valid"

    def get_operation_button_state(self) -> Dict[str, bool]:
        """
        Get the enabled/disabled state for all operation buttons.

        Returns:
            Dictionary mapping operation names to enabled state
        """
        return {
            'split': self.is_operation_available(FileOperation.SPLIT),
            'merge': self.is_operation_available(FileOperation.MERGE),
            'export_pdf': self.is_operation_available(FileOperation.EXPORT_PDF),
            'rename': self.is_operation_available(FileOperation.RENAME)
        }

    def get_selection_summary(self) -> str:
        """
        Get a human-readable summary of current selection.

        Returns:
            Summary string
        """
        if not self.selected_files:
            return "No files selected"

        info = self.set_files(self.selected_files)

        parts = []
        parts.append(f"Total: {info['total_files']} file(s)")

        if info['docx_count'] > 0:
            parts.append(f"DOCX: {info['docx_count']}")
        if info['pdf_count'] > 0:
            parts.append(f"PDF: {info['pdf_count']}")
        if info['unknown_count'] > 0:
            parts.append(f"Other: {info['unknown_count']}")

        # Add available operations
        if info['all_docx']:
            parts.append("✓ All operations available")
        else:
            parts.append("✓ Rename only")

        return " | ".join(parts)


# Singleton instance for easy access
_file_selection_manager = None

def get_file_selection_manager() -> FileSelectionManager:
    """Get or create the global file selection manager instance"""
    global _file_selection_manager
    if _file_selection_manager is None:
        _file_selection_manager = FileSelectionManager()
    return _file_selection_manager

