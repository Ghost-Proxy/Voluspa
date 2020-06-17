from modules.paging import MenuWithCustomOptions

from discord.ext import commands

class TestMenu(MenuWithCustomOptions):
    def init_feedback_ui(self):
        self.add_feedback_ui_field(name='You Selected', value='None')

    def update_feedback_ui(self):
        field = '\n'.join(self.get_selected_options())
        self.set_feedback_ui_field_at(0, name='You Selected', value=field, default='None')

class TestCog(commands.Cog):
    @commands.command()
    async def menutest(self, ctx):
        title = 'Generic Paging Test'
        options = {'thumbsup': 'Option 1', 'thumbsdown': 'Option 2', 'raised_hand': 'Option 3'}
        menu = TestMenu(ctx, title, options=options, max_lines_per_page=2)
        await menu.run()

def setup(bot):
    bot.add_cog(TestCog())
