import discord
from discord.ext import commands


class AutoRole:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='lfg-add')  # , aliases=['game-role', 'lfg-role'])
    @commands.guild_only()
    async def add_roles(self, ctx, *roles: str):  # roles: list):
        """Adds Game Mode roles for @ pings.

        Uses either short names like 'c' for crucible, or full names like 'gambit'.

        Multiple roles can be added at once, e.g. `$lfg-add c g` adds @crucible and @gambit.
        """

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

        for r in roles:
            for role, allowed_names in role_dict.items():
                for name in allowed_names:
                    if r == name:
                        roles_to_add.add(role)
                        break

        print(f'Roles to Add: {roles_to_add}')
        print(f'Role Dict: {role_dict}')

        if not list(roles_to_add):
            return

        # Build list of roles to add
        new_roles = [discord.utils.get(ctx.guild.roles, name=role) for role in roles_to_add]

        # Add check if roles are already applied and avoid doing it again

        print(f'New Roles: {new_roles}')
        #role = discord.utils.get(ctx.guild.roles, name="role to add name")
        user = ctx.message.author
        await user.add_roles(*new_roles)
        await ctx.send(f'{ctx.message.author.mention} added Game Mode roles `{", ".join(roles_to_add)}`')

    @commands.command(name='lfg-remove')  # , aliases=['game-role', 'lfg-role'])
    @commands.guild_only()
    async def remove_roles(self, ctx, *roles: str):  # roles: list):
        """Removes Game Mode roles for @ pings.

        Uses either short names like 'c' for crucible, or full names like 'gambit'.
        
        Multiple roles can be removed at once, e.g. `$lfg-remove c g` removes @crucible and @gambit.
        """

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

        for r in roles:
            for role, allowed_names in role_dict.items():
                for name in allowed_names:
                    if r == name:
                        roles_to_add.add(role)
                        break

        print(f'Roles to Add: {roles_to_add}')
        print(f'Role Dict: {role_dict}')

        if not list(roles_to_add):
            return

        # Build list of roles to add
        new_roles = [discord.utils.get(ctx.guild.roles, name=role) for role in roles_to_add]

        # Add check if roles are already applied and avoid doing it again

        print(f'New Roles: {new_roles}')
        #role = discord.utils.get(ctx.guild.roles, name="role to add name")
        user = ctx.message.author
        await user.remove_roles(*new_roles)
        await ctx.send(f'{ctx.message.author.mention} removed Game Mode roles `{", ".join(roles_to_add)}`')


def setup(bot):
    bot.add_cog(AutoRole(bot))
