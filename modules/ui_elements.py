"""Shared UI elements"""

from typing import Any
from discord.emoji import Emoji
from discord.enums import ButtonStyle
from discord.partial_emoji import PartialEmoji
from github import Github

import discord

from modules.config import CONFIG
from cogs.config.roles import ROLES

ROLE_TYPES = ['topics', 'game_modes', 'other_games']
MAX_SELECT_OPTIONS = 25

class FeedbackModal(discord.ui.Modal, title="Feedback"):
    """Creates and handles a Feedback Modal"""
    feedback = discord.ui.TextInput(label="Enter your feedback here:", style=discord.TextStyle.long)

    async def on_submit(self, interaction: discord.Interaction): # pylint: disable=arguments-differ
        """Submits the modal"""
        feedback_channel = interaction.client.get_channel(CONFIG['Voluspa']['feedback_channel_id'])
        await feedback_channel.send(f"Incoming message for the Vanguard:\n>>> {self.children[0].value}")
        await interaction.response.send_message(content="Your feedback has been sent.", ephemeral=True)

class IssueModal(discord.ui.Modal, title="New Github Issue"):
    """Creates and handles a GitHub Issue Modal"""
    issue_title = discord.ui.TextInput(label="Issue Title", style=discord.TextStyle.short)
    body = discord.ui.TextInput(label="Issue Body", style=discord.TextStyle.long)

    async def on_submit(self, interaction: discord.Interaction): # pylint: disable=arguments-differ
        """Submits the modal"""
        ghub = Github(CONFIG['Github']['token'])
        repo = ghub.get_repo(CONFIG['Github']['repo_name'])
        issue = repo.create_issue(title=str(self.issue_title), body=str(self.body))

        await interaction.response.send_message(
            content=f'Your issue has been created _([#{issue.number}]({issue.html_url}))_',
            ephemeral=True
            )

def role_names_to_roles(role_names: list, roles_to_search):
    """Returns list of Role objects that exist in roles_to_search keyed by role_names"""
    return [role for role in (discord.utils.get(roles_to_search, name=role_name) for role_name in role_names) if role is not None]

class ManageMembershipView(discord.ui.View):
    """View for managing a guild member's membership"""
    def __init__(self, member):
        super().__init__()
        self.member = member
        self.add_roles = []
        self.remove_roles = []

    async def run(self, interaction, verb):
        """Adds and removes respective roles for a member"""
        self.clear_items()

        self.add_roles = role_names_to_roles(self.add_roles, self.member.guild.roles)
        self.remove_roles = role_names_to_roles(self.remove_roles, self.member.roles)
        if self.add_roles:
            await self.member.add_roles(*self.add_roles)
        if self.remove_roles:
            await self.member.remove_roles(*self.remove_roles)

        await interaction.response.edit_message(content=f'{verb} {self.member.display_name}', view=self)

    @discord.ui.button(label='Quarantine')
    async def quarantine(self, interaction, button: discord.ui.Button) -> None: # pylint: disable=unused-argument
        """Button to quarantine the member"""
        self.remove_roles = ['ghost-proxy-member',
                             'ghost-proxy-envoy',
                             'ghost-proxy-friend',
                             'ghost-proxy-legacy',
                             'crucible-lead',
                             'gambit-lead',
                             'raid-lead',
                             'strike-nf-pve-lead',]

        await self.run(interaction, 'Quarantined')

    @discord.ui.button(label='Set Friend')
    async def set_friend(self, interaction: discord.Interaction, button: discord.ui.Button) -> None: # pylint: disable=unused-argument
        """Button to make the member a friend"""
        self.add_roles = ['ghost-proxy-friend',]

        if 'ghost-proxy-member' in (role.name for role in self.member.roles):
            self.add_roles.append('ghost-proxy-legacy')

        self.remove_roles = ['ghost-proxy-member',
                             'ghost-proxy-envoy',
                             'crucible-lead',
                             'gambit-lead',
                             'raid-lead',
                             'strike-nf-pve-lead',]

        await self.run(interaction, 'Set friend for')

    @discord.ui.button(label='Set Envoy')
    async def set_envoy(self, interaction: discord.Interaction, button: discord.ui.Button) -> None: # pylint: disable=unused-argument
        """Button to make the member an envoy"""
        self.add_roles = ['ghost-proxy-envoy',
                          'ghost-proxy-friend',]

        if 'ghost-proxy-member' in (role.name for role in self.member.roles):
            self.add_roles.append('ghost-proxy-legacy')

        self.remove_roles = ['ghost-proxy-member',]

        await self.run(interaction, 'Set envoy for')

    @discord.ui.button(label='Set Member')
    async def set_member(self, interaction: discord.Interaction, button: discord.ui.Button) -> None: # pylint: disable=unused-argument
        """Button to make the member a member (of gp destiny clan)"""
        self.add_roles = ['ghost-proxy-member',]

        self.remove_roles = ['ghost-proxy-friend',
                             'ghost-proxy-legacy',
                             'ghost-proxy-envoy',]

        await self.run(interaction, 'Set member for')

