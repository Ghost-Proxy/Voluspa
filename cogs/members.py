# pylint: disable=too-many-locals
"""Members Cog"""

import itertools
import logging
import math
import statistics

import discord
from discord.ext import commands
# https://github.com/seatgeek/fuzzywuzzy <- instead

from modules.config import CONFIG
from modules.discord_utils import send_multipart_msg
from modules.exceptions import VoluspaError
from modules.external_services.bungie import async_bungie_request_handler

from modules.custom_embed import default_embed, format_list

logger = logging.getLogger('voluspa.cog.members')


def filter_character_types(clan_characters, min_level=0):
    """Filter destiny character types"""
    hunters = []
    titans = []
    warlocks = []
    total_num_chars = 0
    for characters in clan_characters:
        for char in characters:
            total_num_chars += 1
            if min_level > 0 and char['light'] < min_level:
                continue
            # Destiny Class
            # Titan: 0
            # Hunter: 1
            # Warlock: 2
            if char['classType'] == 0:
                titans.append(char['light'])
            elif char['classType'] == 1:
                hunters.append(char['light'])
            elif char['classType'] == 2:
                warlocks.append(char['light'])
    return hunters, titans, warlocks, total_num_chars


async def filter_characters_from_members(destiny_members, platform_type=None):
    """Filter character types from members"""
    clan_characters = []
    for d_member in destiny_members:
        # destiny_member_id = await async_get_member_data_by_id(
        #     d_member['membershipId'],
        #     d_member['membershipType']
        # )
        membership_type = platform_type if platform_type else d_member['membershipType']
        clan_characters.append(await async_get_destiny_profile_characters(d_member['membershipId'], membership_type))
    return clan_characters


async def generate_char_stats_message(light_levels, total_chars, char_type):
    """Generate character stats message"""
    num_chars = len(light_levels)
    percent_total = round(((num_chars / total_chars) * 100), 2)
    max_ll = max(light_levels)
    min_ll = min(light_levels)
    mean_ll = math.ceil(statistics.mean(light_levels))
    median_ll = math.ceil(statistics.median(light_levels))
    stats_msg = f'Number of {char_type}: **{num_chars}**\n' \
                f'  - Percent of Chars: {percent_total}%\n' \
                f'  - Lowest LL: {min_ll}\n' \
                f'  - Mean / Median LL: {mean_ll} / {median_ll}\n' \
                f'  - Highest LL: {max_ll}'
    return stats_msg


async def async_get_destiny_profile_characters(destiny_membership_id, membership_type):
    """Get Destiny Profile characters"""
    # https://bungie-net.github.io/multi/operation_get_Destiny2-GetProfile.html#operation_get_Destiny2-GetProfile
    target_endpoint = f'/Destiny2/{membership_type}/Profile/{destiny_membership_id}/'
    profile_params = {'components': 'Profiles,Characters'}  # ?components=Profiles,Characters
    raw_json = await async_bungie_request_handler(target_endpoint, params=profile_params)
    logger.info('Successfully retrieved characters for %s', target_endpoint)
    if raw_json:
        bungie_response = raw_json['Response']
        characters_data = bungie_response['characters']['data']
        characters = []
        for char in characters_data.values():
            characters.append({'classType': char['classType'], 'light': char['light']})
        return characters
    raise VoluspaError('raw_json was empty!')


async def async_get_member_data_by_id(membership_id, membership_type, platform_type=4):  # platform_type 4 is PC
    """Get Member data by id"""
    # https://bungie-net.github.io/multi/operation_get_User-GetMembershipDataById.html#operation_get_User-GetMembershipDataById
    target_endpoint = f'/User/GetMembershipsById/{membership_id}/{membership_type}/'
    raw_json = await async_bungie_request_handler(target_endpoint)
    # logger.info('MEMBER DATA INFO:\n{}'.format(raw_json))\
    if raw_json:
        bungie_response = raw_json['Response']
        destiny_memberships = bungie_response['destinyMemberships']
        destiny_membership_info = [dm for dm in destiny_memberships if dm['membershipType'] == platform_type][0]
        # logger.info('> Returning: {}'.format(destiny_membership_info['membershipId']))
        return destiny_membership_info['membershipId']
    raise VoluspaError('raw_json was empty!')


