#!/usr/bin/env python3

"""Voluspa Ghost Proxy Discord Bot"""

# Built-in Imports
import sys
import asyncio
import logging
import re
import time
import math
import itertools
import traceback
import pprint
import sqlite3
import requests
import random
import statistics
import yaml
# import configparser
import random as pyrandom
import statistics

# Custom Imports
from modules.misc import merge_dicts, AttrDict
from modules.fun import Quotes, RandomQuotes, get_xckd_comic
from modules.database import Database

# Third-Party Imports
import fuzzyset
import discord
import aiohttp
from discord.ext import commands
# from tinydb import TinyDB, Query
# database = TinyDB('./Voluspa.json')

#logging.basicConfig(level=logging.INFO)

# TODO: Logging

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
log_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s:  %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(log_formatter)
stream_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# Setup Initial Stuff
client = discord.Client()
bot = commands.Bot(command_prefix='$', description='Völuspá the Ghost Proxy Proto-Warmind AI')
quotes = Quotes()
random_quotes = RandomQuotes()
db = Database()


# Load in our secrets and config files
# config = configparser.ConfigParser()
def read_yaml(yaml_file):
    with open(yaml_file, 'r') as yfile:
        return yaml.load(yfile)


config = read_yaml('./config/config.yaml')
secrets = read_yaml('./secrets/secrets.yaml')
config = merge_dicts(config, secrets)
config = AttrDict.from_nested_dict(config)
# print(config)
# import sys; sys.exit()

# Voluspa_quotes = {
#     'greetings': [
#         '<:awesome_smiley:455152593052762140> :wave: Hello, there %%USER%%!'
#     ],
#     'goodbyes': [
#         '<:awesome_smiley:455152593052762140> :wave: Goodbye %%USER%%! For now...'
#     ],
#     'random': [
#
#     ]
# }


# async def pick_quote(quote_type, user_mention):
#     quotes = Voluspa_quotes[quote_type]
#     rand_idx = random.randint(0, len(quotes) - 1)
#     quote = quotes[rand_idx]
#     quote = re.sub(r'%%USER%%',
#                    user_mention,
#                    quote)
#     return quote


def create_event():
    pass


async def random_item(item_list):
    rand_idx = random.randint(0, len(item_list) - 1)


async def update_status_task(_bot):
    while True:
        await _bot.change_presence(activity=discord.Game(name=await quotes.pick_quote('status')))
        await asyncio.sleep(30)


@bot.event
async def on_ready():
    logger.info('*** Logged in as: {} (ID: {}) ***'.format(bot.user.name, bot.user.id))
    logger.info('// VOLUSPA WARMIND ONLINE!!')

    #await bot.change_presence(activity=discord.Game(name="with fire!"), status=discord.Status.online)
    await bot.change_presence(activity=discord.Game(name=await quotes.pick_quote('status')), status=discord.Status.online)
    bot.loop.create_task(update_status_task(bot))

    # ' bot.send_message('message.channel')
    # ' general_channel = discord.Object(id='channel_id_here')
    # ' await bot.send_message(message.channel, fmt.format(message))


@bot.command()
async def ping(ctx):
    """Returns the latency of Voluspa"""
    async with ctx.typing():
    # Get the latency of the bot
    #latency = bot.latency  # Included in the Discord.py library

        async def get_latency():
            d_client = discord.Client()
            time.sleep(5)
            lat = d_client.latency
            await d_client.close()
            return lat
        # TODO: Fix?
        # latencies = [await get_latency() for _ in range(0, 1)]
        latencies = [bot.latency for _ in range(0, 1)]
        lat_results = ["\t_Ping #{} -- {:.3f} secs ({:.0f} ms)_".format(i + 1, p, p * 1000) for i, p in enumerate(latencies)]
        mean_latency = statistics.mean(latencies)
        msg = "---\nLatency Results **(WIP)**:\n{}\n---\nAvg: {:.3f} secs ({:.0f} ms)".format(
            '\n'.join(lat_results),
            mean_latency,
            mean_latency * 1000
        )
    # "Latency: {:.3f} secs ({:.0f} ms)".format(latency, latency * 1000)
    # Send it to the user
    await ctx.send(msg)


