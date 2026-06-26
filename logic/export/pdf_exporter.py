# -*- coding: utf-8 -*-
"""
pdf_exporter.py
---------------
Export DOCX documents to PDF with format preservation.
Uses multi-threading for batch operations with robust Word COM handling.
"""

import os
import time
from pathlib import Path
from typing import List, Dict
import win32com.client
import win32com.client
import pythoncom


def convert_docx_to_pdf_robust(docx_path: str, pdf_path: str, max_retries: int = 2) -> bool:
    """
    Convert DOCX to PDF using Word COM with proper error handling and retries.

    Args:
        docx_path: Path to source DOCX file
        pdf_path: Path to output PDF file
        max_retries: Maximum number of retry attempts

    Returns:
        bool: True if successful

    Raises:
        Exception: If conversion fails after all retries
    """
    # Initialize COM for this thread
    pythoncom.CoInitialize()

    word = None
    doc = None
    attempt = 0

    try:
        while attempt <= max_retries:
            try:
                # Create Word application instance
                word = win32com.client.DispatchEx("Word.Application")
                word.Visible = False
                word.DisplayAlerts = 0  # wdAlertsNone

                # Open document
                doc = word.Documents.Open(str(Path(docx_path).absolute()))

                # Export to PDF (wdFormatPDF = 17)
                doc.SaveAs(str(Path(pdf_path).absolute()), FileFormat=17)

                # Close document
                doc.Close(False)
                doc = None

                # Quit Word
                word.Quit()
                word = None

                # Success!
                return True

            except Exception as e:
                attempt += 1

                # Clean up on error
                try:
                    if doc:
                        doc.Close(False)
                        doc = None
                except:
                    pass

                try:
                    if word:
                        word.Quit()
                        word = None
                except:
                    pass

                # If this was the last attempt, raise the error
                if attempt > max_retries:
                    raise Exception(f"Failed after {max_retries + 1} attempts: {str(e)}")

                # Wait a bit before retry
                time.sleep(1)

    finally:
        # Ensure cleanup
        try:
            if doc:
                doc.Close(False)
        except:
            pass

        try:
            if word:
                word.Quit()
        except:
            pass

        # Uninitialize COM
        try:
            pythoncom.CoUninitialize()
        except:
            pass

    return False


