from modules.paging import MenuWithOptions

from discord.ext import commands

class TestCog(commands.Cog):
    @commands.command()
    async def menutest(self, ctx):
        title = 'Generic Paging Test'
        options = ['Option 1', 'Option 2', 'Option 3']
        menu = MenuWithOptions(ctx, title, options=options, max_lines_per_page=2)
        await menu.run()

def setup(bot):
    bot.add_cog(TestCog())
