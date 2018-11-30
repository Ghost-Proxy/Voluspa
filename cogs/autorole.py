import discord
from discord.ext import commands

class AutoroleCog:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='lfg', aliases=['role'])
    @commands.guild_only()
    async def update_roles(self, ctx, *args: str):  # roles: list):
        """Sets a Game Mode role for @ pings"""

        # $lfg (no param) -- Lists current LFG roles set
        # $lfg role1 role2 -- adds/removes the roles
        # $lfg all -- adds/removes all roles
        # Handle ALL Eventually...

        # Build roles
        role_list = [
            'crucible',
            'gambit',
            'raid',
            'strike-nf-pve'
        ]

        # role_dict = {role_name: [] for role_name in role_list}
        role_dict = {
            'crucible': ['c', 'crucible'],
            'gambit': ['g', 'gambit'],
            'raid': ['r', 'raid'],
            'strike-nf-pve': ['s', 'nf', 'pve', 'strike', 'nightfall', 'strike-nf-pve']
        }

        # Process input and sanitize
        roles_to_add = set()

        for r in args:
            for role, allowed_names in role_dict.items():
                for name in allowed_names:
                    if r == name:
                        roles_to_add.add(role)
                        break

        # Build list of roles to add
        new_roles = [discord.utils.get(ctx.guild.roles, name=role) for role in roles_to_add]

        #role = discord.utils.get(ctx.guild.roles, name="role to add name")
        user = ctx.message.author
        await user.add_roles(new_roles)

def setup(bot):
    bot.add_cog(AutoroleCog(bot))