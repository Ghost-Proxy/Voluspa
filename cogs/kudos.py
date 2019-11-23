import logging

import modules.cache as cache

import discord
from discord.ext import commands

logger = logging.getLogger('voluspa.cog.kudos')


class Kudos(commands.Cog):
    """Test of Kudos :)"""
    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=['k', 'kudo'])
    async def kudos(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid _kudos_ command.')

    @kudos.command(name='view-player', aliases=['view player', 'vp'])
    async def view_player_kudos(self, ctx):
        await ctx.send('view_player_kudos')

    @kudos.command(name='view-leaderboard', aliases=['view leaderboard', 'vl'])
    async def view_kudos_leaderboard(self, ctx):
        await ctx.send('view_kudos_leaderboard')

    @kudos.command(name='send', aliases=['s'])
    async def send_kudos(self, ctx):
        await ctx.send('send_kudos')


def setup(bot):
    bot.add_cog(Kudos(bot))

