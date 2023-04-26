"""Discord Utils Module"""

import asyncio

import discord
from discord.ext import commands

from modules.config import CONFIG


def get_prefix(bot, message):
    """A callable Prefix for our bot. This could be edited to allow per server prefixes."""
    prefixes = [CONFIG['Voluspa']['prefix']]
    # Check to see if we are outside of a guild. e.g DM's etc.
    if not message.guild:
        # Only allow prefix to be used in DMs
        return CONFIG['Voluspa']['prefix']
    # If we are in a guild, we allow for the user to mention us or use any of the prefixes in our list.
    return commands.when_mentioned_or(*prefixes)(bot, message)


async def update_status_task(bot, quotes):
    """Update Bot Status task"""
    while True:
        await bot.change_presence(activity=discord.Game(name=await quotes.pick_quote('status')))
        await asyncio.sleep(30)


# from modules.custom_embed import default_embed, format_list
# TODO: This should prolly be combined with Custom_Embed + Styles into a Theme module + Messaging
# TODO: Create a multipart(paged) embed...
async def send_multipart_msg(ctx, raw_msg):
    """Multipart message handler"""
    msg_len = len(raw_msg)
    # >>> chunks, chunk_size = len(x), len(x)/4
    # >>> [ x[i:i+chunk_size] for i in range(0, chunks, chunk_size) ]
    # num_msg_required = math.ceil(msg_len / 2000)
    msg_chunk_size = 2000
    # parts = [your_string[i:i + n] for i in range(0, len(your_string), n)]
    msg_part_list = [raw_msg[i:i + msg_chunk_size] for i in range(0, msg_len, msg_chunk_size)]
    for msg_part in msg_part_list:
        await ctx.send(msg_part)
