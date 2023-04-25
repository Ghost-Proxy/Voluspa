"""Custom embeds module"""

from typing import Union, List, Tuple, Sequence, Iterable

from discord import Embed
# from discord.ext import commands

from voluspa import CONFIG
from modules.styles import Styles

styles = Styles()

# TODO:
#  - Prompts/confirm "dialog"
#  - Paging support
#  - Automatic cleanup
#  - built in "theme" handling (conv funcs/wrappers)

def remove_color_kwarg(kwargs):
    """Remove color"""
    try:
        kwargs.pop('color')
    except KeyError:
        pass
    return kwargs


def success_embed(*args, **kwargs):
    """Create a styled Success embed"""
    return default_embed(*args, color=styles.colors('success'), **remove_color_kwarg(kwargs))


def info_embed(*args, **kwargs):
    """Create a styled Info embed"""
    return default_embed(*args, color=styles.colors('info'), **remove_color_kwarg(kwargs))


def warning_embed(*args, **kwargs):
    """Create a styled Warning embed"""
    return default_embed(*args, color=styles.colors('warning'), **remove_color_kwarg(kwargs))


def error_embed(*args, **kwargs):
    """Create a styled Error embed"""
    return default_embed(*args, color=styles.colors('error'), **remove_color_kwarg(kwargs))


def default_embed(title='Völuspá', description='', color=0x009933, footer_notes=None, **kwargs):
    """Create a default styled embed"""
    embed = Embed(
        title=title,
        description=description,
        color=color,
        **kwargs
    )
    # embed.set_author(name='\uFEFF', icon_url=f'{CONFIG.Resources.image_bucket_root_url}/ghost-proxy/GP_Logo-2.png')
    embed.set_footer(
        text=f'via Völuspá with \u2764{f" | {footer_notes}" if footer_notes else ""}',
        icon_url=f"{CONFIG.Resources.image_bucket_root_url}/voluspa/Voluspa_icon_64x64.png"
    )
    return embed


def format_list(items: Union[List, Tuple, Sequence, Iterable], surround: str = '```', none_msg='_N/A_'):
    """Formats a list nicely"""
    items = list(items)
    new_line = '\n'
    init_items_num = len(items)
    if surround:
        items.insert(0, '```')
        items.append('```')
    return f'{new_line.join(items)}' if init_items_num >= 1 else none_msg
