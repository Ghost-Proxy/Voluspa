"""Kudos Cog"""

import logging

from discord.ext import commands

logger = logging.getLogger('voluspa.cog.kudos')


class Kudos(commands.Cog):
    """Test of Kudos :)"""
    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=['k', 'kudo'])
    async def kudos(self, ctx):
        """Kudos! View help for more info..."""
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid _kudos_ command.')

    @kudos.command(name='view-player', aliases=['vp'])
    async def view_player_kudos(self, ctx):
        """View Player Kudos"""
        await ctx.send('view_player_kudos')

    @kudos.command(name='view-leaderboard', aliases=['vl'])
    async def view_kudos_leaderboard(self, ctx):
        """View Kudos Leaderboard"""
        await ctx.send('view_kudos_leaderboard')

    @kudos.command(name='send', aliases=['s'])
    async def send_kudos(self, ctx):
        """Send Kudos"""
        await ctx.send('send_kudos')


async def setup(bot):
    """Cog Setup"""
    await bot.add_cog(Kudos(bot))
