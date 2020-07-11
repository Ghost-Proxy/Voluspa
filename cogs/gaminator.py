import logging

from cogs.config.roles import ROLES
from modules.paging import MenuWithOptions

from discord.ext import commands

logger = logging.getLogger('voluspa.cog.gaminator')

TAB_LENGTH = 10
MAX_LINES_PER_PAGE = 7

class OtherGamesMenu(MenuWithOptions):
    # Override
    def update_feedback_ui(self):
        ctx = self.get_ctx()
        adding = []
        removing = []
        for option in self.get_selected_options():
            if option[0] not in [role.name for role in ctx.message.author.roles]:
                adding.append(f'`@{option[0]}`')
            else:
                removing.append(f'`@{option[0]}`')

        self.set_feedback_ui_field_at(0, 'Adding', '\n'.join(adding), 'None')
        self.set_feedback_ui_field_at(1, 'Removing', '\n'.join(removing), 'None')

    # Override
    def option_to_string(self, option):
        role_name = option[0]
        padding = (TAB_LENGTH - len(role_name)) * '\u2000'
        qualified_name = option[1][0].title()

        return f'`@{role_name}`{padding}{qualified_name}'

class Gaminator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='other-games', aliases=['og'])
    @commands.cooldown(1, 1800, commands.BucketType.user)
    async def other_games(self, ctx):
        logger.info(f'{ctx.message.author} called other_games')

        options = ROLES['other_games'].items()
        menu = OtherGamesMenu(ctx, 'Other Games', options=options, max_lines_per_page=MAX_LINES_PER_PAGE)
        menu.add_feedback_ui_field('Adding', 'None')
        menu.add_feedback_ui_field('Removing', 'None')

        try:
            await menu.run()
            if len(menu.get_selected_options()) > 0:
                autorole = self.bot.get_cog('Autorole')
                adding = []
                removing = []
                for option in menu.get_selected_options():
                    if option[0] not in [role.name for role in ctx.message.author.roles]:
                        adding.append(option)
                    else:
                        removing.append(option)

                if len(adding) > 0:
                    await autorole.other_game_add(ctx, *[option[1][0] for option in adding])
                if len(removing) > 0:
                    await autorole.other_game_remove(ctx, *[option[1][0] for option in removing])
        finally:
            self.bot.get_command('other-games').reset_cooldown(ctx)

def setup(bot):
    bot.add_cog(Gaminator(bot))
