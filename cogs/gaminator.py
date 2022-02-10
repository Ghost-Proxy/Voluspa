import logging

from cogs.config.roles import ROLES
from modules.paging import MenuWithOptions

from discord.ext import commands

logger = logging.getLogger('voluspa.cog.gaminator')

TAB_LENGTH = 10
MAX_LINES_PER_PAGE = 7


def get_longest_role_name(role_dict):
    longest_role = 0
    for role, role_options in role_dict.items():
        for role_option in role_options:
            if len(role_option) > longest_role:
                longest_role = len(role_option)
    return longest_role


def get_tab_length(default, longest_item, buffer=4):
    return default if default > longest_item else longest_item + buffer


DESTINY_ROLE_TAB_LENGTH = get_tab_length(TAB_LENGTH, get_longest_role_name(ROLES['game_modes']))


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


# Hmm... (figure out a means to DRY)
class DestinyRoleMenu(MenuWithOptions):
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
        padding = (DESTINY_ROLE_TAB_LENGTH - len(role_name)) * '\u2000'
        qualified_name = option[1][0].title()

        return f'`@{role_name}`{padding}{qualified_name}'


class Gaminator(commands.Cog):
    """Wizards for setting @ roles and more!"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='other-games', aliases=['og', 'games'])
    @commands.cooldown(1, 1800, commands.BucketType.user)
    async def other_games(self, ctx):
        """Wizard to enable channels of other games

        Provides a role wizard that adds specific other game @ roles
        and makes the related Other Game channel visible.
        """
        logger.info(f'{ctx.message.author} called other_games')

        options = ROLES['other_games'].items()
        # We could do this dynamically!
        # Get a list of all server roles, filter for anything starting with `og-`
        # fetch/build list everyday at midnight UTC and during reboot/spawn, then cache
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

    @commands.command(name='game-roles', aliases=['gr', 'game-modes', 'gm'])
    @commands.cooldown(1, 1800, commands.BucketType.user)
    async def game_roles(self, ctx):
        """Wizard to enable Destiny 2 game mode roles

        Provides a role wizard that adds the Destiny 2 @ game mode roles.
        """
        logger.info(f'{ctx.message.author} called game_roles')

        options = ROLES['game_modes'].items()
        menu = DestinyRoleMenu(ctx, 'Destiny Game Roles', options=options, max_lines_per_page=MAX_LINES_PER_PAGE)
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
                    await autorole.lfg_add(ctx, *[option[1][0] for option in adding])
                if len(removing) > 0:
                    await autorole.lfg_remove(ctx, *[option[1][0] for option in removing])
        finally:
            self.bot.get_command('game-roles').reset_cooldown(ctx)


def setup(bot):
    bot.add_cog(Gaminator(bot))
