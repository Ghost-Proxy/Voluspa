from discord import Embed
# from discord.ext import commands

from voluspa import CONFIG

from typing import Any, List, Dict, Tuple, Sequence, Iterable


# TODO:
#  - Prompts/confirm "dialog"
#  - Paging support
#  - Automatic cleanup
#  - built in "theme" handling (conv funcs/wrappers)


def default_embed(title='Völuspá', description='', color=0x009933, footer_notes=None, **kwargs):
    embed = Embed(
        title=title,
        description=description,
        color=color,
        **kwargs
    )
    # embed.set_author(name='\uFEFF', icon_url=f'{CONFIG.Resources.image_bucket_root_url}/ghost-proxy/GP_Logo-2.png')
    embed.set_footer(
        text=f'via Völuspá with \u2764{f" | {footer_notes}" if footer_notes else ""}',
        icon_url=f"{CONFIG.Resources.image_bucket_root_url}/voluspa/Voluspa_icon_64x48.png"
    )
    return embed


# Hmm... this seems wrong?
def format_list(items: (List, Tuple, Sequence, Iterable), surround: str = '```', none_msg='_N/A_'):
    items = list(items)
    nl = '\n'
    init_items_num = len(items)
    if surround:
        items.insert(0, '```')
        items.append('```')
    return f'{nl.join(items)}' if init_items_num >= 1 else none_msg
