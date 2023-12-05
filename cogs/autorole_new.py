import discord
from discord.ext import commands

class ManageMembershipView(discord.ui.View):
    def __init__(self, member):
        super().__init__()
        self.member = member
        self.add_roles = []
        self.remove_roles = []
    
    def role_names_to_roles(self, role_names: list, roles_to_search):
        return [role for role in (discord.utils.get(roles_to_search, name=role_name) for role_name in role_names) if role is not None]

    async def run(self, interaction, verb):
        self.clear_items()

        self.add_roles = self.role_names_to_roles(self.add_roles, self.member.guild.roles)
        self.remove_roles = self.role_names_to_roles(self.remove_roles, self.member.roles)
        if self.add_roles: await self.member.add_roles(*self.add_roles)
        if self.remove_roles: await self.member.remove_roles(*self.remove_roles)
        
        await interaction.response.edit_message(content=f'{verb} {self.member.display_name}', view=self)

    @discord.ui.button(label='Quarantine')
    async def quarantine(self, interaction, button: discord.ui.Button) -> None:
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
    async def set_friend(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
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
    async def set_envoy(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.add_roles = ['ghost-proxy-envoy',
                          'ghost-proxy-friend',]

        if 'ghost-proxy-member' in (role.name for role in self.member.roles):
            self.add_roles.append('ghost-proxy-legacy')
            
        self.remove_roles = ['ghost-proxy-member',]

        await self.run(interaction, 'Set envoy for')

    @discord.ui.button(label='Set Member')
    async def set_member(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.add_roles = ['ghost-proxy-member',]

        self.remove_roles = ['ghost-proxy-friend',
                             'ghost-proxy-legacy',
                             'ghost-proxy-envoy',]
        
        await self.run(interaction, 'Set member for')

@discord.app_commands.context_menu(name='Manage Membership')
@discord.app_commands.guild_only()
@discord.app_commands.checks.has_role('ghost-proxy-vanguard')
async def manage_membership(interaction: discord.Interaction, member: discord.Member) -> None:
    await interaction.response.send_message(f"Manage membership for {member.display_name}", view=ManageMembershipView(member), ephemeral=True)

async def setup(bot):
    bot.tree.add_command(manage_membership)