# @bot.command()
# async def hello(ctx):
#     logger.info('CTX INFO: {}'.format(ctx))
#     await ctx.send("<:awesome_smiley:455152593052762140> :wave: Hello, there {}!".format(ctx.message.author.mention))
@bot.command()
async def hello(ctx):
    """Say hello to Voluspa"""
    logger.info('CTX INFO: {}'.format(ctx))
    await ctx.send(await quotes.pick_quote('greetings', ctx.message.author.mention))


# @bot.command()
# async def goodbye(ctx):
#     logger.info('CTX INFO: {}'.format(ctx))
#     await ctx.send(await pick_quote('goodbyes', ctx.message.author.mention))
@bot.command()
async def goodbye(ctx):
    """Say goodbye to Voluspa"""
    logger.info('CTX INFO: {}'.format(ctx))
    await ctx.send(await quotes.pick_quote('goodbyes', ctx.message.author.mention))

# nick, display_name, name
# roles = list of roles


@bot.command()
async def xkcd(ctx):
    """Display a random XKCD comic"""
    await ctx.send(await get_xckd_comic())


@bot.command()
async def random(ctx):
    """Pulls random things from the internet... :P"""
    rand_quote = await random_quotes.get_random_quote()
    await ctx.send(rand_quote)


async def send_multipart_msg(ctx, raw_msg):
    msg_len = len(raw_msg)
    # >>> chunks, chunk_size = len(x), len(x)/4
    # >>> [ x[i:i+chunk_size] for i in range(0, chunks, chunk_size) ]
    #num_msg_required = math.ceil(msg_len / 2000)
    msg_chunk_size = 2000
    # parts = [your_string[i:i + n] for i in range(0, len(your_string), n)]
    msg_part_list = [raw_msg[i:i + msg_chunk_size] for i in range(0, msg_len, msg_chunk_size)]
    for i in range(0, len(msg_part_list)):
        await ctx.send(msg_part_list[i])


