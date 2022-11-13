import logging

import modules.cache as cache
from modules.custom_embed import default_embed, success_embed, error_embed

from discord.ext import commands

logger = logging.getLogger('voluspa.cog.cache')

CACHE_NAME_PREFIX = 'cache_name='


def check_for_cache_name(cache_name, cache_key, cache_value):
    if cache_value is None and CACHE_NAME_PREFIX in cache_key:
        _cache_name, cache_key = cache_key.split(' ')
        _cache_name = _cache_name.split(CACHE_NAME_PREFIX)[1]
        return _cache_name, cache_key, cache_value
    if CACHE_NAME_PREFIX in cache_key:
        _cache_name = cache_key.split(CACHE_NAME_PREFIX)[1]
        cache_key, cache_value = cache_value.split(' ')
        return _cache_name, cache_key, cache_value
    return cache_name, cache_key, cache_value


class Cache(commands.Cog):
    """Test of Caches"""
    def __init__(self, bot):
        self.bot = bot

    # TODO: This needs some refactoring/DRY'ing

    @commands.command(name='cache-add', aliases=['ca', 'cache-create'])
    @commands.has_any_role('founder', 'ghost-proxy-vanguard', 'ghost-proxy-gatekeeper')
    async def cache_add(self, ctx, cache_key: str, *, cache_value: str):
        """Adds key/value to cache

        Errors if Key already exists!"""
        cache_name, cache_key, cache_value = check_for_cache_name(
            cache.CACHE_NAME,
            cache_key,
            cache_value
        )
        try:
            await cache.add(cache_key, cache_value, cache_name=cache_name)
        except ValueError as e:
            logger.info(f'Key already exists: {e}')
            embed = error_embed(
                title='Cache Add (K/V)',
                description=f'Error adding Key/Value to "{cache_name}" cache!\n\n'
                            f'_Must use `cache-overwrite` to update Key:_\n`{cache_key}`'
            )
        else:
            embed = success_embed(
                title='Cache Add (K/V)',
                description=f'Added the following Key/Value to "{cache_name}" cache'
            )
            embed.add_field(
                name=f'{cache_key}',
                value=f'{cache_value}',
                inline=False
            )
        await ctx.send(embed=embed)

    @commands.command(name='cache-overwrite', aliases=['cow', 'cache-update'])
    @commands.has_any_role('founder', 'ghost-proxy-vanguard', 'ghost-proxy-gatekeeper')
    async def cache_overwrite(self, ctx, cache_key: str, *, cache_value: str):
        """Writes key/value to cache (CAUTION!)

        This implies creating if not present
        OR
        This implies overwriting if present"""
        cache_name, cache_key, cache_value = check_for_cache_name(
            cache.CACHE_NAME,
            cache_key,
            cache_value
        )
        original_value = await cache.read(cache_key, cache_name=cache_name)
        await cache.write(cache_key, cache_value, cache_name=cache_name)
        embed = default_embed(
            title='Cache Overwrite (K/V)',
            description=f'Overwrote the following Key/Value in "{cache_name}" cache'
        )
        embed.add_field(
            name=f'Original {cache_key}',
            value=f'{original_value}',
            inline=False
        )
        embed.add_field(
            name=f'New {cache_key}',
            value=f'{cache_value}',
            inline=False
        )
        await ctx.send(embed=embed)

    @commands.command('cache-append', aliases=['cap'])
    @commands.has_any_role('founder', 'ghost-proxy-vanguard', 'ghost-proxy-gatekeeper')
    async def cache_append(self, ctx, cache_key: str, *, cache_value: str):
        """Appends value to key in cache"""
        cache_name, cache_key, cache_value = check_for_cache_name(
            cache.CACHE_NAME,
            cache_key,
            cache_value
        )
        original_value = await cache.read(cache_key, cache_name=cache_name)
        if original_value is not None:
            cache_value = f'{original_value}\n{cache_value}'
        await cache.write(cache_key, cache_value, cache_name=cache_name)
        embed = default_embed(
            title='Cache Append (K/V)',
            description=f'Updated the following Key/Value in "{cache_name}" cache'
        )
        embed.add_field(
            name=f'Original {cache_key}',
            value=f'{original_value}',
            inline=False
        )
        embed.add_field(
            name=f'Updated {cache_key}',
            value=f'{cache_value}',
            inline=False
        )
        await ctx.send(embed=embed)

    @commands.command(name='cache-read', aliases=['cr', 'cg', 'cache-get'])
    @commands.has_any_role('founder', 'ghost-proxy-vanguard', 'ghost-proxy-gatekeeper')
    async def cache_read(self, ctx, *, cache_key: str):
        """Reads value for key from cache"""
        cache_name, cache_key, _ = check_for_cache_name(cache.CACHE_NAME, cache_key, None)
        cache_value = await cache.read(cache_key, cache_name=cache_name)
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

    @commands.command(name='cache-delete', aliases=['cd'])  # , 'cr', 'cache-remove'])
    @commands.has_any_role('founder', 'ghost-proxy-vanguard', 'ghost-proxy-gatekeeper')
    async def cache_delete(self, ctx, *, cache_key: str):
        """Deletes key/value from cache (CAUTION!)"""
        cache_name, cache_key, _ = check_for_cache_name(cache.CACHE_NAME, cache_key, None)
        cache_value = await cache.delete(cache_key, cache_name=cache_name)
        embed = default_embed(
            title='Cache Delete (K/V)',
            description=f'Deleted the following Key from "{cache_name}" cache'
        )
        embed.add_field(
            name=f'{cache_key}',
            value=f'_deleted_',
            inline=False
        )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Cache(bot))
