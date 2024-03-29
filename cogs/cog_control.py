"""Meta Cog Cog"""

from discord.ext import commands

# From: https://gist.github.com/EvieePy/d78c061a4798ae81be9825468fe146be#file-owner-py


class CogControl(commands.Cog):
    """Cog for controlling Cogs"""
    # TODO: Use sub-command pattern... :D
    def __init__(self, bot):
        self.bot = bot

    # Hidden means it won't show up on the default help.
    @commands.command(name='load', hidden=True)
    @commands.is_owner()
    async def load(self, ctx, *, cog: str):
        """Command which Loads a Module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            self.bot.load_extension(cog)
        except Exception as exc: # pylint: disable=broad-exception-caught
            await ctx.send(f'**`ERROR:`** {type(exc).__name__} - {exc}')
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(name='unload', hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, *, cog: str):
        """Command which Unloads a Module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            self.bot.unload_extension(cog)
        except Exception as exc: # pylint: disable=broad-exception-caught
            await ctx.send(f'**`ERROR:`** {type(exc).__name__} - {exc}')
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, *, cog: str):
        """Command which Reloads a Module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as exc: # pylint: disable=broad-exception-caught
            await ctx.send(f'**`ERROR:`** {type(exc).__name__} - {exc}')
        else:
            await ctx.send('**`SUCCESS`**')


async def setup(bot):
    """Cog Setup"""
    await bot.add_cog(CogControl(bot))