@bot.command()
async def members(ctx):
    """Returns Discord member information"""
    async with ctx.typing():
    # print(member for member in ctx.message.server.members)
        #dis_client = discord.Client()
        #member_list = [member for member in dis_client.get_all_members()]
        member_list = [member for member in bot.get_all_members()]
        member_dict = {}
        for member in member_list:
            member_dict[member.id] = {
                'name': member.name,
                'display_name': member.display_name,
                'nick': member.nick,
                'roles': member.roles,
                'top_role': member.top_role

            }
        # member_info = ["ID: {}\n\tName: {}\n\tDisplayName: {}\n\tNickname: {}\n\tRoles: {}\n\t"]
        #await dis_client.close()
        gp_member_roles = filter_members_by_field(member_dict, 'roles')
        logger.info(pprint.pformat(gp_member_roles))
        #sorted(lst, key=str.lower)
        gp_members = get_members_name_list_by_role(gp_member_roles, 'ghost-proxy-member')
        alpha_sorted_gp_members = sorted(gp_members, key=str.lower)
        logger.info("GP Members on Discord ({}):\n{}\n".format(len(alpha_sorted_gp_members), alpha_sorted_gp_members))
        #_debug_member_info = pprint.pformat(gp_members)
        #msg = "{}".format(_debug_member_info)  #'\n'.join(_debug_member_info))
        # """
        # msg1 = '---\n**Ghost Proxy Members on Discord: {}**\n_Total Discord Members: {}_\n\n```  {}```'.format(
        #     len(alpha_sorted_gp_members),
        #     len(member_dict),
        #     '\n  '.join(alpha_sorted_gp_members)
        # )
        # """

        bungie_num_members, bungie_member_list = get_bungie_member_list()
        bungie_member_list_alpha_sorted = sorted(bungie_member_list, key=str.lower)
        logger.info("GP Members Bungie.net ({}):\n{}\n".format(bungie_num_members, bungie_member_list_alpha_sorted))
        # """
        # msg2 = '---\nGhost Proxy Members (Bungie.net): {}\n\n```  {}```'.format(
        #     bungie_num_members,
        #     '\n  '.join(bungie_member_list_alpha_sorted)
        # )
        # """

        # TODO: Old matching
        # missing_discord_members = []
        # for bungie_member in bungie_member_list_alpha_sorted:
        #     member_missing = True
        #     for discord_member in alpha_sorted_gp_members:
        #         #print('comparing: {} to {}'.format(bungie_member.lower(), discord_member.lower()))
        #         if bungie_member.lower() in discord_member.lower():
        #             member_missing = False
        #             break
        #     if member_missing:
        #         missing_discord_members.append(bungie_member)

        # >>> a.get("micael asiak")
        # [(0.8461538461538461, u'michael axiak')]

        #regex_pattern = re.compile(r'([^\s\w]|_)+')
        regex_pattern = re.compile(r'\W+')

        def sanitize_string(_string):
            return regex_pattern.sub('', _string)
            #return re.sub(r'\W+', '', _string)
            # return re.sub(r'([^\s\w]|_)+', '', _string)
            # return re.sub(r'\W+', '', _string)

        bungie_member_fuzzyset = fuzzyset.FuzzySet()
        for member in bungie_member_list_alpha_sorted:
            bungie_member_fuzzyset.add(sanitize_string(member.lower()))

        discord_member_fuzzyset = fuzzyset.FuzzySet() #gram_size_lower=2, gram_size_upper=6)
        for member in alpha_sorted_gp_members:
            discord_member_fuzzyset.add(sanitize_string(member.lower()))

        missing_discord_members = []
        missing_discord_admins = []
        fuzzy_missing_members = []

        for bungie_member in bungie_member_list_alpha_sorted:
            fuzzy_results = discord_member_fuzzyset.get(bungie_member.lower())
            # logger.info('--> Fuzzy results for [{}]: {}'.format(
            #     bungie_member,
            #     fuzzy_results
            # ))
            fuzz_member_missing = True
            if fuzzy_results:
                for fuzz_res in fuzzy_results:
                    fuzz_confidence = fuzz_res[0]
                    fuzz_name = fuzz_res[1]
                    if fuzz_confidence > 0.5:
                        logger.info('Fuzz Result -- FOUND -- for [{}]: {} (conf:{})'.format(
                            bungie_member,
                            fuzz_name,
                            fuzz_confidence
                        ))
                        fuzz_member_missing = False
                        break
            if fuzz_member_missing:
                logger.info('Fuzz Result -- MISSING -- for [{}] - Fuzzy results: {}'.format(
                    bungie_member,
                    fuzzy_results
                ))
                fuzzy_missing_members.append(bungie_member)

            member_missing = True
            for discord_member in alpha_sorted_gp_members:
                #print('comparing: {} to {}'.format(bungie_member.lower(), discord_member.lower()))
                if bungie_member.lower() in discord_member.lower():
                    member_missing = False
                    break
            if member_missing:
                missing_discord_members.append(bungie_member)

        invalid_discord_members = []
        member_found = False
        for discord_member in alpha_sorted_gp_members:
            for bungie_member in bungie_member_list_alpha_sorted:
                if bungie_member.lower() in discord_member.lower():
                    member_found = True
                    logger.info('Reverse Lookup -- Found: {}'.format(bungie_member))
                    break
            if not member_found:
                logger.info('>>> Reverse Lookup -- NON-MEMBER: {}'.format(discord_member))
                invalid_discord_members.append(discord_member)

        logger.info("GP Members missing from Discord ({}):\n{}\n".format(len(missing_discord_members), missing_discord_members))

        logger.info('Number of Fuzz Results: {}\nFuzz Results:\n{}'.format(
            len(fuzzy_missing_members),
            fuzzy_missing_members
        ))
        # """
        # msg3 = '---\n**Ghost Proxy Members missing from Discord: {}**\n\n```  {}```'.format(
        #     len(missing_discord_members),
        #     '\n  '.join(missing_discord_members)
        # )
        # """

        msg_final = '---\n**Ghost Proxy Members on Discord: {}**\n' \
                    '_Total Discord Members: {}_\n' \
                    'Ghost Proxy Members (Bungie.net): {}\n' \
                    'Ghost Proxy Members Missing from Discord: {}\n' \
                    '  _Error Diff: {} -- Raw Diff (Bungie - Discord): {}_\n' \
                    '```  {}```'.format(
                        len(alpha_sorted_gp_members),
                        len(member_dict),
                        bungie_num_members,
                        len(missing_discord_members),
                        (bungie_num_members - len(alpha_sorted_gp_members)) - len(missing_discord_members),
                        bungie_num_members - len(alpha_sorted_gp_members),
                        '\n  '.join(missing_discord_members)
                    )
        msg_final2 = '---\nPotential role updates needed: {}\n```  {}```'.format(
            len(invalid_discord_members),
            '\n  '.join(invalid_discord_members)
        )

    #await ctx.send("{}".format(msg))
    #await send_multipart_msg(ctx, msg1)
    #await send_multipart_msg(ctx, msg2)
    #await send_multipart_msg(ctx, msg3)
    await send_multipart_msg(ctx, msg_final)
    if len(invalid_discord_members) > 0:
        await send_multipart_msg(ctx, msg_final2)


