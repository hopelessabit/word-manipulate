"""
Theme Manager
Handles light/dark theme switching with modern styling
"""
import tkinter as tk
from tkinter import ttk
import json
from pathlib import Path


class ThemeManager:
    """Manages application themes (light/dark mode)"""

    LIGHT_THEME = {
        'name': 'aqua_light',

        # Background & Foreground
        'bg': '#E9FBFF',  # Very soft aqua background
        'fg': '#0F3057',  # Deep blue-gray text (modern, readable)

        # Selection
        'select_bg': '#00C8D2',  # Use main accent for consistency
        'select_fg': '#FFFFFF',

        # Inputs
        'input_bg': '#FFFFFF',
        'input_fg': '#0F3057',

        # Buttons
        'button_bg': '#F0F9FF',  # Soft light-blue
        'button_fg': '#084C61',
        'button_active_bg': '#CDEEFF',  # More aqua, less purple than #D7F3FF
        # Optional: a subtle border around buttons
        'button_border': '#C5E3EC',

        # Frames / Cards
        'frame_bg': '#F4FDFF',  # Ultra soft cyan
        'card_bg': '#FFFFFF',
        'shadow': '#00000020',

        # Accents
        'accent': '#00C8D2',  # Fresh aqua accent
        'success': '#1CB5A3',  # Aqua-green success
        'warning': '#FFB74D',  # Soft amber
        'error': '#E53935',  # Soft red
        'info': '#00BCD4',  # Cyan info

        # Borders & Hover
        'border': '#A0D4DE',  # More visible aqua-cyan border for boxes
        'hover': '#DFF6FA',  # Slightly more contrast than before

        # Secondary Text
        'text_secondary': '#4B5563',  # Neutral slate gray

        # Scrollbar
        'scrollbar_bg': '#E1F3F6',  # Track
        'scrollbar_fg': '#9ED6DE',  # Thumb (darker than track → clearer)
        'scrollbar_disabled_bg': '#E1F3F6',
        'scrollbar_disabled_fg': '#D3E7EB',  # Slight hint but muted

        # Sash (PanedWindow separator)
        'sash_bg': '#9ED6DE',  # Same family as scrollbar thumb

        # Optional: keyboard focus / outline color
        'focus_ring': '#00ACC1',

        # Menu
        'menu_bg': '#FFFFFF',
        'menu_fg': '#0F3057',
        'menu_active_bg': '#E0F7FA',
        'menu_active_fg': '#0F3057'
    }

    DARK_THEME = {
        'name': 'dark',

        # Background & Foreground (cool, modern)
        'bg': '#050816',  # Deep navy/ink background (not pure black)
        'fg': '#E5E7EB',  # Light neutral gray text

        # Selection
        'select_bg': '#1D4ED8',  # Strong modern blue (similar to VSCode selection)
        'select_fg': '#FFFFFF',

        # Inputs
        'input_bg': '#0B1020',  # Slightly lighter than bg for fields
        'input_fg': '#E5E7EB',

        # Buttons
        'button_bg': '#111827',  # Dark slate button
        'button_fg': '#E5E7EB',
        'button_active_bg': '#1F2937',  # Hover/pressed, a bit brighter
        'button_border': '#1F2937',  # Subtle outline

        # Frames / Cards
        'frame_bg': '#050816',  # Match main background
        'card_bg': '#0F172A',  # Slightly lighter block/panel color
        'shadow': '#00000080',

        # Accents
        'accent': '#38BDF8',  # Modern cyan/sky blue accent
        'success': '#22C55E',  # Bright but soft green
        'warning': '#EAB308',  # Warm yellow (no brown)
        'error': '#F97373',  # Softer red, not too harsh
        'info': '#60A5FA',  # Soft blue info

        # Borders & Hover
        'border': '#2D3748',  # More visible slate border for dark theme
        'hover': '#111827',  # For row/element hover

        # Secondary Text
        'text_secondary': '#9CA3AF',  # Muted neutral gray

        # Scrollbar (minimal, modern)
        'scrollbar_bg': '#050816',  # Blend with background
        'scrollbar_fg': '#374151',  # Thumb – visible but subtle
        'scrollbar_hover': '#4B5563',
        'scrollbar_disabled_bg': '#050816',
        'scrollbar_disabled_fg': '#111827',

        # Sash (splitter between panes)
        'sash_bg': '#1F2937',

        # Menu
        'menu_bg': '#050816',  # Same as app bg (floating panels feel native)
        'menu_fg': '#E5E7EB',
        'menu_active_bg': '#111827',
        'menu_active_fg': '#F9FAFB'
    }

    def __init__(self):
        """Initialize theme manager"""
        self.current_theme = self.LIGHT_THEME
        self.theme_callbacks = []
        self.config_file = Path.home() / '.wording_tool_theme.json'
        self._load_saved_theme()

    def _load_saved_theme(self):
        """Load saved theme preference"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    theme_name = config.get('theme', 'light')
                    if theme_name == 'dark':
                        self.current_theme = self.DARK_THEME
        except:
            pass

    def _save_theme(self):
        """Save theme preference"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump({'theme': self.current_theme['name']}, f)
        except:
            pass

    def toggle_theme(self):
        """Toggle between light and dark theme"""
        if self.current_theme['name'] == 'dark':
            self.current_theme = self.LIGHT_THEME
        else:
            self.current_theme = self.DARK_THEME

        self._save_theme()
        self._notify_callbacks()

    def set_theme(self, theme_name: str):
        """Set specific theme by name"""
        if theme_name in ['light', 'aqua_light']:
            self.current_theme = self.LIGHT_THEME
        elif theme_name == 'dark':
            self.current_theme = self.DARK_THEME

        self._save_theme()
        self._notify_callbacks()

    def get_color(self, key: str) -> str:
        """Get color from current theme"""
        return self.current_theme.get(key, '#000000')

    def is_dark(self) -> bool:
        """Check if dark theme is active"""
        return self.current_theme['name'] == 'dark'

    def register_callback(self, callback):
        """Register callback for theme changes"""
        self.theme_callbacks.append(callback)

    def _notify_callbacks(self):
        """Notify all callbacks of theme change"""
        for callback in self.theme_callbacks:
            try:
                callback()
            except Exception as e:
                print(f"Theme callback error: {e}")

    def apply_to_widget(self, widget, widget_type='frame'):
        """Apply theme to a widget"""
        theme = self.current_theme

        try:
            if widget_type == 'frame':
                widget.configure(background=theme['frame_bg'])

            elif widget_type == 'label':
                widget.configure(
                    background=theme['bg'],
                    foreground=theme['fg']
                )

            elif widget_type == 'button':
                widget.configure(
                    background=theme['button_bg'],
                    foreground=theme['button_fg'],
                    activebackground=theme['button_active_bg']
                )

            elif widget_type == 'text':
                widget.configure(
                    background=theme['input_bg'],
                    foreground=theme['input_fg'],
                    insertbackground=theme['fg'],
                    selectbackground=theme['select_bg'],
                    selectforeground=theme['select_fg']
                )

            elif widget_type == 'entry':
                widget.configure(
                    background=theme['input_bg'],
                    foreground=theme['input_fg'],
                    insertbackground=theme['fg']
                )
        except:
            pass

    def get_ttk_style(self):
        """Get ttk style configuration for current theme"""
        theme = self.current_theme

        return {
            'TFrame': {
                'background': theme['frame_bg']
            },
            'TLabel': {
                'background': theme['frame_bg'],
                'foreground': theme['fg']
            },
            'TLabelframe': {
                'background': theme['frame_bg'],
                'foreground': theme['fg'],
                'bordercolor': theme['border'],
                'darkcolor': theme['border'],
                'lightcolor': theme['frame_bg']
            },
            'TLabelframe.Label': {
                'background': theme['frame_bg'],
                'foreground': theme['accent'],
                'font': ('TkDefaultFont', 9, 'bold')
            },
            'TButton': {
                'background': theme['button_bg'],
                'foreground': theme['button_fg'],
                'bordercolor': theme['border'],
                'lightcolor': theme['button_bg'],
                'darkcolor': theme['border'],
                'borderwidth': 1,
                'relief': 'flat',
                'focuscolor': ''  # Remove focus outline
            },
            'Treeview': {
                'background': theme['input_bg'],
                'foreground': theme['fg'],
                'fieldbackground': theme['input_bg'],
                'bordercolor': theme['border'],
                'borderwidth': 1
            },
            'Treeview.Heading': {
                'background': theme['button_bg'],
                'foreground': theme['fg'],
                'bordercolor': theme['border']
            },
            'TEntry': {
                'fieldbackground': theme['input_bg'],
                'foreground': theme['fg'],
                'bordercolor': theme['border'],
                'lightcolor': theme['input_bg'],
                'darkcolor': theme['border'],
                'focuscolor': ''  # Remove focus outline
            },
            'TScrollbar': {
                'background': theme['scrollbar_fg'],      # Thumb (draggable part)
                'troughcolor': theme['scrollbar_bg'],     # Track background
                'bordercolor': theme['border'],
                'arrowcolor': theme['fg'],
                'darkcolor': theme['scrollbar_fg'],
                'lightcolor': theme['scrollbar_fg']
            },
            'TPanedwindow': {
                'background': theme['frame_bg']
            },
            'Sash': {
                'sashthickness': 4,
                'sashrelief': 'flat',
                'sashpad': 0
            },
            'TNotebook': {
                'background': theme['frame_bg'],
                'bordercolor': theme['border'],
                'tabmargins': [2, 5, 2, 0]
            },
            'TNotebook.Tab': {
                'background': theme['button_bg'],
                'foreground': theme['fg'],
                'padding': [12, 8],
                'borderwidth': 0
            },
            'TSeparator': {
                'background': theme['border']
            },
            'TProgressbar': {
                'background': theme['accent'],
                'troughcolor': theme['input_bg'],
                'bordercolor': theme['border']
            },
            'TRadiobutton': {
                'background': theme['frame_bg'],
                'foreground': theme['fg'],
                'indicatorbackground': theme['input_bg'],
                'indicatorforeground': theme['accent'],
                'bordercolor': theme['border'],
                'focuscolor': ''  # Remove focus outline
            }
        }


# Global theme manager instance
_theme_manager = None

def get_theme_manager() -> ThemeManager:
    """Get or create global theme manager"""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager

