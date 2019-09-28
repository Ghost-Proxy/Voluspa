# import re
# import asyncio
import aiohttp
import io
import logging
# from typing import Any, List, Dict, Tuple, Sequence
import datetime

# 3rd-party
import pandas as pd
import matplotlib.pyplot as plt
import emoji
from textwrap import wrap

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

def gen_yticks(max_pt):
    """Generates an array of y-axis ticks in integers - step is determined by the largest data point"""
    if max_pt <= 10:
        step = 1
    elif max_pt <= 50:
        step = 5
    elif max_pt <= 100:
        step = 10
    elif max_pt <= 500:
        step = 50
    else:
        step = 100
    
    return range(0, max_pt + step, step)

def trunc_label(label, num_opts=None, max_lines=None, max_length=25):
    """Breaks the label up into 25 character max lines."""
    """If the label space is too small, only some lines will be append and the rest will be represented with ..."""
    if max_lines == None:
        if num_opts <= 4:
            max_lines = 4
        elif num_opts <= 6:
            max_lines = 3
        elif num_opts <= 8:
            max_lines = 2
        else:
            max_lines = 1
        
    res = wrap(label, max_length)
    res_full_length = len(res)
    res = res[:min(res_full_length, max_lines)]
    
    return "\n".join(res) + ("..." if res_full_length > max_lines else "")

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
        """Creates a new poll
        
        $poll "title" "opt-a" "opt-b" ...
        """
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
                
    @commands.command(name='collate', aliases=['c', 'cd', 'collate-dark'])
    async def collate_poll(self, ctx, *poll_ids: str):
        """Summarises the given poll references
        
        Use $cd for dark theme
        
        Use $c c<channel-id> <poll-args>... to specify a channel to pull from
        """
        
        logger.info(f'Collating {len(poll_ids)} polls')
        
        if (len(poll_ids) > 0 and poll_ids[0][0] == 'c'):
            id_fetch_point = ctx.bot.get_channel(int(poll_ids[0][1:]))
            if id_fetch_point == None:
                await ctx.send(f'Sorry, `{poll_ids[0][1:]}` is not a valid channel id.')
                return
            
            poll_ids = poll_ids[1:]
        else:
            id_fetch_point = ctx.channel
        
        if len(poll_ids) < 1:
            await ctx.send('Sorry, I need a poll reference to collate!')
            return
        
        async with ctx.typing():
            for id in poll_ids:
                try:
                    try:
                        poll = await id_fetch_point.fetch_message(id)
                    except discord.NotFound:
                        await ctx.send(f'Sorry, I couldn\'t find poll `{id}`')
                        continue
                    except discord.HTTPException:
                        await ctx.send(f'Sorry, `{id}` is not a valid poll id')
                        continue
                        
                    if len(poll.embeds) < 1:
                        await ctx.send(f'Sorry, I couldn\'t find the embed for poll `{id}`')
                        continue
                                    
                    poll_labels = []
                    poll_results = []
                    poll_title = trunc_label(poll.embeds[0].title, max_lines=2, max_length=50)
                    
                    for option in poll.embeds[0].description.split("\n"):
                        key = emoji.emojize(option[:option.find(' ')], use_aliases=True)
                        desc = option[option.find(' ') + 1:]
                        
                        poll_labels.append(trunc_label(desc, len(poll.reactions)))
                        
                        # If polls options don't match reactions, list has been messed with
                        # Else get count for option
                        reaction = next((r for r in poll.reactions if r.emoji == key), None)
                        if reaction == None:
                            raise KeyError()
                        poll_results.append(reaction.count - 1)
                    
                    data = pd.Series(poll_results, index=poll_labels)
                        
                    axes = data.plot.bar(title=poll_title, x='options', color=plt.cm.tab10(range(len(data))))
                    axes.set_ylabel('Respondents')
                    
                    if ctx.invoked_with in ['cd', 'collate-dark']:
                        line_colors = "#FFFFFF"
                        
                        axes.spines['bottom'].set_color(line_colors)
                        axes.spines['top'].set_color(line_colors)
                        axes.spines['left'].set_color(line_colors)
                        axes.spines['right'].set_color(line_colors)
                        
                        axes.tick_params(colors=line_colors)
                        
                        axes.yaxis.label.set_color(line_colors)
                        axes.xaxis.label.set_color(line_colors)
                        
                        axes.title.set_color(line_colors)
                        
                        axes.set_facecolor("#2C2F33")
                        
                        bg_color = "#2C2F33"
                        bar_top_color = line_colors
                    else:
                        bg_color = "#FFFFFF"
                        bar_top_color = "k" # aka black
                    
                    # New padding technique for top of chart and bar text
                    _, top_ylim = plt.ylim()
                    top_ylim *= 1.02
                    plt.ylim(bottom=0, top=top_ylim)
                    
                    plt.yticks(gen_yticks(max(poll_results))) # Appropriate tick spacing for number of respondents                    
                    plt.xticks(rotation=45)
                    
                    # Adds number of respondents at top of bars
                    for x, y in enumerate(poll_results):
                        axes.text(x, y, str(y), ha='center', va='bottom', color=bar_top_color)
                    
                    plt.tight_layout() # Ensures label text is not cut off
                    
                    png_wrapper = io.BytesIO()
                    plt.savefig(png_wrapper, format='png', facecolor=bg_color)
                    png_wrapper.seek(0)

                    dt = datetime.datetime
                    filename = "gp-poll-" + id + "-" + dt.strftime(dt.utcnow(), "%Y-%m-%d-%H-%M-%S") + ".png"
                    await ctx.send(file=discord.File(png_wrapper, filename=filename))
                    
                    png_wrapper.close()
                    plt.close()
                except KeyError:
                    await ctx.send(f'Uh oh, I was unable to collate poll `{id}`. Sorry!')

def setup(bot):
    bot.add_cog(Utilities(bot))