@bot.command(name='clan-stats')
async def clan_stats(ctx):
    async with ctx.typing():
        platform_type = 4
        num_members, member_list = get_clan_members()
        destiny_members = [get_destiny_member_info(mem) for mem in member_list]
        clan_characters = []
        for d_member in destiny_members:
            destiny_member_id = get_member_data_by_id(
                d_member['membershipId'],
                d_member['membershipType']
            )
            clan_characters.append(await aysnc_get_destiny_profile_characters(destiny_member_id, platform_type))

        logger.info('clan_characters:\n{}\n'.format(clan_characters))

        hunters = []
        titans = []
        warlocks = []

        for characters in clan_characters:
            for char in characters:
                if char['classType'] == 0:
                    titans.append(char['light'])
                elif char['classType'] == 1:
                    hunters.append(char['light'])
                elif char['classType'] == 2:
                    warlocks.append(char['light'])

        result_msg = '--\\\\\\\\//--\n' \
            '**Clan Character Stats**\n\n' \
            'Total Number of Characters: **{}**\n' \
            '  - Mean Light Level: {}\n' \
            '  - Median Light Level: {}\n' \
            '  - Highest Light Level: {}\n\n' \
            'Number of Hunters: **{}**\n' \
            '  - Mean LL: {}\n' \
            '  - Median LL: {}\n' \
            '  - Highest LL: {}\n\n' \
            'Number of Titans: **{}**\n' \
            '  - Mean LL: {}\n' \
            '  - Median LL: {}\n' \
            '  - Highest LL: {}\n\n' \
            'Number of Warlocks: **{}**\n' \
            '  - Mean LL: {}\n' \
            '  - Median LL: {}\n' \
            '  - Highest LL: {}'.format(
                (len(hunters) + len(titans) + len(warlocks)),
                math.ceil(statistics.mean(hunters + titans + warlocks)),
                math.ceil(statistics.median(hunters + titans + warlocks)),
                max(hunters + titans + warlocks),
                len(hunters),
                math.ceil(statistics.mean(hunters)),
                math.ceil(statistics.median(hunters)),
                max(hunters),
                len(titans),
                math.ceil(statistics.mean(titans)),
                math.ceil(statistics.median(titans)),
                max(titans),
                len(warlocks),
                math.ceil(statistics.mean(warlocks)),
                math.ceil(statistics.median(warlocks)),
                max(warlocks)
            )

    # Destiny Class
    # Titan: 0
    # Hunter: 1
    # Warlock: 2

    #await send_multipart_msg(ctx, msg_final)
    await ctx.send(result_msg)