class ManageRolesView(discord.ui.View):
    """A View to manage your optional roles"""
    def __init__(self, *, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        for role_type in ROLE_TYPES:
            buttons = self.get_buttons(role_type)
            for button in buttons:
                self.add_item(button)

        self.add_item(QuitButton(label='Done'))

    def get_page_string(self, i, max_len):
        """
        Returns page number string for a button label
        If no paging, don't give a page number, else give a page number
        """
        if max_len <= MAX_SELECT_OPTIONS:
            return ''
        if i == 0:
            return ' (1)'
        return ' (' + str(int(i / MAX_SELECT_OPTIONS + 1)) + ')'

    def get_buttons(self, role_type):
        """Returns list of buttons to go in ManageRolesView"""
        # Prettify the button labels
        match role_type:
            case 'game_modes':
                role_type_label = 'Game Modes'
            case 'other_games':
                role_type_label = 'Other Games'
            case 'topics':
                role_type_label = 'Hidden Channels'
            case _:
                role_type_label = 'Not Implemented'

        ret = []
        # Cast the ROLES dict to list of tuples to guarantee order
        roles = list(ROLES[role_type].items())
        # Since Discord supports 25 max options per Select, we want to split the roles up into separate buttons if they overflow
        for i in range(0, len(roles), MAX_SELECT_OPTIONS):
            options = {}
            for role in roles[i:i + MAX_SELECT_OPTIONS]:
                options[role[0]] = role[1]
                # SelectMenuButton leads to RoleSelectView
            ret += [SelectMenuButton(label=f'{role_type_label}{self.get_page_string(i, len(roles))}', options=options)]

        return ret

class RoleSelectView(discord.ui.View):
    """Has a select menu with roles to select for yourself, then apply or cancel"""
    def __init__(self, *, timeout: float | None = 180, options: list[dict] | None = None, user):
        super().__init__(timeout=timeout)
        select_options = []
        # Make sure the roles the user already has are selected by default
        for role_name, alias_list in options.items():
            is_enabled = False
            for user_role in user.roles:
                if user_role.name == role_name:
                    is_enabled = True
                    break
            select_options += [discord.SelectOption(label=f'@{role_name}', description=alias_list[0].title(), default=is_enabled)]

        self.select = DeferSelect(min_values=0, max_values=len(select_options), options=select_options)

        self.add_item(self.select)
        self.add_item(ApplyRolesButton(label='Save', user=user, select=self.select))
        self.add_item(BackButton(label='Cancel'))

class ApplyRolesButton(discord.ui.Button):
    """Button that applies roles you have selected in RoleSelectView"""
    def __init__(self, *, style: ButtonStyle = ButtonStyle.secondary, label: str | None = None, disabled: bool = False,
                 custom_id: str | None = None, url: str | None = None, emoji: str | Emoji | PartialEmoji | None = None,
                 row: int | None = None, user, select: discord.ui.Select):
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)
        self.user = user
        self.select = select

    async def callback(self, interaction: discord.Interaction) -> Any:
        # [:1] to strip leading '@'
        add_roles = [value[1:] for value in self.select.values]
        remove_roles = [option.label[1:] for option in self.select.options if option.label[1:] not in add_roles]

        add_roles = role_names_to_roles(add_roles, self.user.guild.roles)
        remove_roles = role_names_to_roles(remove_roles, self.user.roles)

        if add_roles:
            await self.user.add_roles(*add_roles)
        if remove_roles:
            await self.user.remove_roles(*remove_roles)

        await interaction.response.edit_message(content='Manage your roles.', view=ManageRolesView())

class SelectMenuButton(discord.ui.Button):
    """Button that spawns the correct RoleSelectView from ManageRolesView"""
    def __init__(self, *, style: ButtonStyle = ButtonStyle.secondary, label: str | None = None, disabled: bool = False,
                 custom_id: str | None = None, url: str | None = None, emoji: str | Emoji | PartialEmoji | None = None,
                 row: int | None = None, options: list[dict] | None = None):
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)
        self.options = options

    async def callback(self, interaction: discord.Interaction) -> Any:
        await interaction.response.edit_message(content='', view=RoleSelectView(options=self.options, user=interaction.user))

class BackButton(discord.ui.Button):
    """Button to return from RoleSelectView to ManageRolesView"""
    async def callback(self, interaction: discord.Interaction) -> Any:
        await interaction.response.edit_message(content='Manage your roles.', view=ManageRolesView())

class QuitButton(discord.ui.Button):
    """Button to 'quit' an interaction"""
    async def callback(self, interaction: discord.Interaction) -> Any:
        await interaction.response.edit_message(content="Thanks!", view=None)

class DeferSelect(discord.ui.Select):
    """Overrides a Select so that bluring will not process the interaction"""
    async def callback(self, interaction: discord.Interaction) -> Any:
        await interaction.response.defer()