def export_to_pdf_worker(thread, config: Dict):
    """
    Worker function to export DOCX files to PDF in a thread.

    Args:
        thread: ManagedThread instance
        config: Configuration dictionary with:
            - files: List of DOCX file paths to export
            - output_dir: Destination directory for PDF files
    """
    overall_start = time.time()
    file_times = []

    try:
        files = config.get('files', [])
        output_dir = config.get('output_dir', '')

        if not files:
            thread.log("ERROR: No files to export", "ERROR")
            return

        if not output_dir:
            thread.log("ERROR: No output directory specified", "ERROR")
            return

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Log start
        thread.log("="*60)
        thread.log(f"PDF EXPORT OPERATION STARTED")
        thread.log(f"Files to export: {len(files)}")
        thread.log(f"Output directory: {output_dir}")
        thread.log("="*60)

        # Update thread status
        thread.current_task = "Export to PDF"
        thread.total_tasks = len(files)
        thread.processed_files = 0
        thread.update_progress(0, "Starting export")

        # Process each file
        for i, file_path in enumerate(files, 1):
            file_name = Path(file_path).name
            base_name = Path(file_path).stem
            output_pdf = os.path.join(output_dir, f"{base_name}.pdf")

            try:
                thread.current_file = file_path
                current_progress = ((i - 1) / len(files)) * 100

                thread.log(f"\n[File {i}/{len(files)}] Exporting: {file_name}", "INFO")
                thread.update_progress(current_progress, f"Exporting {file_name}")
                thread.update_sub_progress(0, "Starting conversion")

                # Step 1: Validate source file
                file_start = time.time()
                thread.log(f"  [1/3] Validating source file...", "INFO")

                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"Source file not found: {file_path}")

                file_size = os.path.getsize(file_path) / 1024  # KB
                thread.log(f"        File size: {file_size:.1f} KB", "DEBUG")
                thread.update_sub_progress(10, "File validated")

                # Step 2: Convert to PDF
                thread.log(f"  [2/3] Converting to PDF...", "INFO")
                thread.update_sub_progress(30, "Converting...")

                convert_start = time.time()

                # Use robust Word COM conversion with retry logic
                try:
                    success = convert_docx_to_pdf_robust(file_path, output_pdf, max_retries=2)

                    if not success:
                        raise Exception("Conversion failed - no PDF created")

                except Exception as conv_error:
                    # Log detailed error
                    thread.log(f"        Conversion error: {str(conv_error)}", "ERROR")
                    raise

                convert_time = time.time() - convert_start
                thread.log(f"        Converted in {convert_time:.3f}s", "DEBUG")
                thread.update_sub_progress(80, "Conversion complete")

                # Step 3: Verify output
                thread.log(f"  [3/3] Verifying output...", "INFO")

                if not os.path.exists(output_pdf):
                    raise FileNotFoundError(f"Output PDF not created: {output_pdf}")

                output_size = os.path.getsize(output_pdf) / 1024  # KB
                thread.log(f"        Output size: {output_size:.1f} KB", "DEBUG")
                thread.update_sub_progress(100, "Verified")

                # Log success
                file_time = time.time() - file_start
                file_times.append((file_name, file_time))
                thread.log(f"  ✓ Exported successfully in {file_time:.3f}s", "SUCCESS")
                thread.log(f"    Output: {os.path.basename(output_pdf)}", "INFO")

                # Update progress
                thread.processed_files += 1
                thread.update_progress((i / len(files)) * 100, f"Completed {i}/{len(files)}")

            except Exception as e:
                thread.log(f"  ✗ ERROR exporting {file_name}: {str(e)}", "ERROR")
                thread.log(f"    File: {file_path}", "ERROR")
                import traceback
                thread.log(f"    {traceback.format_exc()}", "ERROR")
                # Continue with next file

        # Final summary
        total_time = time.time() - overall_start
        success_count = thread.processed_files

        thread.log("\n" + "="*60)
        if success_count == len(files):
            thread.log(f"✓ EXPORT COMPLETED SUCCESSFULLY", "SUCCESS")
        else:
            thread.log(f"⚠ EXPORT COMPLETED WITH ERRORS", "WARNING")
        thread.log("="*60)
        thread.log(f"Files exported: {success_count}/{len(files)}", "INFO")
        thread.log(f"Total time: {total_time:.3f}s", "INFO")

        if success_count > 0:
            thread.log(f"Average time per file: {(total_time/success_count):.3f}s", "INFO")

        thread.log(f"Output directory: {output_dir}", "INFO")

        # Show per-file timing
        if file_times:
            thread.log(f"\nPer-file timing:", "INFO")
            for fname, ftime in file_times:
                thread.log(f"  • {fname}: {ftime:.3f}s", "INFO")

        thread.log("="*60)
        thread.update_progress(100, "Export complete")

    except Exception as e:
        thread.log(f"CRITICAL ERROR: {str(e)}", "ERROR")
        import traceback
        thread.log(traceback.format_exc(), "ERROR")
        thread.update_progress(0, "Error")


def export_single_pdf(docx_path: str, pdf_path: str) -> bool:
    """
    Export a single DOCX file to PDF.

    Args:
        docx_path: Path to source DOCX file
        pdf_path: Path to output PDF file

    Returns:
        bool: True if successful
    """
    try:
        print(f"Exporting: {Path(docx_path).name} -> {Path(pdf_path).name}")

        success = convert_docx_to_pdf_robust(docx_path, pdf_path, max_retries=2)

        if success and os.path.exists(pdf_path):
            print(f"  ✓ Success: {Path(pdf_path).name}")
            return True
        else:
            print(f"  ✗ Failed: Output not created")
            return False

    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return False

