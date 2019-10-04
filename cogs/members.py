import itertools
import logging
import math
import pprint
import re
import statistics

from modules.config import CONFIG
from modules.discord_utils import send_multipart_msg

import aiohttp
import discord
from discord.ext import commands
import requests
# https://github.com/seatgeek/fuzzywuzzy <- instead

from modules.custom_embed import default_embed, format_list

logger = logging.getLogger('voluspa.cog.members')

from modules.custom_embed import default_embed


def filter_character_types(clan_characters, min_level=0):
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
    num_chars = len(light_levels)
    percent_total = round(((num_chars / total_chars) * 100), 2)
    max_ll = max(light_levels)
    min_ll = min(light_levels)
    mean_ll = math.ceil(statistics.mean(light_levels))
    median_ll = math.ceil(statistics.median(light_levels))
    stats_msg = 'Number of {}: **{}**\n' \
                '  - Percent of Chars: {}%\n' \
                '  - Lowest LL: {}\n' \
                '  - Mean / Median LL: {} / {}\n' \
                '  - Highest LL: {}'.format(
                    char_type,
                    num_chars,
                    percent_total,
                    min_ll,
                    mean_ll,
                    median_ll,
                    max_ll
                )
    return stats_msg


# TODO: Deprecated - Remove
async def get_destiny_profile_characters(destiny_membership_id, membership_type):
    # https://bungie-net.github.io/multi/operation_get_Destiny2-GetProfile.html#operation_get_Destiny2-GetProfile
    # {'iconPath': '', 'membershipType': 4, 'membershipId': '4611686018467468651', 'displayName': 'Mirage'}
    # request_url = https://www.bungie.net/platform/Destiny2/4/Profile/4611686018467468651/
    target_endpoint = '/Destiny2/{}/Profile/{}/'.format(membership_type, destiny_membership_id)
    # ?components=Profiles,Characters
    profile_params = {'components': 'Profiles,Characters'}
    request_url = 'https://www.bungie.net/platform{}'.format(target_endpoint)
    # TODO: Replace requests with aiohttp
    r = requests.get(request_url, headers={'X-API-Key': CONFIG.Bungie.api_key}, params=profile_params)
    raw_json = r.json()
    # logger.info('Destiny Profile:\n{}'.format(raw_json))
    bungie_response = raw_json['Response']
    characters_data = bungie_response['characters']['data']
    characters = []
    for char in characters_data.values():
        characters.append({'classType': char['classType'], 'light': char['light']})
    return characters


async def async_get_destiny_profile_characters(destiny_membership_id, membership_type):
    target_endpoint = '/Destiny2/{}/Profile/{}/'.format(membership_type, destiny_membership_id)
    # ?components=Profiles,Characters
    profile_params = {'components': 'Profiles,Characters'}
    request_url = 'https://www.bungie.net/platform{}'.format(target_endpoint)

    async with aiohttp.ClientSession() as session:
        async with session.get(request_url, headers={'X-API-Key': CONFIG.Bungie.api_key}, params=profile_params) as r:
            if r.status == 200:
                raw_json = await r.json()
                bungie_response = raw_json['Response']
                characters_data = bungie_response['characters']['data']
                characters = []
                for char in characters_data.values():
                    characters.append({'classType': char['classType'], 'light': char['light']})
                return characters


async def async_get_member_data_by_id(membership_id, membership_type, platform_type=4):  # platform_type 4 is PC
    target_endpoint = '/User/GetMembershipsById/{}/{}/'.format(membership_id, membership_type)
    request_url = 'https://www.bungie.net/platform{}'.format(target_endpoint)
    async with aiohttp.ClientSession() as session:
        async with session.get(request_url, headers={'X-API-Key': CONFIG.Bungie.api_key}) as r:
            if r.status == 200:
                raw_json = await r.json()
                bungie_response = raw_json['Response']
                destiny_memberships = bungie_response['destinyMemberships']
                destiny_membership_info = [dm for dm in destiny_memberships if dm['membershipType'] == platform_type][0]
                # logger.info('> Returning: {}'.format(destiny_membership_info['membershipId']))
                return destiny_membership_info['membershipId']


async def async_get_clan_members():
    target_endpoint = '/GroupV2/{}/Members/'.format(CONFIG.Bungie.clan_group_id)
    request_url = 'https://www.bungie.net/platform{}'.format(target_endpoint)
    async with aiohttp.ClientSession() as session:
        async with session.get(request_url, headers={'X-API-Key': CONFIG.Bungie.api_key}) as r:
            if r.status == 200:
                raw_json = await r.json()
                bungie_results = raw_json['Response']
                member_list = bungie_results['results']
                num_members = bungie_results['totalResults']
                logger.info('BUNGIE MEMBER LIST:\n{}'.format(member_list))
                return num_members, member_list


