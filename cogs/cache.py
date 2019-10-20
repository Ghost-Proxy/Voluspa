import logging

from modules.cache import CACHE_NAME, write_cache, read_cache
from modules.custom_embed import default_embed

from discord.ext import commands

logger = logging.getLogger('voluspa.cog.cache')


class Cache(commands.Cog):
    """Test of Caches"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='cache-write', aliases=['cw', 'ca', 'cache-add'])
    @commands.has_any_role('founder', 'ghost-proxy-vanguard', 'ghost-proxy-gatekeeper')
    async def cache_write(self, ctx, cache_key: str, *, cache_value: str):
        """Writes key/value to cache"""
        cache_name = CACHE_NAME
        if 'cache_name=' in cache_key:
            cache_name = cache_key.split('cache_name=')[1]
            cache_key, cache_value = cache_value.split(' ')
        await write_cache(cache_key, cache_value, cache_name=cache_name)
        embed = default_embed(
            title='Cache Write (K/V)',
            description=f'Wrote the following Key/Value to "{cache_name}" cache'
        )
        embed.add_field(
            name=f'{cache_key}',
            value=f'{cache_value}',
            inline=False
        )
        await ctx.send(embed=embed)

    @commands.command(name='cache-read', aliases=['cr', 'cg', 'cache-get'])
    @commands.has_any_role('founder', 'ghost-proxy-vanguard', 'ghost-proxy-gatekeeper')
    async def cache_read(self, ctx, *, cache_key: str):
        """Reads value for key from cache"""
        cache_name = CACHE_NAME
        if 'cache_name=' in cache_key:
            cache_name, cache_key = cache_key.split(' ')
            cache_name = cache_name.split('cache_name=')[1]
        cache_value = await read_cache(cache_key, cache_name=cache_name)
        embed = default_embed(
            title='Cache Read (K/V)',
            description=f'Read the following Key/Value from "{cache_name}" cache'
        )
        embed.add_field(
            name=f'{cache_key}',
            value=f'{cache_value}',
            inline=False
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Cache(bot))