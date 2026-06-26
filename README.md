# Wording Tool

A comprehensive document management tool for Word and XML documents with support for splitting, merging, renaming, and PDF export operations.

## Overview

The Wording Tool is a desktop application built with Python and Tkinter that provides an intuitive interface for performing advanced document operations. It supports DOCX files with specialized XML processing capabilities and can export documents to PDF format.

## Features

### Core Operations

- **Split Documents**: Split DOCX files into smaller documents based on specified criteria
- **Merge Documents**: Combine multiple DOCX files into a single document
- **Rename Files**: Rename individual or batch files with ease
- **Export to PDF**: Convert DOCX documents to PDF format
- **XML Processing**: Advanced XML document handling and editing capabilities

### Smart File Type Detection

The application automatically detects file types and enables/disables operations accordingly:
- **DOCX Files**: All operations available (split, merge, export, rename)
- **PDF Files**: Rename operation available
- **Mixed Selection**: Only rename operation available

### User Interface

- **Modern, Responsive Design**: Built with Tkinter and TTK for a professional look
- **Theme Manager**: Support for light and dark themes
- **Menu Bar**: Comprehensive menu system for all operations
- **Toolbar**: Quick access buttons for common operations
- **Work Area**: Intuitive file browser and operation management
- **Status Bar**: Real-time feedback on application status and operations
- **Thread Monitor**: Monitor long-running operations and view logs

### Advanced Features

- **Multi-threaded Operations**: Non-blocking UI for long operations
- **Dialog Management**: Specialized dialogs for each operation type
- **File Selection Manager**: Intelligent file selection with operation validation
- **Customizable Naming**: Advanced naming schemes for file operations
- **PDF Export Configuration**: Configurable PDF export options

## Project Structure

```
python/
├── main.py                     # Application entry point
├── logic/                      # Core business logic
│   ├── file_selection_manager.py   # File management and operation validation
│   ├── export/                 # PDF export functionality
│   ├── merge/                  # Document merging logic
│   ├── split/                  # Document splitting logic
│   └── name/                   # File naming operations
├── ui/                         # User interface components
│   ├── main_window.py          # Main application window
│   ├── menu_bar.py             # Menu bar implementation
│   ├── toolbar.py              # Toolbar with action buttons
│   ├── status_bar.py           # Status bar display
│   ├── work_area.py            # File management work area
│   ├── theme_manager.py        # Theme and styling
│   ├── thread_monitor_panel.py # Thread monitoring UI
│   └── dialogs/                # Operation dialogs
│       ├── split_dialog.py
│       ├── merge_dialog.py
│       ├── export_pdf_dialog.py
│       └── naming_dialog.py
├── thread/                     # Threading and async operations
│   ├── thread_manager.py       # Thread management system
│   └── example_workers.py      # Worker thread implementations
└── existed_logic/              # Legacy XML processing modules
```

## Installation

### Requirements

- Python 3.8 or higher
- Tkinter (usually included with Python)
- python-docx (for DOCX file handling)
- Additional dependencies as specified in requirements.txt

### Setup

1. Clone or download the project
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Quick Start

Run the application:
```bash
python main.py
```

### Basic Workflow

1. **Select Files**: Use the work area to browse and select DOCX files
2. **Choose Operation**: Based on your selection, available operations will be enabled in the toolbar
3. **Configure Options**: Use dialogs to configure operation-specific settings
4. **Execute**: Click the operation button to start processing
5. **Monitor**: Watch progress in the thread monitor panel and status bar

### Operations Guide

#### Split Documents
Split a single DOCX document into multiple smaller documents:
1. Select one or more DOCX files
2. Click the "Split" button
3. Configure split criteria in the dialog
4. Click "Execute"

#### Merge Documents
Combine multiple DOCX files into one:
1. Select 2 or more DOCX files
2. Click the "Merge" button
3. Set merge options and output location
4. Click "Execute"

#### Export to PDF
Convert DOCX documents to PDF format:
1. Select one or more DOCX files
2. Click the "Export PDF" button
3. Configure PDF export settings
4. Click "Execute"

#### Rename Files
Rename files individually or in batch:
1. Select one or more files (DOCX or PDF)
2. Click the "Rename" button
3. Enter new names or use naming patterns
4. Click "Execute"

## Architecture

### Threading Model

The application uses a thread manager for executing long-running operations without blocking the UI:
- Main thread handles UI interactions
- Worker threads process file operations
- Thread-safe communication via message queues
- Cancel and pause operations support

### File Selection Management

The `FileSelectionManager` class handles:
- File type detection and validation
- Available operation determination
- File information retrieval
- Selection state management

### Theme System

Dynamic theming support with:
- Light and dark themes
- Color configuration
- Component-specific styling
- Runtime theme switching

## Development

### Building Executable

The project includes a PyInstaller configuration file (`WordMerger.spec`) for building standalone executables:

```bash
pyinstaller WordMerger.spec
```

This generates a `WordMerger.exe` in the `dist/` folder.

### Key Components

- **MainWindow**: Central UI controller managing all components
- **ThreadManager**: Handles asynchronous operation execution
- **WorkArea**: Primary file management interface
- **DialogFactory**: Creates specialized dialogs for each operation
- **FileSelectionManager**: Intelligent file selection and validation

## Configuration

The application stores theme and configuration settings which can be customized through:
- Theme manager for UI customization
- Dialog settings for operation defaults
- Status bar for real-time information

## Troubleshooting

### Operations Not Available
- Ensure files are DOCX format for full operation support
- Check file accessibility and permissions
- Verify file extension is recognized

### Long Operations Hanging
- Check the thread monitor for operation status
- View detailed logs in the log viewer
- Cancel operations if needed

### Theme Issues
- Try switching to opposite theme and back
- Restart the application
- Check TTK theme compatibility

## Future Enhancements

Potential improvements for future versions:
- Additional document formats (ODT, RTF)
- Advanced XML transformation options
- Batch operation scheduling
- Operation history and undo/redo
- Custom template support
- Command-line interface

## Support

For issues, questions, or contributions, please refer to the project documentation or contact the development team.

---

**Version**: 1.0  
**Last Updated**: June 2026

