# import re
import asyncio
import logging
from typing import Any, List, Dict, Tuple, Sequence, Iterable, Collection
from collections import OrderedDict

import discord
from discord.ext import commands

from modules.custom_embed import default_embed, format_list
from modules.styles import STYLES
from cogs.config.roles import ROLES
from modules.misc import chunk_list

from voluspa import CONFIG

from titlecase import titlecase

logger = logging.getLogger('voluspa.cog.autorole')


# TODO: Configurable matching rules?
def process_role_inputs(role_inputs, role_dict, allow_all=False):
    roles_to_update = set()
    for ri in role_inputs:
        for role, allowed_names in role_dict.items():
            for name in allowed_names:
                if ((allow_all and ri.lower() == 'all') or
                        ri.lower() == name.lower() or
                        ri.replace(' ', '') == name.lower()):
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


class Autorole(commands.Cog):
    """Automatic Role Management System (ARMS)"""
    # OR Discord Role Management heh DRM...
    # TODO: Improve this structure, use cog's and command structure/features better
    # TODO: Break it down into a simple set of funcs/rules
    def __init__(self, bot):
        self.bot = bot
        self.roles_dicts = ROLES

    async def update_roles(self,
                           ctx,
                           role_class: str,
                           roles: Sequence[str],
                           user_id: int = None,
                           options: Dict = None,
                           allow_all=False,
                           use_role_label=False):
        # TODO: Make it so that if the roles list is not supplied, the entire roles_dict is used?
        async with ctx.typing():
            # Set options and values
            if not options:
                options = {}
            action = options.get('action', 'add')
            if action not in ['add', 'remove']:
                return
            update_message = options.get('update_message', 'set')
            if action and update_message == 'add':
                update_message = 'added'
            elif action and update_message == 'remove':
                update_message = 'removed'
            confirm = options.get('confirm', True)
            role_dict = self.roles_dicts[role_class]

            if len(role_dict) <= 0:
                logger.info('Invalid role class!')
                return

            # Process input and sanitize
            logger.info(f'update_roles - roles_input: {roles}')
            roles_to_update = process_role_inputs(roles, role_dict, allow_all=allow_all)

            print(f'Roles to Update: {roles_to_update}')
            print(f'Role Dict: {role_dict}')

            if not list(roles_to_update):
                return

            # Build list of roles to add
            updated_roles = [discord.utils.get(ctx.guild.roles, name=role) for role in roles_to_update]

            # elif:  # if 'DJ' in [role.name for role in ctx.message.author.roles]:
            # pass

            role_results = roles_to_update
            if use_role_label:
                role_results = [f'{role:<12} {titlecase(role_dict[role][0])}' for role in roles_to_update]

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
                confirm_embed = default_embed(
                    title='Role Update',
                    description=f'\n{update_message.capitalize()} role(s):{format_list(role_results)}',
                    color=STYLES.colors.success
                )
                await ctx.send(f'{ctx.message.author.mention}', embed=confirm_embed)

            # TODO: Better guarantee of succees...
            return True

    async def assign_roles_to_user(self,
                                   ctx,
                                   role_class: str,
                                   roles: Sequence[str],
                                   users: Collection[str],
                                   # role_limit: str = None,
                                   role_limits: Sequence[str] = None,
                                   action: str = 'add',
                                   success_callbacks: Sequence[Any] = None):
        # Args are multiple user names (potentially _n_)
        # Search member list for each user name provided
        #  - if more then one user name matches, return a list of matches and ask for a retry
        #  - if only one match, sets friend role for discord user

        # <Member id=962762036347236771 name='Zed' discriminator='6791' bot=False nick=None
        # guild=<Guild id=374330517165965313 name='Ghost Proxy' chunked=True>>,

        # RegEx Filter: r'^\S+#\d+$' # TODO...
        # TODO: Check if member is set, and then remove, but prompt?
        # TODO: Add verification of role before message

        # TODO: Ugh... this is a mess and should be redone from scratch...
        if action not in ['add', 'remove']:
            return

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
                multiple_users_warn_embed = default_embed(
                    title='Multiple Users Found!',
                    description=f'\n:warning: Found multiple Users, need more info:{format_list(temp_list)}',
                    color=STYLES.colors.warning
                )
                await ctx.send(f'{ctx.message.author.mention}', embed=multiple_users_warn_embed)
            elif len(user_matches) == 1:
                # TODO: Do role limit check here... for now!
                # TODO: Support multiple role limits -- list: [role, role]
                # TODO: THIS IS WAY TOO BIG! -- BREAK IT UP!!
                ok_to_update_roles = True
                if role_limits:
                    conflicting_roles = [role for role in role_limits if role in user_matches[0]['roles']]
                    if conflicting_roles:
                        conflict_roles_embed = default_embed(
                            title='Role Update Error',
                            description=f'\n:no_entry: Sorry, could not immediately change Roles for:\n\n'
                            f'`{user_matches[0]["name"]}#{user_matches[0]["salt"]} ({user_matches[0]["nick"]})`'
                            f'\n\nUser has the following conflicting Role(s):{format_list(conflicting_roles)}',
                            color=STYLES.colors.danger
                        )
                        await ctx.send(f'{ctx.message.author.mention}', embed=conflict_roles_embed)

                        conflict_embed = default_embed(
                            title='Role Conflict',
                            description='\nWould you like to remove the conflicting role(s)'
                            ' and continue with role updates?\n\n'
                            '  To remove the role and continue select :white_check_mark:\n'
                            '  To cancel the role change command select :no_entry:',
                            color=STYLES.colors.warning
                        )
                        role_conflict_msg = await ctx.send(embed=conflict_embed)
                        # TODO: Ask for a reset of conflicting role here :check
                        ok_to_update_roles = await self.handle_role_conflict(ctx, role_conflict_msg)

                        if ok_to_update_roles:
                            # Remove conflicting roles
                            roles_removed = []
                            for conf_role in conflicting_roles:
                                rm_role = await self.update_roles(
                                    ctx,
                                    role_class,
                                    [conf_role],  # Could technically pass in the list of roles...
                                    user_id=user_matches[0]['id'],
                                    options={
                                        'confirm': False,
                                        'action': 'remove'
                                    }
                                )
                                if rm_role:
                                    roles_removed.append(conf_role)

                            ok_to_update_roles = set(conflicting_roles) == set(roles_removed)
                            if not ok_to_update_roles:
                                logger.info('Error during conflict role updating!')
                                await ctx.send(':no_entry: ERROR: Problem updating conflicting roles!')

                if ok_to_update_roles:

                    if action == 'add':
                        action_message = f'**+** adding Role(s):'
                    elif action == 'remove':
                        action_message = f'**-** removing Role(s):'
                    else:  # TODO: Pretty sure this should not be possible... ?
                        action_message = f'setting Role(s):'

                    role_embed = default_embed(
                        title=':white_check_mark: Setting User Roles',
                        description=f'`\n{user_matches[0]["name"]}#{user_matches[0]["salt"]} '
                        f'({user_matches[0]["nick"]})`\n\n'
                        f'{action_message}'
                        f'{format_list(roles)}',
                        color=STYLES.colors.success
                    )

                    # await self.update_roles(ctx, 'ghost_proxy_roles', ['gpf'])  # TODO: Abstract this to params...
                    await self.update_roles(
                        ctx,
                        role_class,
                        roles,
                        user_id=user_matches[0]['id'],
                        options={
                            'confirm': False,
                            'action': action
                        }
                    )

                    # Send message after doing the above
                    # TODO: Ensure guarantee of removal before sending below...?
                    await ctx.send(f'{ctx.message.author.mention}', embed=role_embed)

                    if success_callbacks:
                        for cb in success_callbacks:
                            try:
                                await cb(user_matches[0])
                            except Exception as e:
                                logger.info(f'Success Callback Exception: {e}')
            else:
                error_embed = default_embed(
                    title='No Matching User',
                    description=f'\n:no_entry: Sorry, could not find a matching User for:\n\n'
                    f'\n`{req_user}`'
                    f'\n\nPlease try again.',
                    color=STYLES.colors.danger
                )
                await ctx.send(f'{ctx.message.author.mention}', embed=error_embed)

        if multiple_users_found:
            multiple_users_embed = default_embed(
                title='Multiple Users Found',
                description=f'\n**NOTE:** _Multiple User results were found for 1 or more requested Users._\n\n'
                f'Please review the results above and then try again with a full Username.\n\n'
                f'_Example:_  `<user>#<id>`  ->  `$p2f guardian#1234`',
                color=STYLES.colors.info
            )
            await ctx.send(embed=multiple_users_embed)

    async def handle_role_conflict(self, ctx, confirm_msg):  # TODO: Make static
        """Returns a bool for confirmation"""
        #reaction_emoji = {'yes': ':white_check_mark:', 'no': ':no_entry:'}
        react_unicode = {'yes': '\u2705', 'no': '\u26D4'}
        for emoji in react_unicode.values():
            await confirm_msg.add_reaction(emoji)

        def check(reaction: discord.Reaction, user: discord.User) -> bool:
            return user == ctx.message.author and reaction.message.id == confirm_msg.id

        try:
            reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=60)
        except asyncio.TimeoutError:
            await ctx.send(f'Request timed out... :(')
            return False
        else:
            print(f'reaction_emoji: {reaction} | {reaction.emoji}')
            # await ctx.send(f'Received reaction: {reaction.emoji} from user: {user}')
            if reaction.emoji == react_unicode['yes']:
                return True
            elif reaction.emoji == react_unicode['no']:
                return False
            else:
                print('Something really horrible has happened, not sure what, but good luck...')

    @commands.command(name='lfg-add')  # , aliases=['game-role', 'lfg-role'])
    @commands.guild_only()
    async def lfg_add(self, ctx, *roles: str):
        """Adds Game Mode roles for @ pings

        Uses either short names like 'c' for crucible, or full names like 'gambit'.

        Multiple roles can be added at once, e.g. `$lfg-add c g` adds @crucible and @gambit.
        """
        # $lfg (no param) -- Lists current LFG roles set
        logger.info(f'roles input: {roles}')
        await self.update_roles(
            ctx,
            'game_modes',
            roles,
            options={'update_message': 'added Game Mode'},
            allow_all=True
        )

    @commands.command(name='lfg-remove')  # , aliases=['game-role', 'lfg-role'])
    @commands.guild_only()
    async def lfg_remove(self, ctx, *roles: str):
        """Removes Game Mode roles for @ pings

        Uses either short names like 'c' for crucible, or full names like 'gambit'.

        Multiple roles can be removed at once, e.g. `$lfg-remove c g` removes @crucible and @gambit.
        """
        await self.update_roles(
            ctx,
            'game_modes',
            roles,
            options={
                'update_message': 'removed Game Mode',
                'action': 'remove'
            },
            allow_all=True
        )

    @commands.command(name='og-list', aliases=['other-game-list'])
    @commands.guild_only()
    async def other_game_list(self, ctx):
        """Lists available Other-Game channels"""
        og_list = ''
        if self.roles_dicts['other_games']:
            og_list += 'ROLE    GAME\n-------------------------\n'
            for og_role, og_names in self.roles_dicts['other_games'].items():
                og_list += f'{og_role.replace("og-", "") + "":<8}{og_names[0].title()}\n'

        og_list_embed = default_embed(
            title='Other Games List',
            description=f'Current available roles and channels for Other Games:\n'
            f'```\n{og_list}\n```'
        )

        await ctx.send(embed=og_list_embed)

    @commands.command(name='og-add', aliases=['other-game-add'])
    @commands.guild_only()
    async def other_game_add(self, ctx, *games: str):
        """Adds Other-Game roles

        Uses either short names like 'div2' or full names like 'Division2'.

        Note: No spaces or surround names with spaces in quotes!
        Example: $og-add "Monster Hunter World"  -->  adds @og-mhw

        Multiple other games can be added at once.
        Example: `$og-add div2 mhw`  -->  adds @gp-div2 and @gp-mhw

        All other games can be added by using `$og-add all`.
        """
        # $lfg (no param) -- Lists current LFG roles set
        logger.info(f'game input: {games}')
        await self.update_roles(
            ctx,
            'other_games',
            games,
            options={'update_message': 'added Other Game(s)'},
            allow_all=True,
            use_role_label=True
        )

    @commands.command(name='og-remove', aliases=['other-game-remove'])
    @commands.guild_only()
    async def other_game_remove(self, ctx, *games: str):
        """Removes Other-Game roles

        Uses either short names like 'div2' or full names like 'Division2'.

        Note: No spaces or surround names with spaces in quotes!
        Example: $og-remove "Monster Hunter World"  -->  removes @og-mhw

        Multiple other-games can be removed at once.
        Example: `$og-remove div2 mhw`  -->  removes @gp-div2 and @gp-mhw

        All other-games can be remove by using `$og-add all`.
        """
        logger.info(f'game input: {games}')
        await self.update_roles(
            ctx,
            'other_games',
            games,
            options={
                'update_message': 'removed Other Game(s)',
                'action': 'remove'
            },
            allow_all=True,
            use_role_label=True
        )

    @commands.command(name='nsfw')
    @commands.has_any_role('ghost-proxy-member', 'ghost-proxy-friend')
    @commands.guild_only()
    async def nsfw_toggle(self, ctx):
        """Toggles the NSFW role

        Can only be used by Ghost Proxy Members or Friends.
        """
        sherpa_role = discord.utils.get(ctx.message.guild.roles, name='nsfw')
        if sherpa_role not in ctx.message.author.roles:
            await self.update_roles(ctx, 'nsfw', ['nsfw'])
        else:
            await self.update_roles(
                ctx,
                'nsfw',
                ['nsfw'],
                options={
                    'update_message': 'removed',
                    'action': 'remove',
                })

    @commands.command(name='current-events', aliases=['ce'])
    @commands.has_any_role('ghost-proxy-member', 'ghost-proxy-friend')
    @commands.guild_only()
    async def current_events_toggle(self, ctx):
        """Toggles the current-events role

        Can only be used by Ghost Proxy Members or Friends.
        """
        ce_role = discord.utils.get(ctx.message.guild.roles, name='current-events')
        if ce_role not in ctx.message.author.roles:
            await self.update_roles(ctx, 'topics', ['current-events'])
        else:
            await self.update_roles(
                ctx,
                'topics',
                ['current-events'],
                options={
                    'update_message': 'removed',
                    'action': 'remove',
                })

    @commands.command(name='sherpa', aliases=['s'])
    @commands.has_role('ghost-proxy-member')
    @commands.guild_only()
    async def sherpa_toggle(self, ctx):
        """Toggles the Sherpa role

        Can only be used by Ghost Proxy Members.
        """
        sherpa_role = discord.utils.get(ctx.message.guild.roles, name='sherpa')
        if sherpa_role not in ctx.message.author.roles:
            await self.update_roles(ctx, 'raid_leads', ['sherpa'])
        else:
            await self.update_roles(
                ctx,
                'raid_leads',
                ['sherpa'],
                options={
                    'update_message': 'removed',
                    'action': 'remove',
                })

    @commands.command(name='dj')
    @commands.has_any_role('ghost-proxy-member', 'ghost-proxy-envoy')
    @commands.guild_only()
    async def set_dj(self, ctx):
        """Adds DJ role for Rythm

        Can only be used by Members.
        """
        # TODO: Improve this, possibly toggle?

        if 'DJ' in [role.name for role in ctx.message.author.roles]:
            await ctx.send(f'{ctx.message.author.mention} - DJ role is already set :+1:')
        else:
            await self.update_roles(ctx, 'rythm_dj', ['dj'])

    @commands.command(name='onboard')
    @commands.has_role('ghost-proxy-vanguard')
    @commands.guild_only()
    async def onboard_member(self, ctx, *users: str):
        """Onboards User(s) to Members(s)

        Currently implies _not_ a ghost-proxy-envoy (WIP)

        Performs an ARM, then sends a DM to the user, and sends a Welcome to Private.

        Can only be used by Vanguard (atm).
        """

        welcome_message = """Welcome to Ghost Proxy! <:ghost_proxy_2:455130686290919427>

If you haven't yet, please read through our `#rules-conduct` and `#server-info` and then feel free to explore the server! A good place to start is `#voluspa`, our very own Warmind where you can set game roles, check who's online, and use a number of other helpful commands (type `$help`).

If you have any questions about anything, feel free to ask in general chat, use the `$feedback` Voluspa feature (here in a DM even), or use the `@ghost-proxy-vanguard` ping to ask for help from the Ghost Proxy admin team.

\\*\\*\\*

And finally, a couple of steps to do now that you are a member:

1. Head to the `#charlemagne` channel and type `!register` -- you will receive a DM from Char, please follow the instructions :+1:

2. Join our Steam Group <https://steamcommunity.com/groups/ghostproxy> 

3. Head to the `#voluspa` channel and type `$help lfg-add` and then add your Game Mode roles

4. Join our Social Tower voice channel and start forming fireteams and have fun!

Thanks and eyes up, Guardian! <:cayde_thumbs_up:451649810894946314>
_ _
        """

        async def send_welcome_direct_message(user_rec):
            new_member = self.bot.get_user(user_rec['id'])
            welcome_prefix = f"_ _\n_ _\n" \
                             f"Hello, {new_member.mention}! :wave: "
            await new_member.send(f"{welcome_prefix}{welcome_message}")

        async def send_welcome_guild_message(user_rec):
            new_member = self.bot.get_user(user_rec['id'])
            guild_welcome = f"_Greetings to our new member, {new_member.mention}! :tada: Welcome to Ghost Proxy!_ <:ghost_proxy_2:455130686290919427>"
            guild_channel = ctx.bot.get_channel(CONFIG.Voluspa.private_guild_channel_id)
            await guild_channel.send(guild_welcome)

        await self.assign_roles_to_user(
            ctx,
            'ghost_proxy_roles',
            [
                'ghost-proxy-member'
            ],
            users,
            role_limits=[
                'ghost-proxy-friend',
                'ghost-proxy-legacy',
                'ghost-proxy-envoy',
            ],
            success_callbacks=[
                send_welcome_direct_message,
                send_welcome_guild_message
            ]
        )

    @commands.command(name='set-member', aliases=['p2m', 'arm'])
    @commands.has_role('ghost-proxy-vanguard')
    @commands.guild_only()
    async def promote_to_member(self, ctx, *users: str):
        """Sets User(s) to Members(s)

        Currently implies _not_ a ghost-proxy-envoy (WIP)

        Can only be used by Vanguard (atm).
        """
        await self.assign_roles_to_user(
            ctx,
            'ghost_proxy_roles',
            [
                'ghost-proxy-member'
            ],
            users,
            role_limits=[
                'ghost-proxy-friend',
                'ghost-proxy-legacy',
                'ghost-proxy-envoy',
            ]
        )

    @commands.command(name='set-friend', aliases=['p2f', 'arf'])
    @commands.has_role('ghost-proxy-vanguard')
    @commands.guild_only()
    async def promote_to_friend(self, ctx, *users: str):
        """Sets User(s) to Friend(s)

        Can only be used by Vanguard (atm).
        """
        await self.assign_roles_to_user(
            ctx,
            'ghost_proxy_roles',
            [
                'ghost-proxy-friend'
            ],
            users,
            role_limits=[
                'ghost-proxy-member',
                'ghost-proxy-legacy',
                'ghost-proxy-envoy'
            ]
        )

    @commands.command(name='set-envoy', aliases=['p2e', 'are'])
    @commands.has_any_role('ghost-proxy-vanguard', 'div2-admin')
    @commands.guild_only()
    async def set_to_envoy(self, ctx, *users: str):
        """Sets User(s) to Envoy(s)

        Currently implies _not_ having ghost-proxy-member (WIP)

        Can only be used by Vanguard and Div2 Admins (atm).
        """
        await self.assign_roles_to_user(
            ctx,
            'ghost_proxy_roles',
            [
                'ghost-proxy-envoy',
                'ghost-proxy-friend',
            ],
            users,
            role_limits=['ghost-proxy-member']
        )
        await self.assign_roles_to_user(
            ctx,
            'other_games',
            ['og-div2'],
            users
        )

    # TODO: Hack job
    @commands.command(name='remove-envoy')
    @commands.has_any_role('ghost-proxy-vanguard', 'div2-admin')
    @commands.guild_only()
    async def remove_envoy(self, ctx, *users: str):
        """Removes Envoy(s) from User(s)

        Can only be used by Vanguard and Div2 Admins (atm).
        """
        await self.assign_roles_to_user(
            ctx,
            'ghost_proxy_roles',
            [
                'ghost-proxy-envoy',
            ],
            users,
            action='remove'
        )

    @commands.command(name='set-legacy', aliases=['p2l', 'arl'])
    @commands.has_role('ghost-proxy-vanguard')
    @commands.guild_only()
    async def set_to_legacy(self, ctx, *users: str):
        """Sets User(s) to Legacy Friend(s)

        Removes gp-member and gp-veteran.

        Can only be used by Vanguard (atm).
        """
        await self.assign_roles_to_user(
            ctx,
            'ghost_proxy_roles',
            [
                'ghost-proxy-friend',
                'ghost-proxy-legacy',
            ],
            users,
            role_limits=[
                'ghost-proxy-member',
                'ghost-proxy-veteran',
                'raid-lead',
                'crucible-lead',
                'gambit-lead',
                'strike-nf-pve-lead'
            ]
        )

    # TODO: RESET MEMBER
    # TODO: ADD EXCEPTION/BLOCK LIST (anyone below Gatekeeper)
    @commands.command(name='remove-roles', aliases=['autorole-reset', 'ar-reset', 'reset-roles', 'roles-reset', 'ARR'])
    @commands.has_role('ghost-proxy-gatekeeper')
    @commands.guild_only()
    async def reset_user(self, ctx, *users: str):
        """Removes all GP roles from a user

        Removes friend, legacy, member, veteran, envoy

        Can only be used by Gatekeeper (atm).
        """
        await self.assign_roles_to_user(
            ctx,
            'ghost_proxy_roles',
            list(self.roles_dicts['ghost_proxy_roles'].keys()),
            users,
            action='remove'
        )

    # TODO: RESETS ALL ROLES -- DANGER!!!
    @commands.command(name='remove-all-roles', aliases=['NFO', 'AR-RAR'])
    @commands.has_role('founder')
    async def remove_all_roles(self, ctx, *users: str):
        """Removes ALL roles from a user!

        Removes friend, legacy, member, veteran, envoy

        Can only be used by Founder (atm).
        """
        await self.assign_roles_to_user(
            ctx,
            'ghost_proxy_roles',
            list(self.roles_dicts['ghost_proxy_roles'].keys()),
            users,
            action='remove'
        )
        await self.assign_roles_to_user(
            ctx,
            'ghost_proxy_elevated_roles',
            list(self.roles_dicts['ghost_proxy_elevated_roles'].keys()),
            users,
            action='remove'
        )
        await self.assign_roles_to_user(
            ctx,
            'ghost_proxy_protected_roles',
            ['ghost-proxy-gatekeeper'],
            users,
            action='remove'
        )
        await self.assign_roles_to_user(
            ctx,
            'game_modes',
            list(self.roles_dicts['game_modes'].keys()),
            users,
            action='remove'
        )
        await self.assign_roles_to_user(
            ctx,
            'other_games',
            list(self.roles_dicts['other_games'].keys()),
            users,
            action='remove'
        )

    @commands.command(name='list-non-roles', aliases=['lnr', 'arn'])
    @commands.has_role('ghost-proxy-vanguard')
    @commands.guild_only()
    async def list_non_role_users(self, ctx):
        """Lists all non-role Discord users

        Outputs a reference list for use with other Autorole commands.

        Can only be used by Vanguard (atm).
        """
        async with ctx.typing():
            non_role_members = [member for member in self.bot.get_all_members() if len(member.roles) == 1]
            num_non_roles = len(non_role_members)
            formatted_non_roles = [f'{nrm.name.casefold()}#{nrm.discriminator}' for nrm in non_role_members]

            embed = default_embed(
                title='Current Non-Role Discord Users',
                description='Reference list for use with other Autorole commands'
            )
            embed.add_field(
                name='Number of Non-Roles',
                value=num_non_roles,
                inline=False
            )
            embed.add_field(
                name='Current Non-Roles',
                value=f'{format_list(formatted_non_roles)}',
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name='list-role-stats', aliases=['lrs', 'rs', 'role-stats'])
    @commands.has_role('ghost-proxy-vanguard')
    @commands.guild_only()
    async def role_stats(self, ctx):
        """Lists Discord role stats

        Provides a list of all Discord members without any Ghost Proxy roles

        Can only be used by vanguard (atm).
        """
        async with ctx.typing():
            num_roles = len(ctx.guild.roles) - 1  # account for `@everyone`
            # Non-ordered Dict...
            # role_stats = {f'{role.name}': len(role.members) for role in ctx.guild.roles}
            role_stats = OrderedDict()
            for role in ctx.guild.roles:
                role_stats[role.name] = len(role.members)
            formatted_role_stats = [f'{r_mems:<8}{r_name}' for r_name, r_mems in reversed(role_stats.items())]

            split_formatted_stats = format_list(formatted_role_stats, surround='').split('\n')
            pages = chunk_list(split_formatted_stats, 1024 - (len(split_formatted_stats) * 2) - 100)
            for page_num, page in enumerate(pages, start=1):
                page = "\n".join(page)
                embed = default_embed(
                    title='Role Stats',
                    description='List of Roles and number of associated Users',
                    footer_notes=f'Page {page_num} of {len(pages)}'
                )
                embed.add_field(
                    name='Number of Roles',
                    value=num_roles,
                    inline=False
                )
                embed.add_field(
                    name='Roles and number of Users',
                    value=f'```{page}```',
                    inline=False
                )
                await ctx.send(embed=embed)

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
    bot.add_cog(Autorole(bot))
