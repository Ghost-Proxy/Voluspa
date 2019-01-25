#!/usr/bin/env python3

"""Voluspa Ghost Proxy Discord Bot"""

# REF:
# https://gist.github.com/EvieePy/d78c061a4798ae81be9825468fe146be

# Built-in Imports
import sys
import asyncio
import logging
from logging.handlers import RotatingFileHandler
import traceback
import datetime

# Custom Imports
from modules.fun import Quotes, RandomQuotes
from modules.database import Database
from modules.helpers import read_config

# Third-Party Imports
import discord
from discord.ext import commands


logger = logging.getLogger('voluspa')
logger.setLevel(logging.DEBUG)
file_handler = RotatingFileHandler(filename='voluspa.log', encoding='utf-8', maxBytes=1024*1024*10, backupCount=10)
log_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s:  %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(log_formatter)
stream_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# Setup Initial Stuff
client = discord.Client()
quotes = Quotes()
random_quotes = RandomQuotes()
db = Database()
config = read_config()

cog_extensions = [
    'cogs.autorole',
    'cogs.systems',
    'cogs.funstuff',
    'cogs.members'
]


# https://gist.github.com/EvieePy/d78c061a4798ae81be9825468fe146be
def get_prefix(bot, message):
    """A callable Prefix for our bot. This could be edited to allow per server prefixes."""
    prefixes = ['$']

    # Check to see if we are outside of a guild. e.g DM's etc.
    if not message.guild:
        # Only allow ? to be used in DMs
        return '$'

    # If we are in a guild, we allow for the user to mention us or use any of the prefixes in our list.
    return commands.when_mentioned_or(*prefixes)(bot, message)


# bot = commands.AutoShardedBot()
bot = commands.Bot(command_prefix=get_prefix, description='Völuspá the Ghost Proxy Proto-Warmind AI')


async def update_status_task(_bot):
    while True:
        await _bot.change_presence(activity=discord.Game(name=await quotes.pick_quote('status')))
        await asyncio.sleep(30)


@bot.event
async def on_ready():
    logger.info('*** Logged in as: {} (ID: {}) ***'.format(bot.user.name, bot.user.id))
    logger.info('// VOLUSPA WARMIND ONLINE!!')

    if not hasattr(bot, 'uptime'):
        bot.uptime = datetime.datetime.utcnow()

    await bot.change_presence(
        activity=discord.Game(name=await quotes.pick_quote('status')),
        status=discord.Status.online
    )

    bot.loop.create_task(update_status_task(bot))

    # ' bot.send_message('message.channel')
    # ' general_channel = discord.Object(id='channel_id_here')
    # ' await bot.send_message(message.channel, fmt.format(message))

# TODO: Get Error Handling working...
# @bot.event
# async def on_command_error(ctx, error):
#     """The event triggered when an error is raised while invoking a command.
#     ctx   : Context
#     error : Exception"""
#     print('ctx: {}\nerror: {}'.format(ctx, error))
#
#     if hasattr(ctx.command, 'on_error'):
#         return
#
#     ignored = (commands.CommandNotFound, commands.UserInputError)
#     error = getattr(error, 'original', error)
#
#     if isinstance(error, ignored):
#         return
#
#     elif isinstance(error, commands.DisabledCommand):
#         return await ctx.send(f'{ctx.command} has been disabled.')
#
#     elif isinstance(error, commands.NoPrivateMessage):
#         try:
#             return await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
#         except:
#             pass
#
#     elif isinstance(error, commands.BadArgument):
#         if ctx.command.qualified_name == 'tag list':
#             return await ctx.send('I could not find that member. Please try again.')
#
#     print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
#     traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


def main():
    for extension in cog_extensions:
        bot.load_extension(extension)
    bot.run(config.Discord.api_key)


if __name__ == '__main__':
    main()
