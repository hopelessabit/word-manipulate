
"""
Dialog Components Package
Contains various dialog windows for specific operations.
"""
from .base_dialog import BaseDialog
from .split_dialog import SplitDialog
from .merge_dialog import MergeDialog
from .naming_dialog import NamingDialog
from .split_document_dialog import SplitDocumentDialog, show_split_dialog

__all__ = ['BaseDialog', 'SplitDialog', 'MergeDialog', 'NamingDialog',
           'SplitDocumentDialog', 'show_split_dialog']