async def async_get_clan_members():
    """Get a list of clan members"""
    target_endpoint = f'/GroupV2/{CONFIG.Bungie.clan_group_id}/Members/'
    raw_json = await async_bungie_request_handler(target_endpoint)
    if raw_json:
        bungie_results = raw_json['Response']
        member_list = bungie_results['results']
        num_members = bungie_results['totalResults']
        logger.info('BUNGIE MEMBER LIST:\n%s', len(member_list))
        return num_members, member_list
    raise VoluspaError('raw_json was empty!')


def get_destiny_member_info(member):
    """Get Destiny member info"""
    return {
        'membershipId': member['destinyUserInfo']['membershipId'],
        'membershipType': member['destinyUserInfo']['membershipType'],
        'displayName': member['destinyUserInfo']['displayName'],
        'LastSeenDisplayName': member['destinyUserInfo']['LastSeenDisplayName'],
        'LastSeenDisplayNameType': member['destinyUserInfo']['LastSeenDisplayNameType'],
        'crossSaveOverride': member['destinyUserInfo']['crossSaveOverride'],
        'supplementalDisplayName': member.get('bungieNetUserInfo', {}).get('supplementalDisplayName'),
        'bungieNetDisplayName': member.get('bungieNetUserInfo', {}).get('displayName'),
    }


async def async_get_bungie_clan_members():
    """Get Bungie Clan members"""
    target_endpoint = f'/GroupV2/{CONFIG.Bungie.clan_group_id}/Members/'
    response = await async_bungie_request_handler(target_endpoint)
    if response:
        logger.info('Bungie Response: %s', response)
        bungie_results = response['Response']
        logger.info('BUNGIE MEMBER LIST:\n%s', bungie_results)
        member_results = bungie_results['results']
        num_members = bungie_results['totalResults']
        member_list = [member['destinyUserInfo']['displayName'] for member in member_results]
        return num_members, member_list, member_results
    raise VoluspaError('response was empty!')


async def async_get_bungie_member_list():
    """Get a list of Bungie members"""
    target_endpoint = f'/GroupV2/{CONFIG.Bungie.clan_group_id}/Members/'
    raw_json = await async_bungie_request_handler(target_endpoint)
    if raw_json:
        bungie_results = raw_json['Response']
        logger.info('BUNGIE MEMBER LIST:\n%s', bungie_results)
        member_results = bungie_results['results']
        num_members = raw_json['Response']['totalResults']
        member_list = [member['destinyUserInfo']['displayName'] for member in member_results]
        return num_members, member_list, member_results
    raise VoluspaError('raw_json was empty!')


async def async_get_bungie_member_type_dict():
    """Get a Bungie member type dictionary"""
    target_endpoint = f'/GroupV2/{CONFIG.Bungie.clan_group_id}/Members/'
    raw_json = await async_bungie_request_handler(target_endpoint)
    if raw_json:
        bungie_results = raw_json['Response']
        logger.info('BUNGIE MEMBER LIST:\n%s', bungie_results)
        member_results = bungie_results['results']
        num_members = raw_json['Response']['totalResults']
        # member_list = [{'displayName': member['destinyUserInfo']['displayName'],
        # 'memberType': member['memberType']} for member in member_results]
        member_dict = {'members': [], 'admins': []}
        # Member type 1 is recruit?
        # Member type 2 is normal member
        # Member type 3 is admin
        # Member type 5 is founder
        for member in member_results:
            if member['memberType'] == 2:
                member_dict['members'].append(member['destinyUserInfo']['displayName'])
            elif member['memberType'] in {3, 5}:
                member_dict['admins'].append(member['destinyUserInfo']['displayName'])
        return num_members, member_dict
    raise VoluspaError('raw_json was empty!')