def get_member_data_by_id(membership_id, membership_type, platform_type=4):  # platform_type 4 is PC
    # https://bungie-net.github.io/multi/operation_get_User-GetMembershipDataById.html#operation_get_User-GetMembershipDataById
    target_endpoint = '/User/GetMembershipsById/{}/{}/'.format(membership_id, membership_type)
    request_url = 'https://www.bungie.net/platform{}'.format(target_endpoint)
    r = requests.get(request_url, headers={'X-API-Key': CONFIG.Bungie.api_key})
    raw_json = r.json()
    # logger.info('MEMBER DATA INFO:\n{}'.format(raw_json))
    bungie_response = raw_json['Response']
    destiny_memberships = bungie_response['destinyMemberships']
    destiny_membership_info = [dm for dm in destiny_memberships if dm['membershipType'] == platform_type][0]
    # logger.info('> Returning: {}'.format(destiny_membership_info['membershipId']))
    return destiny_membership_info['membershipId']


def get_destiny_member_info(member):
    # >> > m['destinyUserInfo']['membershipType']
    # 4
    # >> > m['destinyUserInfo']['membershipId']
    # 'displayName':
    membership_type = member['destinyUserInfo']['membershipType']
    membership_id = member['destinyUserInfo']['membershipId']
    display_name = member['destinyUserInfo']['displayName']

    return {
        'membershipId': member['destinyUserInfo']['membershipId'],
        'membershipType': member['destinyUserInfo']['membershipType'],
        'displayName': member['destinyUserInfo']['displayName'],
        'LastSeenDisplayName': member['destinyUserInfo']['LastSeenDisplayName'],
        'LastSeenDisplayNameType': member['destinyUserInfo']['LastSeenDisplayNameType'],
        'crossSaveOverride': member['destinyUserInfo']['crossSaveOverride'],
        'supplementalDisplayName': member['bungieNetUserInfo']['supplementalDisplayName'],
        'bungieNetDisplayName': member['bungieNetUserInfo']['displayName'],
    }


# TODO: Abstract further
async def async_bungie_request_handler(target_endpoint):  # , request_url):
    request_url = 'https://www.bungie.net/platform{}'.format(target_endpoint)
    # target_url = f'{request_url}{target_endpoint}'
    async with aiohttp.ClientSession() as session:
        async with session.get(request_url, headers={'X-API-Key': CONFIG.Bungie.api_key}) as r:
            if r.status == 200:
                raw_json = await r.json()
                return raw_json
            else:
                return None  # BOOM


async def async_get_bungie_clan_members():
    target_endpoint = '/GroupV2/{}/Members/'.format(CONFIG.Bungie.clan_group_id)
    #request_url = 'https://www.bungie.net/platform'
    response = await async_bungie_request_handler(target_endpoint)
    logger.info(f'Bungie Response: {response}')
    bungie_results = response['Response']
    logger.info('BUNGIE MEMBER LIST:\n{}'.format(bungie_results))
    member_results = bungie_results['results']
    num_members = bungie_results['totalResults']
    member_list = [member['destinyUserInfo']['displayName'] for member in member_results]
    return num_members, member_list, member_results

def get_clan_members():
    target_endpoint = '/GroupV2/{}/Members/'.format(CONFIG.Bungie.clan_group_id)
    request_url = 'https://www.bungie.net/platform{}'.format(target_endpoint)
    r = requests.get(request_url, headers={'X-API-Key': CONFIG.Bungie.api_key})
    raw_json = r.json()
    bungie_results = raw_json['Response']
    member_list = bungie_results['results']
    num_members = bungie_results['totalResults']
    # logger.info('BUNGIE MEMBER LIST:\n{}'.format(member_list))
    return num_members, member_list


def get_bungie_member_list():  # TODO THIS ONE
    member_list_url = "https://www.bungie.net/platform/GroupV2/{}/Members/".format(CONFIG.Bungie.clan_group_id)
    r = requests.get(member_list_url, headers={'X-API-Key': CONFIG.Bungie.api_key})
    raw_json = r.json()
    bungie_results = raw_json['Response']
    logger.info('BUNGIE MEMBER LIST:\n{}'.format(bungie_results))
    member_results = bungie_results['results']
    num_members = raw_json['Response']['totalResults']
    member_list = [member['destinyUserInfo']['displayName'] for member in member_results]
    return num_members, member_list, member_results


