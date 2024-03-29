"""Utilities Cog"""

import logging
# from typing import Any, List, Dict, Tuple, Sequence
import datetime

import aiohttp

from discord.ext import commands

from modules.custom_embed import default_embed

logger = logging.getLogger('voluspa.cog.utilities')


async def get_online_datetime(location):
    """Gets online datetime from https://worldtimeapi.org/"""
    worldtimeapi_url = f'https://www.worldtimeapi.org/api/timezone/{location}'
    async with aiohttp.ClientSession() as session:
        async with session.get(worldtimeapi_url) as resp:
            if resp.status == 200:
                json_resp = await resp.json()
                #datetime_str = json_resp['datetime']
                #return json_resp  #, datetime_str
                return parse_datetime(json_resp['datetime']), json_resp['abbreviation']

            logger.info('Error: Unable to retrieve time for: %s | Resp: %s', location, resp)
            return None, None


def parse_datetime(dt_str):
    """Parses and returns a datetime"""
    return datetime.datetime.strptime(dt_str, '%Y-%m-%dT%H:%M:%S.%f%z')


def display_datetime(datetime_str, time_zone=None, verbose=True):
    """Returns a formatted datetime with TZ (if provided) or 'Error (Missing)"""
    # >>> print(datetime.datetime.utcnow().strftime("%Y/%m/%d %a %I:%M %p"))
    # 2019/05/19 Sun 01:10 AM
    if datetime_str:  # and type(datetime_str) == datetime.datetime.now():
        if verbose:
            return f'{datetime_str.strftime("%Y/%m/%d %a %I:%M %p")}{f" ({time_zone})" if time_zone else ""}'
        return f'{datetime_str.strftime("%a %I:%M %p")}{f" ({time_zone})" if time_zone else ""}'
    return 'Error (Missing)'


class Utilities(commands.Cog):
    """Helpful utility functions"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='emotes-list', aliases=['el'])
    @commands.is_owner()
    async def custom_emotes_list(self, ctx):
        """Displays a list of all custom emojis"""
        bot_emojis = self.bot.emojis
        guild_emojis = ctx.guild.emojis
        # logger.info(f'Bot Emojis: {nl.join(bot_emojis)}\n')
        # logger.info(f'Guild Emojis: {nl.join(guild_emojis)}\n')
        logger.info('bot emojis: %s', bot_emojis)
        logger.info('guild emojis: %s', guild_emojis)

    @commands.command(name='time', aliases=['clock', 't'])
    @commands.guild_only()
    @commands.cooldown(1, 30)
    async def current_times(self, ctx, verbose: bool = False):
        """Current time in several time zones

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

            datetime_embed = default_embed(
                title=":globe_with_meridians: World Clocks :clock1:",
                description='Provided by Völuspá Timekeeping',
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
                berlin_time = await get_online_datetime('Europe/Berlin')
                moscow_time = await get_online_datetime('Europe/Moscow')
                shanghai_time = await get_online_datetime('Asia/Shanghai')
                australia_east_time = await get_online_datetime('Australia/Sydney')

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
                datetime_embed.add_field(name='Aussie East', value=display_datetime(*australia_east_time), inline=False)
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


async def setup(bot):
    """Cog Setup"""
    await bot.add_cog(Utilities(bot))
