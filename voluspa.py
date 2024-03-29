#!/usr/bin/env python3

"""Völuspá Ghost Proxy Discord Bot"""

import datetime
import math
import sys
import traceback
import asyncio

# Third-Party Imports
import discord
from discord import app_commands
from discord.ext import commands

# UVloop
try:
    import uvloop
except ImportError:
    pass
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

# Caches
from aiocache import caches

# Custom Imports
from modules.config import CONFIG
from modules.logger import Archivist

from modules.fun import Quotes
# from modules.database import Database
from modules.discord_utils import get_prefix, update_status_task
from modules.exceptions import BungieAPIError, BungieAPIOffline

# Init
archivist = Archivist()
logger = archivist.get_logger()
caches.set_config(CONFIG['Voluspa']['cache'])

# Setup initial client (Intents new as of discordpy 1.5.1)
intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.message_content = True
client = discord.Client(intents=intents)

# These should perhaps be cogs..?
quotes = Quotes()
# db = Database()

cog_extensions = [
    'cogs.autorole',
    'cogs.systems',
    'cogs.funstuff',
    'cogs.members',
    'cogs.destinyart',
    'cogs.utilities',
    'cogs.cache',
    'cogs.polls',
    'cogs.feedback',
    'cogs.kudos',
    'cogs.cog_control',
    #'cogs.roster',
    'jishaku',
    #'cogs.console', # https://github.com/Gorialis/jishaku/issues/55
    'cogs.gaminator',
]


# Note: AutoShard when guilds > 1000 bot = commands.AutoShardedBot()
bot = commands.Bot(
    command_prefix=get_prefix,
    description='Völuspá the Ghost Proxy Proto-Warmind AI',
    case_insensitive=True,
    intents=intents
)


@bot.event
async def on_ready():
    """Bot on_ready event"""

    if bot.user:
        logger.info('*** Logged in as: %s (ID: %s) ***', bot.user.name, bot.user.id)
    else:
        logger.error('*** Unable to login!! ***')
    logger.info('// VOLUSPA WARMIND ONLINE!!')

    if not hasattr(bot, 'uptime'):
        setattr(bot, 'uptime', datetime.datetime.utcnow())

    await bot.change_presence(
        activity=discord.Game(name=await quotes.pick_quote('status')),
        status=discord.Status.online
    )

    bot.loop.create_task(update_status_task(bot, quotes))

    await bot.tree.sync()

    # ' bot.send_message('message.channel')
    # ' general_channel = discord.Object(id='channel_id_here')
    # ' await bot.send_message(message.channel, fmt.format(message))


@bot.event
async def on_member_join(member):
    """on_member_join auto-firing event"""
    server_info_channel = discord.utils.get(member.guild.channels, name='server-info')
    rules_channel = discord.utils.get(member.guild.channels, name='rules-conduct')
    # server-info ID: 548653299109462017 | <#server-info:548653299109462017>
    welcome_msg = f'Please read the above, {rules_channel.mention}, and {server_info_channel.mention}.\n' \
                  f'Then take a look around, check things out, start chatting, and have fun!\n' \
                  f'Feel free to ask if you have any questions, thanks! <:cayde_thumbs_up:451649810894946314>'
    # channel = bot.get_channel(542680659228098561)
    channel = discord.utils.get(member.guild.channels, name='start-here')
    # General ID: '374330517165965315'
    # Welcome - Start Here ID: '542680659228098561'
    embed = discord.Embed(
        title=f':wave: Greetings, {member.name}!',
        color=0x009933
    )
    embed.add_field(
        name='Welcome to Ghost Proxy! <:ghost_proxy:455130405398380564>',
        value=welcome_msg,
        inline=False
    )
    embed.set_footer(
        text='via Völuspá with \u2764',
        icon_url=f"{CONFIG['Resources']['image_bucket_root_url']}/voluspa/Voluspa_icon_64x64.png"
    )
    if channel is not None:
        await channel.send(f'{member.mention}', embed=embed, delete_after=28800)  # delete after 8 hours


