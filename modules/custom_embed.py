from discord import Embed
#from discord.ext import commands

from voluspa import CONFIG


def default_embed(title='Völuspá', description='', color=0x009933, **kwargs):
    embed = Embed(
        title=title,
        description=description,
        color=color,
        **kwargs
    )
    # embed.set_author(name='\uFEFF', icon_url=f'{CONFIG.Resources.image_bucket_root_url}/ghost-proxy/GP_Logo-2.png')
    embed.set_footer(
        text='via Völuspá with \u2764',
        icon_url=f"{CONFIG.Resources.image_bucket_root_url}/voluspa/Voluspa_icon_64x48.png"
    )
    return embed