def get_bungie_member_type_dict():
    member_list_url = "https://www.bungie.net/platform/GroupV2/{}/Members/".format(CONFIG.Bungie.clan_group_id)
    r = requests.get(member_list_url, headers={'X-API-Key': CONFIG.Bungie.api_key})
    raw_json = r.json()
    bungie_results = raw_json['Response']
    logger.info('BUNGIE MEMBER LIST:\n{}'.format(bungie_results))
    member_results = bungie_results['results']
    num_members = raw_json['Response']['totalResults']
    # member_list = [{'displayName': member['destinyUserInfo']['displayName'], 'memberType': member['memberType']} for member in member_results]
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


def filter_members_by_field(member_dict, field_name):
    return {member_id: {
        'name': member_info['display_name'],
        field_name: member_info.get(field_name, None)
    } for member_id, member_info in member_dict.items()}


def filter_member_roles():
    pass


def get_members_attr_list_by_role(member_dict, role_name, attr):
    filtered_members = []
    for member_id, member_info in member_dict.items():
        exclusion_list = ['@everyone']
        roles = [role.name for role in member_info['roles'] if role.name not in exclusion_list]
        if role_name in roles:
            filtered_members.append(member_info[attr])
    return filtered_members

# elif message.content.startswith('!members'):
#     x = message.server.members
#     for member in x:
#         print(member.name)


def bungie_search_users(player_name):
    search_url = "https://www.bungie.net/platform/User/SearchUsers/?q={}".format(player_name)
    r = requests.get(search_url, headers={'X-API-Key': CONFIG.Bungie.api_key})
    raw_json = r.json()
    bungie_results = raw_json['Response']
    logger.info('Bungie Search response:\n{}'.format(bungie_results))

    if len(bungie_results) == 0:
        endpoint_path = f'/Destiny2/SearchDestinyPlayer/{4}/{player_name}/'
        target_url = f'https://www.bungie.net/platform{endpoint_path}'
        r = requests.get(target_url, headers={'X-API-Key': CONFIG.Bungie.api_key})
        raw_json = r.json()
        bungie_results = raw_json['Response']
        logger.info(f'Destiny Search response:\n{bungie_results}')
    '''
    # [{'membershipId': '1595120', 'uniqueName': 'DESTROYRofWRLDS', 
    # 'displayName': 'Mirage', 'profilePicture': 70655, 'profileTheme': 1101, 
    # 'userTitle': 0, 'successMessageFlags': '16', 'isDeleted': False, 
    # 'about': 'SEE YOU SPACE COWBOY...', 'firstAccess': '2010-09-20T09:36:17.91Z', 
    # 'lastUpdate': '2018-09-04T21:10:12.901Z', 'psnDisplayName': 'Mirage_1337', 
    # 'xboxDisplayName': 'D3STROYRofWRLDS', 'showActivity': False, 'locale': 'en', 
    # 'localeInheritDefault': True, 'showGroupMessaging': True, 
    # 'profilePicturePath': '/img/profile/avatars/cc25.jpg', 'profileThemeName': 'd2_01', 
    # 'userTitleDisplay': 'Newbie', 'statusText': '', 'statusDate': '0001-01-01T00:00:00Z', 
    # 'blizzardDisplayName': 'Mirage#1758'},
    '''
    #results = bungie_results['results']
    #num_results = raw_json['Response']['totalResults']
    #player_list = [member['destinyUserInfo']['displayName'] for member in member_results]
    #return num_results, results
    return bungie_results