# https://gist.github.com/AileenLumina/510438b241c16a2960e9b0b014d9ed06
@bot.event
async def on_command_error(ctx, error):
    """Custom error handler for on_command_error"""
    # if command has local error handler, return
    if hasattr(ctx.command, 'on_error'):
        return

    # get the original exception
    error = getattr(error, 'original', error)

    if isinstance(error, commands.CommandNotFound):
        return

    if isinstance(error, commands.BotMissingPermissions):
        missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_permissions]
        if len(missing) > 2:
            fmt = f'{"**, **".join(missing[:-1])}, and {missing[-1]}'
        else:
            fmt = ' and '.join(missing)
        _message = f'I need the **{fmt}** permission(s) to run this command.'
        await ctx.send(_message)
        return

    # if isinstance(error, commands.DisabledCommand):
    #     await ctx.send('This command has been disabled.')
    #     return

    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"This command is on cooldown, please retry in {math.ceil(error.retry_after)}s.")
        return

    if isinstance(error, commands.MissingPermissions):
        missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_permissions]
        if len(missing) > 2:
            fmt = f'{"**, **".join(missing[:-1])}, and {missing[-1]}'
        else:
            fmt = ' and '.join(missing)
        _message = f'You need the **{fmt}** permission(s) to use this command.'
        await ctx.send(_message)
        return

    if isinstance(error, commands.UserInputError):
        await ctx.send("Invalid input.")
        await ctx.send_help(ctx.command)
        return

    if isinstance(error, commands.NoPrivateMessage):
        try:
            await ctx.author.send('This command cannot be used in direct messages.')
        except discord.Forbidden:
            pass
        return

    if isinstance(error, commands.CheckFailure):
        await ctx.send("You do not have permission to use this command.")
        return

    if isinstance(error, BungieAPIError):
        await ctx.send("There was an error with the Bungie API.")
        return

    if isinstance(error, BungieAPIOffline):
        await ctx.send("Bungie API appears to be currently offline. :(")
        return

    # ignore all other exception types, but print them to stderr
    print(f'Ignoring exception in command {ctx.command}:', file=sys.stderr)

    if isinstance(error, BaseException):
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

# https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/stats.py
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
    """Command error handler for on_app_command_error"""
    # Why is this necessary?
    error = getattr(error, 'original', error)

    if isinstance(error, app_commands.CommandNotFound):
        return

    if isinstance(error, app_commands.BotMissingPermissions):
        missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_permissions]
        if len(missing) > 2:
            fmt = f'{"**, **".join(missing[:-1])}, and {missing[-1]}'
        else:
            fmt = ' and '.join(missing)
        _message = f'I need the **{fmt}** permission(s) to run this command.'
        await interaction.response.send_message(_message, ephemeral=True)
        return

    # if isinstance(error, commands.DisabledCommand):
    #     await ctx.send('This command has been disabled.')
    #     return

    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(
            f"This command is on cooldown, please retry in {math.ceil(error.retry_after)}s.",
            ephemeral=True
            )
        return

    if isinstance(error, app_commands.MissingPermissions):
        missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_permissions]
        if len(missing) > 2:
            fmt = f'{"**, **".join(missing[:-1])}, and {missing[-1]}'
        else:
            fmt = ' and '.join(missing)
        _message = f'You need the **{fmt}** permission(s) to use this command.'
        await interaction.response.send_message(_message, ephemeral=True)
        return

    if isinstance(error, app_commands.NoPrivateMessage):
        try:
            await interaction.user.send('This command cannot be used in direct messages.')
        except discord.Forbidden:
            pass
        return

    if isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    if isinstance(error, BungieAPIError):
        await interaction.response.send_message("There was an error with the Bungie API.", ephemeral=True)
        return

    if isinstance(error, BungieAPIOffline):
        await interaction.response.send_message("Bungie API appears to be currently offline. :(", ephemeral=True)
        return

    # ignore all other exception types, but print them to stderr
    print(f'Ignoring exception in command {interaction.command}:', file=sys.stderr)

    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

bot.tree.on_error = on_app_command_error

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


async def main():
    """Main entrypoint for the whole show!!"""
    logger.info('// Völuspá / Booting...')

    async with bot:
        logger.info('Initializing bot...')
        for extension in cog_extensions:
            logger.info('Loading extension [%s]...', extension)
            await bot.load_extension(extension)
        logger.info('Starting bot...')
        await bot.start(CONFIG['Discord']['api_key'])


if __name__ == '__main__':
    asyncio.run(main())
