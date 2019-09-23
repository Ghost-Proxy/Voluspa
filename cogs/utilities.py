# import re
# import asyncio
import aiohttp
import logging
# from typing import Any, List, Dict, Tuple, Sequence
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import io
import emoji

import discord
from discord.ext import commands

from modules.custom_embed import default_embed

logger = logging.getLogger('voluspa.cog.utilities')

# Uses https://worldtimeapi.org/


async def get_online_datetime(location):
    worldtimeapi_url = f'https://www.worldtimeapi.org/api/timezone/{location}'
    async with aiohttp.ClientSession() as session:
        async with session.get(worldtimeapi_url) as r:
            if r.status == 200:
                json_resp = await r.json()
                #datetime_str = json_resp['datetime']
                #return json_resp  #, datetime_str
                return parse_datetime(json_resp['datetime']), json_resp['abbreviation']
            else:
                logger.info(f'Error: Unable to retrieve time for: {location} | Resp: {r}')
                return None, None


def parse_datetime(dt_str):
    return datetime.datetime.strptime(dt_str, '%Y-%m-%dT%H:%M:%S.%f%z')


def display_datetime(datetime_str, time_zone=None, verbose=True):
    """Returns a formatted datetime with TZ (if provided) or 'Error (Missing)"""
    """      
    >>> print(datetime.datetime.utcnow().strftime("%Y/%m/%d %a %I:%M %p"))
    2019/05/19 Sun 01:10 AM
    """
    if datetime_str:  # and type(datetime_str) == datetime.datetime.now():
        if verbose:
            return f'{datetime_str.strftime("%Y/%m/%d %a %I:%M %p")}{f" ({time_zone})" if time_zone else ""}'
        else:
            return f'{datetime_str.strftime("%a %I:%M %p")}{f" ({time_zone})" if time_zone else ""}'
    else:
        return 'Error (Missing)'

def generate_poll_embed(poll_args):
    desc_str = ""
    react_char = '\U0001f1e6'
    for arg_iter in range(1, len(poll_args)):
        desc_str += f'{react_char} {poll_args[arg_iter]}\n'
        react_char = chr(ord(react_char) + 1)
    
    return default_embed(
        title=poll_args[0],
        description=desc_str
    )