def bungie_get_profile(player_name=None):
    bungie_account_url = "http://www.bungie.net/platform/User/GetBungieAccount/{}/254/".format(
        1595120
    )
    r = requests.get(bungie_account_url, headers={'X-API-Key': CONFIG.Bungie.api_key})
    raw_json = r.json()
    logger.info('RESPONSE ({}):\n{}'.format(bungie_account_url, raw_json))
    # {'Response': {'destinyMemberships': [{'membershipType': 2, 'membershipId': '4611686018428895515',
    # 'displayName': 'Mirage_1337'}, {'membershipType': 4, 'membershipId': '4611686018467468651',
    # 'displayName': 'Mirage'}], 'bungieNetUser': {'membershipId': '1595120', 'uniqueName': 'DESTROYRofWRLDS',
    # 'displayName': 'Mirage', 'profilePicture': 70655, 'profileTheme': 1101, 'userTitle': 0,
    # 'successMessageFlags': '16', 'isDeleted': False, 'about': 'SEE YOU SPACE COWBOY...',
    # 'firstAccess': '2010-09-20T09:36:17.91Z', 'lastUpdate': '2018-09-04T21:10:12.901Z',
    # 'psnDisplayName': 'Mirage_1337', 'xboxDisplayName': 'D3STROYRofWRLDS', 'showActivity': False,
    # 'locale': 'en', 'localeInheritDefault': True, 'showGroupMessaging': True,
    # 'profilePicturePath': '/img/profile/avatars/cc25.jpg', 'profileThemeName': 'd2_01',
    # 'userTitleDisplay': 'Newbie', 'statusText': '', 'statusDate': '0001-01-01T00:00:00Z',
    # 'blizzardDisplayName': 'Mirage#1758'}}, 'ErrorCode': 1, 'ThrottleSeconds': 0,
    # 'ErrorStatus': 'Success', 'Message': 'Ok', 'MessageData': {}}

    # /User/GetBungieNetUserById/{id}/
    bungie_net_user_url = "http://www.bungie.net/platform/User/GetBungieNetUserById/{id}/".format(
        id=1595120
    )
    r = requests.get(bungie_net_user_url, headers={'X-API-Key': CONFIG.Bungie.api_key})
    raw_json = r.json()
    logger.info('RESPONSE ({}):\n{}'.format(bungie_net_user_url, raw_json))
    # {'ErrorCode': 217, 'ThrottleSeconds': 0, 'ErrorStatus': 'UserCannotResolveCentralAccount',
    # 'Message': "We couldn't find the account you're looking for. The account may not exist,
    # or we may be experiencing technical difficulties.", 'MessageData': {}}

    bungie_profile_url = "http://www.bungie.net/platform/Destiny2/{membershipType}/Profile/{membershipId}/LinkedProfiles/".format(
        membershipType=4,
        membershipId=4611686018467468651
    )
    r = requests.get(bungie_profile_url, headers={'X-API-Key': CONFIG.Bungie.api_key})
    raw_json = r.json()
    logger.info('RESPONSE ({}):\n{}'.format(bungie_profile_url, raw_json))

    destiny_memberships = "http://www.bungie.net/platform/User/GetMembershipsById/{membershipId}/{membershipType}/".format(
        membershipId=4611686018467468651,
        membershipType=4
    )
    r = requests.get(destiny_memberships, headers={'X-API-Key': CONFIG.Bungie.api_key})
    raw_json = r.json()
    logger.info('RESPONSE ({}):\n{}'.format(destiny_memberships, raw_json))

    # /Destiny/[MembershipType]/Stats/GetMembershipIdByDisplayName/[DisplayName]

    profile_url = "https://www.bungie.net/platform/Destiny2/{}/Profile/{}/".format(
        4,  # TigerBlizzard (PC)
        1595120  # ME
    )
    r = requests.get(profile_url, headers={'X-API-Key': CONFIG.Bungie.api_key})
    raw_json = r.json()
    logger.info('RESPONSE:\n{}'.format(raw_json))
    #bungie_results = raw_json['Response']
    #logger.info('Bungie response:\n{}'.format(bungie_results))
    #return bungie_results
    return


def get_discord_member_record(member):
    return {
        'name': member.name,
        'display_name': member.display_name,
        'nick': member.nick,
        'roles': member.roles,
        'top_role': member.top_role
    }