def filter_members_by_field(member_dict, field_name):
    """Filter members by desired field_name"""
    return {member_id: {
        'name': member_info['display_name'],
        field_name: member_info.get(field_name, None)
    } for member_id, member_info in member_dict.items()}


def get_members_attr_list_by_role(member_dict, role_name, attr):
    """Get member attributes list by role"""
    filtered_members = []
    for _member_id, member_info in member_dict.items():
        exclusion_list = ['@everyone']
        roles = [role.name for role in member_info['roles'] if role.name not in exclusion_list]
        if role_name in roles:
            filtered_members.append(member_info[attr])
    return filtered_members


async def async_bungie_search_users(player_name):
    """Search Bungie for player_name"""
    search_url = f'/User/SearchUsers/?q={player_name}'
    raw_json = await async_bungie_request_handler(search_url)
    if raw_json:
        bungie_results = raw_json['Response']
        logger.info('Bungie Search response:\n%s', bungie_results)
        if len(bungie_results) == 0:
            endpoint_path = f'/Destiny2/SearchDestinyPlayer/{4}/{player_name}/'
            player_raw_json = await async_bungie_request_handler(endpoint_path)
            if player_raw_json:
                bungie_results = player_raw_json['Response']
                logger.info('Destiny Search response:\n%s', bungie_results)
            raise VoluspaError('player_raw_json was empty!')
        return bungie_results
    raise VoluspaError('raw_json was empty!')


def get_discord_member_record(member):
    """Get the Discord member record"""
    return {
        'name': member.name,
        'display_name': member.display_name,
        'nick': member.nick,
        'roles': member.roles,
        'top_role': member.top_role
    }