class Utilities(commands.Cog):
    """Helpful utility functions"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='emotes-list', aliases=['el'])
    @commands.is_owner()
    async def custom_emotes_list(self, ctx):
        bot_emojis = self.bot.emojis
        guild_emojis = ctx.guild.emojis
        nl = '\n'
        # logger.info(f'Bot Emojis: {nl.join(bot_emojis)}\n')
        # logger.info(f'Guild Emojis: {nl.join(guild_emojis)}\n')
        logger.info(f'bot emojis: {bot_emojis}')
        logger.info(f'guild emojis: {guild_emojis}')

    @commands.command(name='time', aliases=['clock', 't'])
    @commands.guild_only()
    @commands.cooldown(1, 30)
    async def current_times(self, ctx, verbose: bool = False):
        """Displays date/time for several time zones

        Cooldown limited to 1 use per 30 seconds across the server"""

        async with ctx.typing():
            # sys_time_local = datetime.datetime.now(), None  #.strftime("%Y/%m/%d %a %I:%M %p")
            sys_time_utc = datetime.datetime.utcnow(), None  #.strftime("%Y/%m/%d %a %I:%M %p")

            hawaii_time = await get_online_datetime('Pacific/Honolulu')
            pacific_time = await get_online_datetime('America/Los_Angeles')
            mountain_time = await get_online_datetime('America/Denver')
            central_time = await get_online_datetime('America/Chicago')
            eastern_time = await get_online_datetime('America/New_York')
            london_time = await get_online_datetime('Europe/London')
            dubai_time = await get_online_datetime('Asia/Dubai')
            tokyo_time = await get_online_datetime('Asia/Tokyo')
            auckland_time = await get_online_datetime('Pacific/Auckland')

            if verbose:
                berlin_time = await get_online_datetime('Europe/Berlin')
                moscow_time = await get_online_datetime('Europe/Moscow')
                shanghai_time = await get_online_datetime('Asia/Shanghai')
                australia_east_time = await get_online_datetime('Australia/Sydney')

            datetime_embed = default_embed(
                title=":globe_with_meridians: World Clocks :clock1:",
                description=f'Provided by Völuspá Timekeeping {self.bot.get_emoji(562955074708439040)}',
                color=0x4286f4
            )
            # datetime_embed.set_author(name="Völuspá Timekeeping")
            # datetime_embed.add_field(name='System Clock Local', value=display_datetime(*sys_time_local), inline=False)
            datetime_embed.add_field(
                name='Local System (UTC)',
                value=f'{display_datetime(*sys_time_utc)}\n',
                inline=False
            )
            datetime_embed.add_field(name='\u200B', value='\u200B', inline=False)

            if verbose:
                datetime_embed.add_field(name='Hawaii', value=display_datetime(*hawaii_time), inline=False)
                datetime_embed.add_field(name='Los Angeles', value=display_datetime(*pacific_time), inline=False)
                datetime_embed.add_field(name='Denver', value=display_datetime(*mountain_time), inline=False)
                datetime_embed.add_field(name='Chicago', value=display_datetime(*central_time), inline=False)
                datetime_embed.add_field(name='New York', value=display_datetime(*eastern_time), inline=False)
                datetime_embed.add_field(name='London', value=display_datetime(*london_time), inline=False)
                datetime_embed.add_field(name='Berlin', value=display_datetime(*berlin_time), inline=False)
                datetime_embed.add_field(name='Moscow', value=display_datetime(*moscow_time), inline=False)
                datetime_embed.add_field(name='Dubai', value=display_datetime(dubai_time[0], 'GST'), inline=False)
                datetime_embed.add_field(name='Shanghai', value=display_datetime(*shanghai_time), inline=False)
                datetime_embed.add_field(name='Tokyo', value=display_datetime(*tokyo_time), inline=False)
                datetime_embed.add_field(name='Australia East', value=display_datetime(*australia_east_time), inline=False)
                datetime_embed.add_field(name='Auckland', value=display_datetime(*auckland_time), inline=False)
            else:
                datetime_embed.add_field(name='Hawaii', value=display_datetime(*hawaii_time, verbose=verbose))
                datetime_embed.add_field(name='Pacific (LA)', value=display_datetime(*pacific_time, verbose=verbose))
                datetime_embed.add_field(name='Mountain (DEN)', value=display_datetime(*mountain_time, verbose=verbose))
                datetime_embed.add_field(name='Central (CHI)', value=display_datetime(*central_time, verbose=verbose))
                datetime_embed.add_field(name='Eastern (NY)', value=display_datetime(*eastern_time, verbose=verbose))
                datetime_embed.add_field(name='London', value=display_datetime(*london_time, verbose=verbose))
                datetime_embed.add_field(name='Dubai', value=display_datetime(dubai_time[0], 'GST', verbose=verbose))
                datetime_embed.add_field(name='Tokyo', value=display_datetime(*tokyo_time, verbose=verbose))
                datetime_embed.add_field(name='Auckland', value=display_datetime(*auckland_time, verbose=verbose))

        await ctx.send(embed=datetime_embed)
    
    @commands.command(name='poll', aliases=['p'])
    async def create_poll(self, ctx, *poll_args: str):
        """Creates a new poll: $poll "title" "opt-a" "opt-b" ..."""
        logger.info(f'New poll requested by {ctx.message.author.name}')
        if len(poll_args) < 3:
            await ctx.send('Sorry, your poll needs at least 2 options!')
        elif len(poll_args) > 21:
            await ctx.send('Sorry, `$poll` only supports 20 options!')
        else:
            async with ctx.typing():
                poll_embed=generate_poll_embed(poll_args)
                result_msg = await ctx.send(embed=poll_embed)
                poll_embed.add_field(name="Poll Reference", value=result_msg.id)
                await result_msg.edit(embed=poll_embed)
                
            react_char = '\U0001f1e6'
            for arg_iter in range(1, len(poll_args)):
                await result_msg.add_reaction(react_char)
                react_char = chr(ord(react_char) + 1)
                
    @commands.command(name='collate', aliases=['pc', 'poll-collate', 'cp', 'collate-poll'])
    async def collate_poll(self, ctx, *poll_ids: str):
        """Collates and summarises the given poll references"""
        
        logger.info(f'Collating {len(poll_ids)} polls')
        
        if len(poll_ids) < 1:
            await ctx.send('Sorry, I need a poll reference to collate!')
            return
        
        async with ctx.typing():
            for id in poll_ids:
                try:
                    try:
                        poll = await ctx.fetch_message(id)
                    except discord.NotFound:
                        await ctx.send(f'Sorry, I couldn\'t find poll `{id}`')
                        continue
                    except discord.HTTPException:
                        await ctx.send(f'Sorry, `{id}` is not a valid poll id')
                        continue
                        
                    if len(poll.embeds) < 1:
                        await ctx.send(f'Sorry, I couldn\'t find the embed for poll `{id}`')
                        continue
                    
                    opt_to_react_dict = {}
                    for reaction in poll.reactions:
                        opt_to_react_dict[str(reaction.emoji)] = reaction
                    
                    poll_results = {}
                    poll_title = poll.embeds[0].title
                    for option in poll.embeds[0].description.split("\n"):
                        key = emoji.emojize(option[0:option.find(' ')], use_aliases=True)
                        desc = option[option.find(' ') + 1:]
                        poll_results[desc] = int(opt_to_react_dict[key].count)
                    
                    data = pd.Series(poll_results)
                    axes = data.plot.bar(title=poll_title, x='options', color=plt.cm.Paired(range(len(data))))
                    axes.set_ylabel('Respondents')
                    
                    png_wrapper = io.BytesIO()
                    plt.savefig(png_wrapper, format='png')
                    png_wrapper.seek(0)

                    await ctx.send(file=discord.File(png_wrapper, filename=(poll_title + ".png")))
                except KeyError:
                    await ctx.send(f'Uh oh, I was unable to collate poll `{id}`. Sorry!')

def setup(bot):
    bot.add_cog(Utilities(bot))
