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

    @commands.command()
    async def menu_test2(self, ctx):
        lorem = """
        Lorem ipsum dolor sit amet, consectetur adipiscing elit,
        sed do eiusmod tempor incididunt ut labore et dolore magna
        aliqua. Nulla aliquet porttitor lacus luctus accumsan tortor
        posuere. In fermentum et sollicitudin ac orci phasellus egestas.
        Convallis posuere morbi leo urna molestie at. Sed enim ut sem
        viverra aliquet eget sit. Dictum non consectetur a erat nam.
        Magna fringilla urna porttitor rhoncus. Lacinia quis vel eros
        donec ac odio tempor orci. Vel elit scelerisque mauris pellentesque
        pulvinar. Pharetra magna ac placerat vestibulum lectus mauris
        ultrices eros in. Tincidunt nunc pulvinar sapien et ligula
        ullamcorper malesuada proin. Nunc scelerisque viverra mauris in
        aliquam sem. Pharetra pharetra massa massa ultricies mi quis
        hendrerit dolor magna. Fermentum leo vel orci porta non
        pulvinar neque. Ut sem viverra aliquet eget sit amet. Pretium
        nibh ipsum consequat nisl vel pretium lectus quam. Semper eget
        duis at tellus at urna condimentum. Amet dictum sit amet justo
        donec enim.
        """.replace('\n', '')
        title = "Lorem ipsum dolor sit amet"

        class Meh(object):
            pass

        class Meh2(object):
            def __str__(self):
                return 'This is my str repr!!'

        m = Meh()
        m2 = Meh2()

        options = {
            'zero': {'string': lorem[10:30]},
            'one': {'string': lorem[30:50]},
            'two': {'string': lorem[50:80]},
            'three': {'string': lorem[80:110]},
            'four': {'string': lorem[110:140]},
            'five': {'string': lorem[170:200]},
            'six': {'string': lorem[200:240]},
            'seven': {'string': lorem[240:250]},
            'eight': {'string': lorem[250:280]},
            'nine': {'string': lorem[280:300]},
            'thumbsup': {'string': m},
            'smile': {'string': m},
            'palm_tree': {'string': m2},
            'exclamation': {'string': lorem[300:600]}
        }
        menu = TestMenu(ctx, title, options=options, max_lines_per_page=3)
        await menu.run()
        await ctx.send(f'Selected Options:\n{menu.get_selected_options()}')


def setup(bot):
    bot.add_cog(TestCog())
