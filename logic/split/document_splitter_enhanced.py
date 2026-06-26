# -*- coding: utf-8 -*-
"""
document_splitter_enhanced.py
------------------------------
Enhanced document splitter with:
- Safe removal of first <w:r> containing shapes (no corruption)
- Effective removal of unnecessary images/objects
- Proper sectPr preservation to avoid "list index out of range" errors
- Better XML handling
"""

import os
import zipfile
import shutil
import xml.etree.ElementTree as ET
import re
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from docx import Document


# Word XML namespaces
NAMESPACES = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
    'v': 'urn:schemas-microsoft-com:vml',
    'pic': 'http://schemas.openxmlformats.org/drawingml/2006/picture'
}

for prefix, uri in NAMESPACES.items():
    ET.register_namespace(prefix, uri)


class EnhancedDocumentSplitter:
    """
    Enhanced splitter with safe shape/object removal and proper XML handling.
    """

    def __init__(self, log_callback=None):
        """
        Initialize enhanced splitter.

        Args:
            log_callback: Callback(message: str, level: str)
        """
        self.log_callback = log_callback
        self.stats = {
            "shapes_removed": 0,
            "images_removed": 0,
            "relationships_cleaned": 0
        }

    def _log(self, message: str, level: str = "INFO"):
        """Log a message"""
        if self.log_callback:
            self.log_callback(message, level)
        else:
            print(f"[{level}] {message}")

    def remove_first_shape_safely(self, file_path: str, output_path: str) -> bool:
        """
        Safely remove first paragraph's shapes while preserving document structure.

        This prevents "list index out of range" errors during merge by:
        1. Preserving sectPr if present
        2. Only removing drawing/picture elements
        3. Keeping paragraph structure intact

        Args:
            file_path: Input DOCX file
            output_path: Output DOCX file

        Returns:
            bool: True if successful
        """
        try:
            self._log(f"Processing: {Path(file_path).name}", "INFO")

            # Extract DOCX to temp directory
            temp_dir = output_path + "_temp"

            with zipfile.ZipFile(file_path, 'r') as zf:
                zf.extractall(temp_dir)

            # Process document.xml
            doc_path = os.path.join(temp_dir, 'word', 'document.xml')
            tree = ET.parse(doc_path)
            root = tree.getroot()

            # Find body
            body = root.find('.//w:body', NAMESPACES)
            if body is None:
                self._log("No body found in document", "ERROR")
                shutil.rmtree(temp_dir)
                return False

            # Find first paragraph
            first_para = body.find('.//w:p', NAMESPACES)
            if first_para is None:
                self._log("No paragraphs found", "WARNING")
                shutil.rmtree(temp_dir)
                return False

            # Check if first paragraph has sectPr
            has_sectp = first_para.find('.//w:sectPr', NAMESPACES) is not None

            if has_sectp:
                self._log("  First paragraph contains sectPr - using safe removal", "INFO")
                removed = self._safe_remove_from_paragraph(first_para)
            else:
                self._log("  First paragraph has no sectPr - can remove paragraph", "INFO")
                removed = self._count_objects_in_paragraph(first_para)
                body.remove(first_para)

            self.stats["shapes_removed"] += removed

            # Save modified document.xml
            tree.write(doc_path, encoding='utf-8', xml_declaration=True)

            # Clean up relationships
            rels_removed = self._clean_unused_relationships(temp_dir)
            self.stats["relationships_cleaned"] += rels_removed

            # Repackage as DOCX
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf_write:
                for root_dir, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path_full = os.path.join(root_dir, file)
                        arcname = os.path.relpath(file_path_full, temp_dir)
                        zf_write.write(file_path_full, arcname)

            # Clean up
            shutil.rmtree(temp_dir)

            self._log(f"  ✓ Removed {removed} objects, cleaned {rels_removed} relationships", "SUCCESS")
            return True

        except Exception as e:
            self._log(f"Error: {str(e)}", "ERROR")
            import traceback
            self._log(traceback.format_exc(), "ERROR")

            # Clean up on error
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

            return False

    def _safe_remove_from_paragraph(self, para_element) -> int:
        """
        Safely remove shapes/images from paragraph while preserving sectPr.

        Returns:
            int: Number of objects removed
        """
        removed_count = 0

        # Get all run elements
        runs = para_element.findall('.//w:r', NAMESPACES)

        for run in runs:
            # Remove drawing elements (shapes, charts)
            for drawing in run.findall('.//w:drawing', NAMESPACES):
                run.remove(drawing)
                removed_count += 1

            # Remove picture elements (VML)
            for pict in run.findall('.//w:pict', NAMESPACES):
                run.remove(pict)
                removed_count += 1

            # Remove object elements (embedded objects)
            for obj in run.findall('.//w:object', NAMESPACES):
                run.remove(obj)
                removed_count += 1

            # If run is now empty (no text, no images), we can remove it
            # but keep at least one run for structure
            has_text = run.find('.//w:t', NAMESPACES) is not None
            has_children = len(list(run)) > 0

            if not has_text and not has_children:
                # Check if this is the last run
                all_runs = para_element.findall('.//w:r', NAMESPACES)
                if len(all_runs) > 1:
                    para_element.remove(run)

        return removed_count

    def _count_objects_in_paragraph(self, para_element) -> int:
        """Count objects in paragraph"""
        count = 0

        count += len(para_element.findall('.//w:drawing', NAMESPACES))
        count += len(para_element.findall('.//w:pict', NAMESPACES))
        count += len(para_element.findall('.//w:object', NAMESPACES))

        return count

    def _clean_unused_relationships(self, extracted_dir: str) -> int:
        """
        Clean unused relationships after removing objects.

        Returns:
            int: Number of relationships cleaned
        """
        try:
            doc_xml_path = os.path.join(extracted_dir, 'word', 'document.xml')
            rels_path = os.path.join(extracted_dir, 'word', '_rels', 'document.xml.rels')

            if not os.path.exists(rels_path):
                return 0

            # Get all relationship IDs used in document
            tree = ET.parse(doc_xml_path)
            doc_root = tree.getroot()

            # Find all r:embed and r:id references
            used_ids = set()

            # Search in the entire document
            doc_str = ET.tostring(doc_root, encoding='unicode')
            id_pattern = re.compile(r'r:(?:id|embed)="([^"]+)"')
            used_ids.update(id_pattern.findall(doc_str))

            # Load relationships
            rels_tree = ET.parse(rels_path)
            rels_root = rels_tree.getroot()

            # Remove unused relationships
            removed = 0
            for rel in list(rels_root):
                rel_id = rel.get('Id')
                rel_type = rel.get('Type', '')

                # Keep if used or if it's a critical relationship
                if rel_id in used_ids:
                    continue

                # Don't remove critical relationships
                if any(critical in rel_type for critical in ['styles', 'numbering', 'settings', 'fontTable', 'theme']):
                    continue

                # Remove if it's an image/media relationship
                if 'image' in rel_type.lower() or 'media' in rel_type.lower():
                    rels_root.remove(rel)
                    removed += 1

                    # Also remove the actual file
                    target = rel.get('Target', '')
                    if target:
                        target_path = os.path.join(extracted_dir, 'word', target)
                        if os.path.exists(target_path):
                            try:
                                os.remove(target_path)
                            except:
                                pass

            # Save modified relationships
            if removed > 0:
                rels_tree.write(rels_path, encoding='utf-8', xml_declaration=True)

            return removed

        except Exception as e:
            self._log(f"Warning: Could not clean relationships: {e}", "WARNING")
            return 0

    def remove_all_unnecessary_objects(self, file_path: str, output_path: str,
                                      remove_headers: bool = True,
                                      remove_footers: bool = True) -> bool:
        """
        Remove all unnecessary objects from document.

        Args:
            file_path: Input file
            output_path: Output file
            remove_headers: Remove headers
            remove_footers: Remove footers

        Returns:
            bool: True if successful
        """
        try:
            self._log(f"Cleaning document: {Path(file_path).name}", "INFO")

            # Extract
            temp_dir = output_path + "_temp"
            with zipfile.ZipFile(file_path, 'r') as zf:
                zf.extractall(temp_dir)

            # Process document.xml
            doc_path = os.path.join(temp_dir, 'word', 'document.xml')
            tree = ET.parse(doc_path)
            root = tree.getroot()

            # Remove all drawings and pictures
            body = root.find('.//w:body', NAMESPACES)
            if body is not None:
                # Remove from all paragraphs
                for para in body.findall('.//w:p', NAMESPACES):
                    removed = self._safe_remove_from_paragraph(para)
                    self.stats["shapes_removed"] += removed

            # Save document.xml
            tree.write(doc_path, encoding='utf-8', xml_declaration=True)

            # Clean headers/footers if requested
            if remove_headers:
                self._clean_headers(temp_dir)

            if remove_footers:
                self._clean_footers(temp_dir)

            # Clean relationships
            rels_removed = self._clean_unused_relationships(temp_dir)
            self.stats["relationships_cleaned"] += rels_removed

            # Repackage
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf_write:
                for root_dir, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path_full = os.path.join(root_dir, file)
                        arcname = os.path.relpath(file_path_full, temp_dir)
                        zf_write.write(file_path_full, arcname)

            # Clean up
            shutil.rmtree(temp_dir)

            self._log(f"  ✓ Cleaned successfully", "SUCCESS")
            return True

        except Exception as e:
            self._log(f"Error: {str(e)}", "ERROR")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            return False

    def _clean_headers(self, extracted_dir: str):
        """Remove content from headers"""
        word_dir = os.path.join(extracted_dir, 'word')

        for file in os.listdir(word_dir):
            if file.startswith('header') and file.endswith('.xml'):
                header_path = os.path.join(word_dir, file)
                try:
                    tree = ET.parse(header_path)
                    root = tree.getroot()

                    # Clear all paragraphs
                    for para in root.findall('.//w:p', NAMESPACES):
                        # Keep paragraph structure, remove content
                        for child in list(para):
                            if not child.tag.endswith('pPr'):  # Keep paragraph properties
                                para.remove(child)

                    tree.write(header_path, encoding='utf-8', xml_declaration=True)
                except:
                    pass

    def _clean_footers(self, extracted_dir: str):
        """Remove content from footers"""
        word_dir = os.path.join(extracted_dir, 'word')

        for file in os.listdir(word_dir):
            if file.startswith('footer') and file.endswith('.xml'):
                footer_path = os.path.join(word_dir, file)
                try:
                    tree = ET.parse(footer_path)
                    root = tree.getroot()

                    # Clear all paragraphs
                    for para in root.findall('.//w:p', NAMESPACES):
                        # Keep paragraph structure, remove content
                        for child in list(para):
                            if not child.tag.endswith('pPr'):
                                para.remove(child)

                    tree.write(footer_path, encoding='utf-8', xml_declaration=True)
                except:
                    pass


