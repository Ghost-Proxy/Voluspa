"""Provides a unified message style and theme color palette"""

STYLES = {
    'colors': {
        'voluspa': 0x009933,
        'info': 0x4286f4,
        'warning': 0xffc107,  # d1c222
        'danger': 0xdc3545,  # d14221
        'error': 0xdc3545,
        'success': 0x28a745,  # 23d15d
        'greyed': 0x6c757d,
        'secondary': 0x17a2b8  # 21b3d1
    }
}

class Styles():
    """Styles Object"""
    def __init__(self):
        self.styles = STYLES

    def colors(self, color_name):
        """Return the relevant color code"""
        return self.styles.get(color_name, None)
