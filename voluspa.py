#!/usr/bin/env python3

"""Voluspa Ghost Proxy Discord Bot"""
VOLUSPA_VERSION = 'v0.0.7a'
# Bot Example: https://gist.github.com/EvieePy/d78c061a4798ae81be9825468fe146be

import datetime
import math
import sys
import traceback

# Custom Imports
from modules.config import CONFIG
from modules.logger import Archivist

archivist = Archivist()
logger = archivist.get_logger()

from modules.fun import Quotes
from modules.database import Database
from modules.discord_utils import get_prefix, update_status_task

# Third-Party Imports
import discord
from discord.ext import commands

# Setup Initial Stuff
VOLUSPA_SHA = CONFIG.Voluspa.sha[:10]
client = discord.Client()

# These should perhaps be cogs..?
quotes = Quotes()
db = Database()

cog_extensions = [
    'cogs.autorole',
    'cogs.systems',
    'cogs.funstuff',
    'cogs.members',
    'cogs.destinyart',
    'cogs.utilities',
]

# bot = commands.AutoShardedBot()
bot = commands.Bot(command_prefix=get_prefix, description='Völuspá the Ghost Proxy Proto-Warmind AI')


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

    bot.loop.create_task(update_status_task(bot, quotes))

    # ' bot.send_message('message.channel')
    # ' general_channel = discord.Object(id='channel_id_here')
    # ' await bot.send_message(message.channel, fmt.format(message))


@bot.event
async def on_member_join(member):
    welcome_msg = f'Welcome to Ghost Proxy! <:ghost_proxy:455130405398380564> \n' \
                  f'Please read #server-info and then take a look around and check things out. ' \
                  f'Feel free to ask if you have any questions, thanks! <:cayde_thumbs_up:451649810894946314>'
    channel = member.guild.system_channel  # This should be "general"
    embed = discord.Embed(
        title='Welcome! :wave:',
        description=f'{member.mention}',
        color=0x009933
    )
    embed.add_field(
        name='',
        value=welcome_msg,
        inline=False
    )
    embed.set_footer(
        text=f'via Völuspá with \u2764',
        icon_url=f"{CONFIG.Resources.image_bucket_root_url}/voluspa/Voluspa_icon_64x64.png"
    )
    if channel is not None:
        await channel.send(embed=embed)


# https://gist.github.com/AileenLumina/510438b241c16a2960e9b0b014d9ed06
@bot.event
async def on_command_error(ctx, error):
    # if command has local error handler, return
    if hasattr(ctx.command, 'on_error'):
        return

    # get the original exception
    error = getattr(error, 'original', error)

    if isinstance(error, commands.CommandNotFound):
        return

    if isinstance(error, commands.BotMissingPermissions):
        missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
        if len(missing) > 2:
            fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
        else:
            fmt = ' and '.join(missing)
        _message = 'I need the **{}** permission(s) to run this command.'.format(fmt)
        await ctx.send(_message)
        return

    # if isinstance(error, commands.DisabledCommand):
    #     await ctx.send('This command has been disabled.')
    #     return

    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send("This command is on cooldown, please retry in {}s.".format(math.ceil(error.retry_after)))
        return

    if isinstance(error, commands.MissingPermissions):
        missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
        if len(missing) > 2:
            fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
        else:
            fmt = ' and '.join(missing)
        _message = 'You need the **{}** permission(s) to use this command.'.format(fmt)
        await ctx.send(_message)
        return

    if isinstance(error, commands.UserInputError):
        await ctx.send("Invalid input.")
        await ctx.command.send_command_help(ctx)
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

    # ignore all other exception types, but print them to stderr
    print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)

    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


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
    bot.run(CONFIG.Discord.api_key)


if __name__ == '__main__':
    main()
