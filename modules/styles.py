from modules.misc import AttrDict

STYLES = {
    'COLORS': {
        'voluspa': 0x009933,
        'info': 0x4286f4,
        'warning': 0xffc107,  # d1c222
        'danger': 0xdc3545,  # d14221
        'success': 0x28a745,  # 23d15d
        'greyed': 0x6c757d,
        'secondary': 0x17a2b8  # 21b3d1
    }
}

STYLES = AttrDict.from_nested_dict(STYLES)