class Members(commands.Cog):
    """Members Cog class"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['m'])
    @commands.cooldown(1, 180, commands.BucketType.guild)
    @commands.guild_only()
    async def members(self, ctx):
        """Returns Discord member information"""
        # TODO: This is a mess and needs to be unwound
        async with ctx.typing():
            # regex_alphanumeric = re.compile(r'[\W_]+', re.UNICODE)

            # TODO: dangerous at scale... this should be done JIT from the generator
            member_list = list(self.bot.get_all_members())
            member_dict = {}
            for member in member_list:
                member_dict[member.id] = get_discord_member_record(member)

            gp_member_roles = filter_members_by_field(member_dict, 'roles')
            gp_members = get_members_attr_list_by_role(gp_member_roles, 'ghost-proxy-member', 'name')
            alpha_sorted_gp_members = sorted(gp_members, key=str.lower)

            # This will only ever return max of 100 records, thus safe to do ahead of time
            bungie_num_members, bungie_member_list, _bungie_members = await async_get_bungie_clan_members()
            _, bungie_member_types_dict = await async_get_bungie_member_type_dict()
            bungie_member_list_alpha_sorted = sorted(bungie_member_list, key=str.lower)
            # NOTE: bungie_member_list = [member['destinyUserInfo']['displayName'], ...]

            # regex_pattern = re.compile(r'\W+')

            # def sanitize_string(_string):
            #     stage_1 = regex_pattern.sub('', _string)
            #     return regex_alphanumeric.sub('', stage_1)

            missing_discord_members = []
            missing_discord_admins = []

            for bungie_member in bungie_member_list_alpha_sorted:
                member_missing = True
                for discord_member in alpha_sorted_gp_members:
                    if bungie_member.lower() in discord_member.lower() or discord_member.lower() in bungie_member.lower():
                        member_missing = False
                        break
                if member_missing:
                    if bungie_member in bungie_member_types_dict['members']:
                        missing_discord_members.append(bungie_member)
                    elif bungie_member in bungie_member_types_dict['admins']:
                        missing_discord_admins.append(bungie_member)

            invalid_discord_members = []
            member_found = False
            for discord_member in alpha_sorted_gp_members:
                for bungie_member in bungie_member_list_alpha_sorted:
                    if bungie_member.lower() in discord_member.lower():
                        member_found = True
                        break
                if not member_found:
                    invalid_discord_members.append(discord_member)

            logger.info("GP Members missing from Discord (%s):\n%s\n",
                len(missing_discord_members),
                missing_discord_members
            )
            logger.info("GP Admins missing from Discord: (%s):\n%s\n",
                len(missing_discord_admins),
                missing_discord_admins
            )

            num_gp_members_missing = len(missing_discord_members)
            num_gp_admins_missing = len(missing_discord_admins)
            num_gp_all_members_discord = len(alpha_sorted_gp_members)
            num_discord_users = len(member_dict)
            num_gp_all_members_bungie = bungie_num_members

            num_gp_all_members_missing = num_gp_members_missing + num_gp_admins_missing
            error_diff = (num_gp_all_members_bungie - num_gp_all_members_discord) - num_gp_all_members_missing
            raw_bungie_diff = num_gp_all_members_bungie - num_gp_all_members_discord
            percent_gp_all_members_missing = math.ceil(num_gp_all_members_discord / num_gp_all_members_bungie * 100)

            logger.info('Potential Invalid members: %s', invalid_discord_members)

            msg_final = '--\\\\\\\\//--\n' \
                        '**Ghost Proxy Members on Discord: {}**\n' \
                        '_Total Discord Members: {}_\n' \
                        'Ghost Proxy Members (Bungie.net): {}\n' \
                        'Total Ghost Proxy Members Missing from Discord: {}\n' \
                        '  _Error Diff: {} -- Raw Diff (Bungie - Discord): {}_\n\n' \
                        'Percent Members on Discord: ~{}%\n\n' \
                        'Admins Missing ({}):\n' \
                        '```  {}```\n' \
                        'Members Missing ({}):\n' \
                        '```  {}```'.format(
                            num_gp_all_members_discord,
                            num_discord_users,
                            num_gp_all_members_bungie,
                            num_gp_all_members_missing,
                            error_diff,
                            raw_bungie_diff,
                            percent_gp_all_members_missing,
                            num_gp_admins_missing,
                            '\n  '.join(missing_discord_admins),
                            num_gp_members_missing,
                            '\n  '.join(missing_discord_members)
                        )
            msg_final2 = '---\nPotential role updates needed: {}\n```  {}```'.format(
                len(invalid_discord_members),
                '\n  '.join(invalid_discord_members)
            )

        await send_multipart_msg(ctx, msg_final)
        if len(invalid_discord_members) > 0:
            await send_multipart_msg(ctx, msg_final2)

    @commands.command(name='clan-stats', aliases=['cs'])
    @commands.guild_only()
    async def clan_stats(self, ctx, min_level: int = 0):
        """Generate clan stats"""
        async with ctx.typing():
            # platform_type = 4  # TODO MEH......
            logger.info('Getting clan member list for stats...')
            _num_members, member_list = await async_get_clan_members()
            destiny_members = [get_destiny_member_info(mem) for mem in member_list]
            logger.info('Found records for %s member(s)', len(destiny_members))
            clan_characters = await filter_characters_from_members(destiny_members)
            num_characters = sum(len(chars) for chars in clan_characters)
            logger.info('Found records for %s character(s)', num_characters)
            hunters, titans, warlocks, num_clan_chars = filter_character_types(clan_characters, min_level)
            num_filtered_chars = len(hunters) + len(titans) + len(warlocks)
            all_chars = hunters + titans + warlocks
            result_msg = '{}{}' \
                'Total Number of Characters {}: **{}**\n' \
                '  - Lowest Light Level: {}\n' \
                '  - Mean / Median Light Level: {} / {}\n' \
                '  - Highest Light Level: {}\n\n' \
                '{}\n\n' \
                '{}\n\n' \
                '{}'.format(
                    'Minimum Light Level Threshold: {}\n'.format(min_level) if min_level else '',
                    'Total Number of Characters in Clan: {}\n\n'.format(num_clan_chars) if min_level else '',
                    f'>={min_level}' if min_level else '',
                    num_filtered_chars,
                    min(all_chars),
                    math.ceil(statistics.mean(all_chars)),
                    math.ceil(statistics.median(all_chars)),
                    max(all_chars),
                    await generate_char_stats_message(hunters, num_filtered_chars, 'Hunters'),
                    await generate_char_stats_message(titans, num_filtered_chars, 'Titans'),
                    await generate_char_stats_message(warlocks, num_filtered_chars, 'Warlocks')
                )
            embed = default_embed(
                title='Clan Character Stats',
                description=result_msg
            )
        await ctx.send(embed=embed)

    @commands.command(name='members-online', aliases=['mo'])
    async def members_online(self, ctx):
        """Lists GP Members currently playing"""
        async with ctx.typing():
            logger.info('Looking up currently online Ghost Proxy members...')
            _num_members, member_list = await async_get_clan_members()
            cur_members_online = [
                member['destinyUserInfo']['displayName']
                for member in member_list
                if member['isOnline']
            ]
            result_msg = f'{len(cur_members_online)} Members Online\n' \
                f'{format_list(cur_members_online, none_msg="None - Check back soon!")}'

            mem_online_embed = default_embed(
                title='Ghost Proxy Members In-Game',
                description=result_msg
            )

        await ctx.send(embed=mem_online_embed)

    @commands.command(name='members-with-role', aliases=['mwr'])
    @commands.guild_only()
    async def members_with_role(self, ctx, *, role_name):
        """Lists Discord Users with a given role"""
        async with ctx.typing():
            logger.info('Getting Discord members with role: %s', role_name)
            member_list = list(self.bot.get_all_members())
            member_dict = {}
            for member in member_list:
                member_dict[member.id] = {
                    'display_name': member.display_name,
                    'roles': member.roles
                }

            role_members = get_members_attr_list_by_role(member_dict, role_name, 'display_name')
            result_msg = f'{format_list(role_members, none_msg="No members found!")}'
            result_embed = default_embed(
                title=f'{len(role_members)} member{"s" if len(role_members) != 1 else ""} with @{role_name}',
                description=result_msg
            )

        await ctx.send(embed=result_embed)

    @commands.command(name='find-player', aliases=['fp'])
    @commands.guild_only()
    async def find_player(self, ctx, *, player_name):
        """Simple Bungie PC player search"""
        #num_players, results = bungie_search_users(player_name)
        results = await async_bungie_search_users(player_name)
        logger.info('>> Bungie Player Search Results: %s', results)
        # TAKE FIRST ONLY FOR NOW
        await ctx.send(f'Found {len(results)} Matching Players{" , top result below." if len(results) > 0 else ""}')
        player = None
        for player_result in itertools.islice(results, 0, 10):
            if 'blizzardDisplayName' in player_result:
                #if player_name.lower() == player_result['displayName'].lower() or player_result['displayName'].lower() in player_name.lower():
                player = player_result
        if player:
            logger.info('Found Player:\n MemberID: %s Name: %s BlizzardName: %s',
                player['membershipId'],
                player['displayName'],
                player.get('blizzardDisplayName', 'N/A')
            )
            #logger.info('Player Results:\n{}'.format(results))
            embed = discord.Embed(
                title="{}".format(player['displayName']),
                description="{}".format(player['about']),
                color=0x009933
            )
            #embed.set_image(url='https://www.bungie.net{}'.format(player['profilePicturePath']))
            embed.add_field(name='Blizzard ID', value="{}".format(player['blizzardDisplayName']))
            if 'http' in player['profilePicturePath']:
                url_target = player['profilePicturePath']
            else:
                url_target = f'https://www.bungie.net{player["profilePicturePath"]}'
            embed.set_thumbnail(url=url_target)
        else:
            embed = discord.Embed(
                title='{}'.format('Search for "{}"'.format(player_name)),
                description='{}'.format('No results found or player is not registered on Bungie.net'),
                color=0x993300
            )
        await ctx.send(embed=embed)


async def setup(bot):
    """Cog Setup"""
    await bot.add_cog(Members(bot))
