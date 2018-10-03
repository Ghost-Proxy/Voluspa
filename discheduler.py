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

# Custom Imports
from modules.misc import merge_dicts, AttrDict
from modules.fun import Quotes, RandomQuotes, get_xckd_comic
from modules.database import Database

# Third-Party Imports
import fuzzyset
import discord
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


    #await ctx.send("{}".format(msg))
    #await send_multipart_msg(ctx, msg1)
    #await send_multipart_msg(ctx, msg2)
    #await send_multipart_msg(ctx, msg3)
    await send_multipart_msg(ctx, msg_final)


#async \
def get_bungie_member_list():
    member_list_url = "https://www.bungie.net/platform/GroupV2/{}/Members/".format(config.Bungie.clan_group_id)
    r = requests.get(member_list_url, headers={'X-API-Key': config.Bungie.api_key})
    raw_json = r.json()
    bungie_results = raw_json['Response']
    member_results = bungie_results['results']
    num_members = raw_json['Response']['totalResults']
    member_list = [member['destinyUserInfo']['displayName'] for member in member_results]
    return num_members, member_list


def filter_members_by_field(member_dict, field_name):
    return {member_id: {'name': member_info['display_name'], field_name: member_info.get(field_name, None)} for member_id, member_info in member_dict.items()}


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

bot.run(config.Discord.api_key)



