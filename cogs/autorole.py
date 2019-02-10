import re
import logging
from typing import List, Dict, Tuple

import discord
from discord.ext import commands

logger = logging.getLogger('voluspa.cog.autorole')


def process_role_inputs(roles, role_dict):
    roles_to_update = set()
    for r in roles:
        for role, allowed_names in role_dict.items():
            for name in allowed_names:
                if r == name:
                    roles_to_update.add(role)
                    break
    return roles_to_update


def match_users(user_list, username):
    print(f'USERNAME REC: {username}')
    matched_users = [user for user in user_list if username[0] in user['name'] or username[0] in user['nick']]
    print(f'>>> Match results before salt: {matched_users}')
    if len(username) >= 2:
        matched_users = [user for user in matched_users if user['salt'] == username[1]]
    print(f'>>> Match results AFTER salt: {matched_users}')
    return matched_users


class AutoRole:
    def __init__(self, bot):
        self.bot = bot
        self.roles_dicts = {
            'game_modes': {
                'crucible': ['c', 'crucible'],
                'gambit': ['g', 'gambit'],
                'raid': ['r', 'raid'],
                'strike-nf-pve': ['s', 'nf', 'pve', 'strike', 'nightfall', 'strike-nf-pve']
            },
            'raid_leads': {
                'sherpa-active': ['on', 'active', 'true', 'enable', 'yes', '1'],
                'sherpa-inactive': ['off', 'inactive', 'false', 'disable', 'no', '0']
            },
            'rythm_dj': {
                'DJ': ['dj', 'rythm', 'rhythm']
            },
            'ghost_proxy_roles': {
                'ghost-proxy-friend': ['gpf', 'gp-friend', 'ghost-proxy-friend'],
                'ghost-proxy-member': ['gpm', 'gp-member', 'ghost-proxy-member']
            }
        }

    async def update_roles(self,
                           ctx,
                           role_class: str,
                           roles: List[str],
                           user_id: int = None,
                           options: Dict = None):
        # Set options and values
        if not options:
            options = {}
        update_message = options.get('update_message', 'added')
        action = options.get('action', 'add')
        confirm = options.get('confirm', True)
        role_dict = self.roles_dicts[role_class]

        if len(role_dict) <= 0:
            logger.info('Invalid role class!')
            return

        # Process input and sanitize
        roles_to_update = process_role_inputs(roles, role_dict)

        print(f'Roles to Update: {roles_to_update}')
        print(f'Role Dict: {role_dict}')

        if not list(roles_to_update):
            return

        # Build list of roles to add
        updated_roles = [discord.utils.get(ctx.guild.roles, name=role) for role in roles_to_update]

        # elif:  # if 'DJ' in [role.name for role in ctx.message.author.roles]:
        # pass

        # TODO: Add check if roles are already applied and avoid doing it again?

        print(f'"Updating Roles (action: {action}): {updated_roles}')
        if user_id:
            user = ctx.guild.get_member(user_id)
        else:
            user = ctx.message.author

        if action == 'add':
            await user.add_roles(*updated_roles)
        elif action == 'remove':
            await user.remove_roles(*updated_roles)
        else:
            print(f"Unknown Action for Update Roles!")
            return

        if confirm:
            await ctx.send(f'{ctx.message.author.mention} {update_message} role(s):  `{", ".join(roles_to_update)}`')

    async def assign_roles_to_user(self,
                                   ctx,
                                   role_class: str,
                                   roles: List[str],
                                   users: Tuple[str],
                                   role_limit: str = None):
        # Args are multiple user names (potentially _n_)
        # Search member list for each user name provided
        #  - if more then one user name matches, return a list of matches and ask for a retry
        #  - if only one match, sets friend role for discord user

        # <Member id=962762036347236771 name='Zed' discriminator='6791' bot=False nick=None
        # guild=<Guild id=374330517165965313 name='Ghost Proxy' chunked=True>>,

        # RegEx Filter: r'^\S+#\d+$' # TODO...
        # TODO: Check if member is set, and then remove, but prompt?
        # TODO: Add verification of role before message

        # TODO: Add error handling for params...
        if len(users) <= 0:
            await ctx.send(f'{ctx.message.author.mention} - Please provide User(s) to promote.')

        logger.info(f'Raw Args: {users}')
        requested_users = [user.casefold().split('#') for user in users]

        logger.info(f'User Args: {requested_users}')
        discord_members = self.bot.get_all_members()
        # TODO: Would be nice to cache this, expire based on timeframes
        #  ...would be cool to tie cache invalidation to event callbacks...
        #  e.g. discord member join event clears discord member cache, hmm...

        # `targetrole = discord.utils.get(myserver.roles, name="MyTargetRole")`

        member_list = [
            {
                'id': member.id,
                'name': member.name.casefold(),
                'salt': member.discriminator,
                'nick': member.nick.casefold() if member.nick else '',
                'roles': [role.name for role in member.roles],  # member.roles,
                'top_role': member.top_role.name  # member.top_role
            }
            for member in discord_members if not member.bot
        ]
        logger.info(f'Discord Members:\n{member_list}')

        user_results = [{req_user[0]: match_users(member_list, req_user)} for req_user in requested_users]
        logger.info(f'Member Search Results:\n{user_results}\n')

        multiple_users_found = False
        for user_rec in user_results:
            print(f'USER REC: {user_rec} | type: {type(user_rec)}')
            req_user = list(user_rec.keys())[0]
            user_matches = user_rec[req_user]
            if len(user_matches) > 1:
                multiple_users_found = True
                temp_list = [f'{user["name"]}#{user["salt"]} ({user["nick"]})' for user in user_matches]
                nl = "\n"
                await ctx.send(
                    f'{ctx.message.author.mention} - '
                    f':warning: Found multiple Users, need more info:```{nl.join(temp_list)}```'
                )
            elif len(user_matches) == 1:
                # TODO: Do role limit check here... for now!
                if role_limit and role_limit in user_matches[0]['roles']:
                    # NOT ALLOWED
                    await ctx.send(
                        f'{ctx.message.author.mention} - '
                        f':no_entry: Sorry, could not change Roles for:\n'
                        f'`{user_matches[0]["name"]}#{user_matches[0]["salt"]} ({user_matches[0]["nick"]})`'
                        f'\n\nUser has the following conflicting Role(s): `{role_limit}`'
                    )
                else:
                    await ctx.send(
                        f'{ctx.message.author.mention} - '
                        f':white_check_mark: Promoting User to Friend:\n'
                        f'`{user_matches[0]["name"]}#{user_matches[0]["salt"]} ({user_matches[0]["nick"]})`'
                    )
                    # await self.update_roles(ctx, 'ghost_proxy_roles', ['gpf'])  # TODO: Abstract this to params...
                    await self.update_roles(
                        ctx,
                        role_class,
                        roles,
                        user_id=user_matches[0]['id'],
                        options={'confirm': False}
                    )
            else:
                await ctx.send(
                    f'{ctx.message.author.mention} - '
                    f':no_entry: Sorry, could not find a matching User for:'
                    f'\n`{req_user}`'
                    f'\n\nPlease try again.'
                )

        if multiple_users_found:
            await ctx.send(
                f'_ _\n**NOTE:** _Multiple User results were found for 1 or more requested Users._\n'
                f'Please review the results above and then try again with a full Username.\n\n'
                f'_Example:_  `<user>#<id>`  ->  `$p2f guardian#1234`'
            )

    # TODO: Improve this structure, use cog's and command structure/features better

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

        await self.update_roles(
            ctx,
            'game_modes',
            *roles,
            options={'update_message': 'added Game Mode'}
        )

    @commands.command(name='lfg-remove')  # , aliases=['game-role', 'lfg-role'])
    @commands.guild_only()
    async def lfg_remove(self, ctx, *roles: str):
        """Removes Game Mode roles for @ pings.

        Uses either short names like 'c' for crucible, or full names like 'gambit'.

        Multiple roles can be removed at once, e.g. `$lfg-remove c g` removes @crucible and @gambit.
        """

        await self.update_roles(
            ctx,
            'game_modes',
            *roles,
            options={
                'update_message': 'removed Game Mode',
                'action': 'remove'
            }
        )

    @commands.command(name='sherpa-on')
    @commands.has_role('raid-lead')
    @commands.guild_only()
    async def sherpa_on(self, ctx):
        """Sets Sherpa status to Active.

        Can only be used by Raid Leads.
        """

        await self.update_roles(ctx, 'raid_leads', ['active'])
        await self.update_roles(
            ctx,
            'raid_leads',
            ['inactive'],
            options={
                'update_message': 'removed',
                'action': 'remove',
                'confirm': False
            })

    @commands.command(name='sherpa-off')
    @commands.has_role('raid-lead')
    @commands.guild_only()
    async def sherpa_off(self, ctx):
        """Sets Sherpa status to Inactive.

        Can only be used by Raid Leads.
        """

        await self.update_roles(ctx, 'raid_leads', ['inactive'])
        await self.update_roles(
            ctx,
            'raid_leads',
            ['active'],
            options={
                'update_message': 'removed',
                'action': 'remove',
                'confirm': False
            }
        )

    @commands.command(name='dj')
    @commands.has_role('ghost-proxy-member')
    @commands.guild_only()
    async def set_dj(self, ctx):
        """Sets DJ role for Rythm

        Can only be used by Members.
        """
        # TODO: Improve this, possibly toggle?

        if 'DJ' in [role.name for role in ctx.message.author.roles]:
            await ctx.send(f'{ctx.message.author.mention} - DJ role is already set :+1:')
        else:
            await self.update_roles(ctx, 'rythm_dj', ['dj'])

    # TODO: STUB
    @commands.command(name='set-member', aliases=['p2m'])
    @commands.has_role('ghost-proxy-vanguard')
    @commands.guild_only()
    async def promote_to_member(self, ctx, *users: str):
        """WIP: Promotes User(s) to Members(s)

        Can only be used by Vanguard (atm).
        """
        await self.assign_roles_to_user(ctx, 'ghost_proxy_roles', ['gpm'], users, role_limit='ghost-proxy-member')

    @commands.command(name='set-friend', aliases=['p2f'])
    @commands.has_role('ghost-proxy-vanguard')
    @commands.guild_only()
    async def promote_to_friend(self, ctx, *users: str):
        """WIP: Promotes User(s) to Friend(s)

        Can only be used by Vanguard (atm).
        """
        await self.assign_roles_to_user(ctx, 'ghost_proxy_roles', ['gpf'], users, role_limit='ghost-proxy-friend')

    # async def get_members_by_roles(self, roles: List[str], include_bots=False):
    #     # TODO: WIP
    #     discord_members = self.bot.get_all_members()
    #     member_list = [
    #         {
    #             'id': member.id,
    #             'name': member.name,
    #             'salt': member.discriminator,
    #             'nick': member.nick if member.nick else '',
    #             'bot': member.bot
    #         }
    #         for member in discord_members if member.roles
    #     ]
    #     return member_list


def setup(bot):
    bot.add_cog(AutoRole(bot))
