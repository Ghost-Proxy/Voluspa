from discord import Embed
#from discord.ext import commands

from voluspa import CONFIG


def default_embed(title='Völuspá', description=''):
    embed = Embed(
        title=title,
        description=description,
        color=0x009933
    )
    # embed.set_author(name='\uFEFF', icon_url=f'{CONFIG.Resources.image_bucket_root_url}/ghost-proxy/GP_Logo-2.png')
    embed.set_footer(
        text=f'via Völuspá with :green_heart:',
        icon_url=f"{CONFIG.Resources.image_bucket_root_url}/voluspa/Voluspa_icon_64x48.png"
    )
    return embed