class Members(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['m'])
    @commands.cooldown(1, 180, commands.BucketType.guild)
    @commands.guild_only()
    async def members(self, ctx):
        """Returns Discord member information"""
        # TODO: This is a mess and needs to be unwound
        async with ctx.typing():
            regex_alphanumeric = re.compile(r'[\W_]+', re.UNICODE)

            # TODO: dangerous at scale... this should be done JIT from the generator
            member_list = [member for member in self.bot.get_all_members()]
            member_dict = {}
            for member in member_list:
                member_dict[member.id] = get_discord_member_record(member)

            gp_member_roles = filter_members_by_field(member_dict, 'roles')
            gp_members = get_members_attr_list_by_role(gp_member_roles, 'ghost-proxy-member', 'name')
            alpha_sorted_gp_members = sorted(gp_members, key=str.lower)

            # This will only ever return max of 100 records, thus safe to do ahead of time
            bungie_num_members, bungie_member_list, bungie_members = await async_get_bungie_clan_members()
            _, bungie_member_types_dict = get_bungie_member_type_dict()
            bungie_member_list_alpha_sorted = sorted(bungie_member_list, key=str.lower)
            # NOTE: bungie_member_list = [member['destinyUserInfo']['displayName'], ...]

            regex_pattern = re.compile(r'\W+')

            def sanitize_string(_string):
                stage_1 = regex_pattern.sub('', _string)
                return regex_alphanumeric.sub('', stage_1)

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

            logger.info("GP Members missing from Discord ({}):\n{}\n".format(
                len(missing_discord_members),
                missing_discord_members
            ))
            logger.info("GP Admins missing from Discord: ({}):\n{}\n".format(
                len(missing_discord_admins),
                missing_discord_admins
            ))

            num_gp_members_missing = len(missing_discord_members)
            num_gp_admins_missing = len(missing_discord_admins)
            num_gp_all_members_discord = len(alpha_sorted_gp_members)
            num_discord_users = len(member_dict)
            num_gp_all_members_bungie = bungie_num_members

            num_gp_all_members_missing = num_gp_members_missing + num_gp_admins_missing
            error_diff = (num_gp_all_members_bungie - num_gp_all_members_discord) - num_gp_all_members_missing
            raw_bungie_diff = num_gp_all_members_bungie - num_gp_all_members_discord
            percent_gp_all_members_missing = math.ceil(num_gp_all_members_discord / num_gp_all_members_bungie * 100)

            logger.info(f'Potential Invalid members: {invalid_discord_members}')

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
        async with ctx.typing():
            # platform_type = 4  # TODO MEH......
            num_members, member_list = await async_get_clan_members()
            destiny_members = [get_destiny_member_info(mem) for mem in member_list]
            clan_characters = await filter_characters_from_members(destiny_members)
            logger.info('clan_characters:\n{}\n'.format(clan_characters))
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
        #await send_multipart_msg(ctx, msg_final)

            embed = default_embed(
                title='Clan Character Stats',
                description=result_msg
            )
        await ctx.send(embed=embed)

    @commands.command(name='members-online', aliases=['mo'])
    async def members_online(self, ctx):
        """Lists Ghost Proxy Members currently playing"""
        async with ctx.typing():
            logger.info('Looking up currently online Ghost Proxy members...')
            num_members, member_list = await async_get_clan_members()
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
        """Lists Ghost Proxy Members with a given role"""
        async with ctx.typing():
            logger.info(f'Getting Discord members with role: {role_name}')
            member_list = [member for member in self.bot.get_all_members()]
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

    # @bot.command(name='get-profile')
    # async def get_player_profile(ctx, *, player_name):
    #     bungie_get_profile()
    #     return

    @commands.command(name='find-player', aliases=['fp'])
    @commands.guild_only()
    async def find_player(self, ctx, *, player_name):
        """Simple Bungie PC player search"""
        #num_players, results = bungie_search_users(player_name)
        results = bungie_search_users(player_name)
        logger.info('>> Bungie Player Search Results: {}'.format(results))
        # TAKE FIRST ONLY FOR NOW
        await ctx.send(f'Found {len(results)} Matching Players{" , top result below." if len(results) > 0 else ""}')
        player = None
        for player_result in itertools.islice(results, 0, 10):
            if 'blizzardDisplayName' in player_result:
                #if player_name.lower() == player_result['displayName'].lower() or player_result['displayName'].lower() in player_name.lower():
                player = player_result
        if player:
            logger.info('Found Player:\n MemberID: {} Name: {} BlizzardName: {}'.format(
                player['membershipId'],
                player['displayName'],
                player.get('blizzardDisplayName', 'N/A')
            ))
            #logger.info('Player Results:\n{}'.format(results))
            embed = discord.Embed(
                title="{}".format(player['displayName']),
                description="{}".format(player['about']),
                color=0x009933
            )
            #embed.set_image(url='https://www.bungie.net{}'.format(player['profilePicturePath']))
            embed.add_field(name='Blizzard ID', value="{}".format(player['blizzardDisplayName']))
            embed.set_thumbnail(url='https://www.bungie.net{}'.format(player['profilePicturePath']) if 'http' not in player['profilePicturePath'] else player['profilePicturePath'])
        else:
            embed = discord.Embed(
                title='{}'.format('Search for "{}"'.format(player_name)),
                description='{}'.format('No results found or player is not registered on Bungie.net'),
                color=0x993300
            )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Members(bot))
