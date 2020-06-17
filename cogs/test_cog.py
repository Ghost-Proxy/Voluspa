import logging

from modules.paging import MenuWithCustomOptions

from discord.ext import commands

logger = logging.getLogger('voluspa.cog.test_cog')

class TestMenu(MenuWithCustomOptions):
    def init_feedback_ui(self):
        self.add_feedback_ui_field(name='You Selected', value='None')

    def update_feedback_ui(self):
        field = '\n'.join([self.option_to_string(o) for o in self.get_selected_options()])
        self.set_feedback_ui_field_at(0, name='You Selected', value=field, default='None')

    def option_to_string(self, option):
        return option['string']

class TestCog(commands.Cog):
    @commands.command()
    async def menutest(self, ctx):
        title = 'Generic Paging Test'
        options = {'\U0001f44d': {'string': 'Option 1'}, 'thumbsdown': {'string': 'Option 2'}, ':raised_hand:': {'string': 'Option 3'}}
        menu = TestMenu(ctx, title, options=options, max_lines_per_page=2)
        await menu.run()
        logger.info(menu.get_selected_options())

def setup(bot):
    bot.add_cog(TestCog())