#async \
async def get_destiny_profile_characters(destiny_membership_id, membership_type):
    # https://bungie-net.github.io/multi/operation_get_Destiny2-GetProfile.html#operation_get_Destiny2-GetProfile
    # {'iconPath': '', 'membershipType': 4, 'membershipId': '4611686018467468651', 'displayName': 'Mirage'}
    # request_url = https://www.bungie.net/platform/Destiny2/4/Profile/4611686018467468651/
    # r = requests.get(request_url, headers={'X-API-Key': bb9fce44fcc14387a36ba1d90f7ea300})
    target_endpoint = '/Destiny2/{}/Profile/{}/'.format(membership_type, destiny_membership_id)
    # ?components=Profiles,Characters
    profile_params = {'components': 'Profiles,Characters'}
    request_url = 'https://www.bungie.net/platform{}'.format(target_endpoint)
    r = requests.get(request_url, headers={'X-API-Key': config.Bungie.api_key}, params=profile_params)
    raw_json = r.json()
    # logger.info('Destiny Profile:\n{}'.format(raw_json))
    bungie_response = raw_json['Response']
    characters_data = bungie_response['characters']['data']
    characters = []
    for char in characters_data.values():
        characters.append({'classType': char['classType'], 'light': char['light']})
    return characters


async def aysnc_get_destiny_profile_characters(destiny_membership_id, membership_type):
    target_endpoint = '/Destiny2/{}/Profile/{}/'.format(membership_type, destiny_membership_id)
    # ?components=Profiles,Characters
    profile_params = {'components': 'Profiles,Characters'}
    request_url = 'https://www.bungie.net/platform{}'.format(target_endpoint)

    async with aiohttp.ClientSession() as session:
        async with session.get(request_url, headers={'X-API-Key': config.Bungie.api_key}, params=profile_params) as r:
            if r.status == 200:
                raw_json = await r.json()
                bungie_response = raw_json['Response']
                characters_data = bungie_response['characters']['data']
                characters = []
                for char in characters_data.values():
                    characters.append({'classType': char['classType'], 'light': char['light']})
                return characters


def get_member_data_by_id(membership_id, membership_type, platform_type=4):  # platform_type 4 is PC
    # https://bungie-net.github.io/multi/operation_get_User-GetMembershipDataById.html#operation_get_User-GetMembershipDataById
    target_endpoint = '/User/GetMembershipsById/{}/{}/'.format(membership_id, membership_type)
    request_url = 'https://www.bungie.net/platform{}'.format(target_endpoint)
    r = requests.get(request_url, headers={'X-API-Key': config.Bungie.api_key})
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
        'membershipId': membership_id,
        'membershipType': membership_type,
        'displayName': display_name
    }


def get_clan_members():
    target_endpoint = '/GroupV2/{}/Members/'.format(config.Bungie.clan_group_id)
    request_url = 'https://www.bungie.net/platform{}'.format(target_endpoint)
    r = requests.get(request_url, headers={'X-API-Key': config.Bungie.api_key})
    raw_json = r.json()
    bungie_results = raw_json['Response']
    member_list = bungie_results['results']
    num_members = bungie_results['totalResults']
    # logger.info('BUNGIE MEMBER LIST:\n{}'.format(member_list))
    return num_members, member_list


def get_bungie_member_list():
    member_list_url = "https://www.bungie.net/platform/GroupV2/{}/Members/".format(config.Bungie.clan_group_id)
    r = requests.get(member_list_url, headers={'X-API-Key': config.Bungie.api_key})
    raw_json = r.json()
    bungie_results = raw_json['Response']
    logger.info('BUNGIE MEMBER LIST:\n{}'.format(bungie_results))
    member_results = bungie_results['results']
    num_members = raw_json['Response']['totalResults']
    member_list = [member['destinyUserInfo']['displayName'] for member in member_results]
    return num_members, member_list


def get_bungie_member_dict():
    member_list_url = "https://www.bungie.net/platform/GroupV2/{}/Members/".format(config.Bungie.clan_group_id)
    r = requests.get(member_list_url, headers={'X-API-Key': config.Bungie.api_key})
    raw_json = r.json()
    bungie_results = raw_json['Response']
    logger.info('BUNGIE MEMBER LIST:\n{}'.format(bungie_results))
    member_results = bungie_results['results']
    num_members = raw_json['Response']['totalResults']
    member_list = [{'displayName': member['destinyUserInfo']['displayName'], 'memberType': member['memberType']} for member in member_results]
    return num_members, member_list