# Convenience functions

def safe_remove_first_shape(input_file: str, output_file: str) -> bool:
    """
    Convenience function to safely remove first shape.

    Args:
        input_file: Input DOCX
        output_file: Output DOCX

    Returns:
        bool: True if successful
    """
    splitter = EnhancedDocumentSplitter()
    return splitter.remove_first_shape_safely(input_file, output_file)


def clean_document_objects(input_file: str, output_file: str,
                           remove_headers: bool = True,
                           remove_footers: bool = True) -> bool:
    """
    Convenience function to clean all unnecessary objects.

    Args:
        input_file: Input DOCX
        output_file: Output DOCX
        remove_headers: Remove headers
        remove_footers: Remove footers

    Returns:
        bool: True if successful
    """
    splitter = EnhancedDocumentSplitter()
    return splitter.remove_all_unnecessary_objects(input_file, output_file,
                                                   remove_headers, remove_footers)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage:")
        print("  python document_splitter_enhanced.py <input.docx> <output.docx> [--clean-all]")
        print("\nOptions:")
        print("  --clean-all    Remove all objects (not just first paragraph)")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    clean_all = '--clean-all' in sys.argv

    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        sys.exit(1)

    print(f"\nProcessing: {input_file}")
    print(f"Output: {output_file}")
    print(f"Mode: {'Clean all objects' if clean_all else 'Remove first shape only'}\n")

    splitter = EnhancedDocumentSplitter()

    if clean_all:
        success = splitter.remove_all_unnecessary_objects(input_file, output_file)
    else:
        success = splitter.remove_first_shape_safely(input_file, output_file)

    if success:
        print(f"\n✅ Success!")
        print(f"   Shapes removed: {splitter.stats['shapes_removed']}")
        print(f"   Relationships cleaned: {splitter.stats['relationships_cleaned']}")
        print(f"   Output: {output_file}")
        sys.exit(0)
    else:
        print(f"\n❌ Failed!")
        sys.exit(1)

