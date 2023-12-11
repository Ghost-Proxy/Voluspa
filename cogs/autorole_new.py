"""New implementation of Autorole using Discord UI Kit"""
import discord
from discord.ext import commands

from modules.ui_elements import ManageMembershipView, ManageRolesView

@discord.app_commands.context_menu(name='Manage Membership')
@discord.app_commands.guild_only()
@discord.app_commands.checks.has_role('ghost-proxy-vanguard')
async def manage_membership(interaction: discord.Interaction, member: discord.Member) -> None:
    """Manage friend, envoy and member status for a member (vanguard only)"""
    await interaction.response.send_message(f"Manage membership for {member.display_name}",
                                            view=ManageMembershipView(member),
                                            ephemeral=True)

class Autorole(commands.Cog):
    """Automatic role management"""
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command()
    @discord.app_commands.guild_only()
    async def roles(self, interaction: discord.Interaction):
        """Manage game modes, topic channels and other game roles for yourself"""
        await interaction.response.send_message('Manage your roles.', view=ManageRolesView(), ephemeral=True)

async def setup(bot):
    """discord.py setup hook"""
    bot.tree.add_command(manage_membership)
    await bot.add_cog(Autorole(bot))