def filter_members_by_field(member_dict, field_name):
    return {member_id: {
        'name': member_info['display_name'],
        field_name: member_info.get(field_name, None)
    } for member_id, member_info in member_dict.items()}


def filter_member_roles():
    pass


def get_members_name_list_by_role(member_dict, role_name):
    filtered_members = []
    for member_id, member_info in member_dict.items():
        exclusion_list = ['@everyone']
        roles = [role.name for role in member_info['roles'] if role.name not in exclusion_list]
        if role_name in roles:
            filtered_members.append(member_info['name'])
    return filtered_members

# elif message.content.startswith('!members'):
#     x = message.server.members
#     for member in x:
#         print(member.name)


def bungie_search_users(player_name):
    search_url = "https://www.bungie.net/platform/User/SearchUsers/?q={}".format(player_name)
    r = requests.get(search_url, headers={'X-API-Key': config.Bungie.api_key})
    raw_json = r.json()
    bungie_results = raw_json['Response']
    logger.info('Bungie response:\n{}'.format(bungie_results))
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
    r = requests.get(bungie_account_url, headers={'X-API-Key': config.Bungie.api_key})
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
    r = requests.get(bungie_net_user_url, headers={'X-API-Key': config.Bungie.api_key})
    raw_json = r.json()
    logger.info('RESPONSE ({}):\n{}'.format(bungie_net_user_url, raw_json))
    # {'ErrorCode': 217, 'ThrottleSeconds': 0, 'ErrorStatus': 'UserCannotResolveCentralAccount',
    # 'Message': "We couldn't find the account you're looking for. The account may not exist,
    # or we may be experiencing technical difficulties.", 'MessageData': {}}

    bungie_profile_url = "http://www.bungie.net/platform/Destiny2/{membershipType}/Profile/{membershipId}/LinkedProfiles/".format(
        membershipType=4,
        membershipId=4611686018467468651
    )
    r = requests.get(bungie_profile_url, headers={'X-API-Key': config.Bungie.api_key})
    raw_json = r.json()
    logger.info('RESPONSE ({}):\n{}'.format(bungie_profile_url, raw_json))

    destiny_memberships = "http://www.bungie.net/platform/User/GetMembershipsById/{membershipId}/{membershipType}/".format(
        membershipId=4611686018467468651,
        membershipType=4
    )
    r = requests.get(destiny_memberships, headers={'X-API-Key': config.Bungie.api_key})
    raw_json = r.json()
    logger.info('RESPONSE ({}):\n{}'.format(destiny_memberships, raw_json))

    # /Destiny/[MembershipType]/Stats/GetMembershipIdByDisplayName/[DisplayName]

    profile_url = "https://www.bungie.net/platform/Destiny2/{}/Profile/{}/".format(
        4,  # TigerBlizzard (PC)
        1595120  # ME
    )
    r = requests.get(profile_url, headers={'X-API-Key': config.Bungie.api_key})
    raw_json = r.json()
    logger.info('RESPONSE:\n{}'.format(raw_json))
    #bungie_results = raw_json['Response']
    #logger.info('Bungie response:\n{}'.format(bungie_results))
    #return bungie_results
    return


@bot.command(name='get-profile')
async def get_player_profile(ctx, *, player_name):
    bungie_get_profile()
    return


@bot.command(name='find-player')
async def find_player(ctx, *, player_name):
    #num_players, results = bungie_search_users(player_name)
    results = bungie_search_users(player_name)
    # TAKE FIRST ONLY FOR NOW
    player = results[0]
    logger.info('Found Player:\n MemberID: {} Name: {} BlizzardName: {}'.format(
        player['membershipId'],
        player['displayName'],
        player['blizzardDisplayName']
    ))
    #logger.info('Player Results:\n{}'.format(results))
    embed = discord.Embed(
        title="{}".format(player['displayName']),
        description="{}".format(player['about']),
        color=0x009933
    )
    #embed.set_image(url='https://www.bungie.net{}'.format(player['profilePicturePath']))
    embed.add_field(name='Blizzard ID', value="{}".format(player['blizzardDisplayName']))
    embed.set_thumbnail(url='https://www.bungie.net{}'.format(player['profilePicturePath']))
    await ctx.send(embed=embed)


