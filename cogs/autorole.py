import discord
from discord.ext import commands

roles_dicts = {
    'game_modes': {
        'crucible': ['c', 'crucible'],
        'gambit': ['g', 'gambit'],
        'raid': ['r', 'raid'],
        'strike-nf-pve': ['s', 'nf', 'pve', 'strike', 'nightfall', 'strike-nf-pve']
    },
    'raid_leads': {
        'sherpa-active': ['on', 'active', 'true', 'enable', 'yes', '1'],
        'sherpa-inactive': ['off', 'inactive', 'false', 'disable', 'no', '0']
    }
}


async def update_roles(ctx,
                       role_dict: dict,
                       update_message: str = 'set',
                       action: str = 'add',
                       *roles: str
                       ):

    # Process input and sanitize
    roles_to_update = set()
    for r in roles:
        for role, allowed_names in role_dict.items():
            for name in allowed_names:
                if r == name:
                    roles_to_update.add(role)
                    break

    print(f'Roles to Update: {roles_to_update}')
    print(f'Role Dict: {role_dict}')

    if not list(roles_to_update):
        return

    # Build list of roles to add
    updated_roles = [discord.utils.get(ctx.guild.roles, name=role) for role in roles_to_update]

    # Add check if roles are already applied and avoid doing it again

    print(f'"Updating Roles (action: {action}): {updated_roles}')
    user = ctx.message.author

    if action == 'add':
        await user.add_roles(*updated_roles)
    elif action == 'remove':
        await user.remove_roles(*updated_roles)
    else:
        print(f"Unknown Action for Update Roles!")
        return

    await ctx.send(f'{ctx.message.author.mention} {update_message} role(s):  `{", ".join(roles_to_update)}`')


class AutoRole:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='lfg-add')  # , aliases=['game-role', 'lfg-role'])
    @commands.guild_only()
    async def lfg_add(self, ctx, *roles: str):
        """Adds Game Mode roles for @ pings.

        Uses either short names like 'c' for crucible, or full names like 'gambit'.

        Multiple roles can be added at once, e.g. `$lfg-add c g` adds @crucible and @gambit.
        """

        # $lfg (no param) -- Lists current LFG roles set
        # $lfg role1 role2 -- adds/removes the roles
        # $lfg all -- adds/removes all roles
        # Handle ALL Eventually...

        # TODO: CLEAN UP
        # Build roles
        role_list = [
            'crucible',
            'gambit',
            'raid',
            'strike-nf-pve'
        ]
        # role_dict = {role_name: [] for role_name in role_list}

        await update_roles(ctx, roles_dicts['game_modes'], 'added Game Mode', action='add', *roles)

    @commands.command(name='lfg-remove')  # , aliases=['game-role', 'lfg-role'])
    @commands.guild_only()
    async def lfg_remove(self, ctx, *roles: str):
        """Removes Game Mode roles for @ pings.

        Uses either short names like 'c' for crucible, or full names like 'gambit'.

        Multiple roles can be removed at once, e.g. `$lfg-remove c g` removes @crucible and @gambit.
        """

        await update_roles(ctx, roles_dicts['game_modes'], 'removed Game Mode', action='remove', *roles)

    @commands.command(name='sherpa-on')
    @commands.has_role('raid-lead')
    @commands.guild_only()
    async def sherpa_on(self, ctx):
        """Sets Sherpa status to Active.

        Can only be used by Raid Leads.
        """

        await update_roles(ctx, roles_dicts['raid_leads'], 'set Sherpa to Active', 'add', 'sherpa-active')

    @commands.command(name='sherpa-off')
    @commands.has_role('raid-lead')
    @commands.guild_only()
    async def sherpa_off(self, ctx):
        """Sets Sherpa status to Inactive.

        Can only be used by Raid Leads.
        """

        await update_roles(ctx, roles_dicts['raid_leads'], 'set Sherpa to Inactive', 'remove', 'sherpa-inactive')


def setup(bot):
    bot.add_cog(AutoRole(bot))
