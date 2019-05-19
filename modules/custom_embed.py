from discord import Embed
#from discord.ext import commands

from voluspa import CONFIG, bot


def default_embed(title='Völuspá', description=''):
    embed = Embed(
        title=title,
        description=description,
        color=0x009933
    )
    embed.set_footer(
        text=f'via Völuspá {bot.get_emoji(455130405398380564)}',
        icon_url=f"{CONFIG.Resources.image_bucket_root_url}/voluspa/Voluspa_icon_64x48.png"
    )
    return embed