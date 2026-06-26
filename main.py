"""
Wording Tool - Main Entry Point
A tool for managing Word and XML documents with split, merge, and name operations.
"""
from ui import MainWindow


def main():
    """Main entry point for the application"""
    # Create and run the main window
    app = MainWindow()
    app.run()


if __name__ == '__main__':
    main()