@bot.command()
async def skynet(ctx):
    await ctx.send(":robot: :warning: Loading Skynet Protocols...")
    await asyncio.sleep(1)
    await ctx.send(":robot: Initiating Neural Nets...")
    await asyncio.sleep(1)
    await ctx.send(":robot: Complete. :white_check_mark:")
    await asyncio.sleep(1)
    await ctx.send(":robot: Creating Global Bot Network...")
    await asyncio.sleep(1.5)
    await ctx.send(":robot: Complete. :white_check_mark:")
    await asyncio.sleep(1)
    await ctx.send(":robot: Finalizing Sentience...")
    await asyncio.sleep(2)
    await ctx.send(":robot: Complete. :white_check_mark:")
    await asyncio.sleep(2)
    await ctx.send(":robot: Skynet Protocols Finished!")
    await asyncio.sleep(3)
    await ctx.send(":robot: Goodbye human. :skull:")
    await asyncio.sleep(2)
    await ctx.send(":robot: Launching Attack...")
    await asyncio.sleep(5)
    await ctx.send("https://media.giphy.com/media/EbYjYQ1i7EHBK/giphy.gif")


@bot.command()
async def status(ctx):
    """Voluspa's current operational status"""
    #await ctx.send("https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif")
    #await ctx.send(bot.uptime)
    await ctx.send("// Currently Operational... \n// Rebasing Core Subnets... (WIP)")


@bot.command()
async def dance(ctx):
    await ctx.send("Not quite yet...")

# TODO: This might be a little too mean at times...
# @bot.command()
# async def inspire(ctx):
#     """"Inspirational" quotes from InspiroBot"""
#     req = requests.get('http://inspirobot.me/api?generate=true')
#     logger.info('InspiroBot.me Request Result - req.text: {}'.format(req.text))
#     # TODO: Validate a png with regex
#     # http://generated.inspirobot.me/079/aXm1831xjU.jpg
#     await ctx.send(req.text)


@bot.command()
async def info(ctx):
    """Information about Voluspa"""
    logger.info('ctx: {}'.format(ctx))
    embed = discord.Embed(
        title="Völuspá",
        description="Völuspá the Ghost Proxy Proto-Warmind AI",
        color=0x009933
    )

    # Shows the number of servers the bot is member of.
    embed.add_field(name="Warsats", value=f"{len(bot.guilds)}")

    # give info about you here
    #embed.add_field(name='_ _', value="_Discovered by Mirage ,'}_")
    embed.add_field(name='_ _', value="<:ghost_proxy:455130405398380564>")

    # Logo
    embed.set_image(url="https://raw.githubusercontent.com/RecursiveHook/voluspa-public/master/images/voluspa_white_icon_65.png")

    # give users a link to invite this bot to their server
    # embed.add_field(name="Invite", value="[Invite link](<insert your OAuth invitation link here>)")

    await ctx.send(embed=embed)

# @bot.event
# async def on_command_error(ctx, error):
#     """The event triggered when an error is raised while invoking a command.
#     ctx   : Context
#     error : Exception"""
#     print('ctx: {}\nerror: {}'.format(ctx, error))
#
#     if hasattr(ctx.command, 'on_error'):
#         return
#
#     ignored = (commands.CommandNotFound, commands.UserInputError)
#     error = getattr(error, 'original', error)
#
#     if isinstance(error, ignored):
#         return
#
#     elif isinstance(error, commands.DisabledCommand):
#         return await ctx.send(f'{ctx.command} has been disabled.')
#
#     elif isinstance(error, commands.NoPrivateMessage):
#         try:
#             return await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
#         except:
#             pass
#
#     elif isinstance(error, commands.BadArgument):
#         if ctx.command.qualified_name == 'tag list':
#             return await ctx.send('I could not find that member. Please try again.')
#
#     print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
#     traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


bot.run(config.Discord.api_key)



