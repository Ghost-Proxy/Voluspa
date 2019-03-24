import logging
import random

# import re
# import asyncio
# import requests
# import aiohttp
# from typing import List, Dict, Tuple

import discord
from discord.ext import commands

from voluspa import CONFIG

logger = logging.getLogger('voluspa.cog.DestinyArt')


# async def create_art_embed(title, art_url):
#     art_embed = discord.Embed(
#         title=f'{title}',
#         color=0x009933
#     )
#     art_embed.set_image(url=art_url)
#     return art_embed


class DestinyArt:
    def __init__(self, bot):
        self.bot = bot
        self.base_image_url = f'{CONFIG.Resources.image_bucket_root_url}/destiny-art/'
        self.num_poses = 51
        self.num_dances = 54
        self.num_emotes = 46

        self.poses_info = (
            self.num_poses,
            'poses/d2_pose',
            'Völuspá strikes a pose!'
        )
        self.dances_info = (
            self.num_dances,
            'dances/d2_dance',
            'Völuspá busts a move!'
        )
        self.emotes_info = (
            self.num_emotes,
            'emotes/d2_emote',
            'Völuspá emotes wildly!'
        )

    #url = "https://raw.githubusercontent.com/RecursiveHook/voluspa-public/master/images/voluspa_white_icon_65.png")
    # @commands.command()
    # async def xkcd(self, ctx):
    #     """Display a random XKCD comic :)"""
    #     xkcd_comic = await get_xkcd_comic()
    #     xkcd_embed = discord.Embed(
    #         title=xkcd_comic['safe_title'],
    #         # description=,
    #         color=0x009933,  # rgb(150,168,200)
    #         # footer=xkcd_comic['alt'],
    #         # img=xkcd_comic['img'],
    #         # thumbnail='img'
    #     )
    #     xkcd_embed.set_author(name=f'xkcd #{xkcd_comic["num"]} - {xkcd_comic["date"]}', url=xkcd_comic['url'])
    #     xkcd_embed.set_image(url=xkcd_comic['img'])
    #     xkcd_embed.set_footer(text=xkcd_comic['alt'])
    #     await ctx.send(embed=xkcd_embed)

    async def create_destiny_art_embed(self, num_images, art_type_prefix, title):
        rand_idx = random.randint(1, num_images)
        art_url = f'{art_type_prefix}_{rand_idx}_small_opt.gif'
        logger.info(f'Sending Voluspa DestinyArt: [{art_url}]')
        art_embed = discord.Embed(
            title=title,
            color=0x009933
        )
        art_embed.set_image(url=f'{self.base_image_url}{art_url}')
        return art_embed

    @commands.command()
    async def pose(self, ctx):
        """Strike a pose!"""
        # rand_idx = random.randint(1, self.num_poses)
        # pose_url = f'poses/d2_pose_{rand_idx}.gif'
        # pose_embed = await create_art_embed(
        #     'Voluspa strikes a pose!',
        #     f'{self.base_image_url}{pose_url}'
        # )
        # await ctx.send(embed=pose_embed)
        await ctx.send(embed=await self.create_destiny_art_embed(*self.poses_info))

    @commands.command()
    async def dance(self, ctx):
        """Bust a move!"""
        # rand_idx = random.randint(1, self.num_dances)
        # dance_url = f'dances/d2_dance_{rand_idx}.gif'
        # dance_embed = await create_art_embed(
        #     'Völuspá dances!',
        #     f'{self.base_image_url}{dance_url}'
        # )
        # await ctx.send(embed=dance_embed)
        await ctx.send(embed=await self.create_destiny_art_embed(*self.dances_info))

    @commands.command()
    async def emote(self, ctx):
        """Emote!!"""
        # rand_idx = random.randint(1, self.num_emotes)
        # emote_url = f'emotes/d2_emote_{rand_idx}.gif'
        # emote_embed = await create_art_embed(
        #     'Völuspá emotes!',
        #     f'{self.base_image_url}{emote_url}'
        # )
        # await ctx.send(embed=emote_embed)
        await ctx.send(embed=await self.create_destiny_art_embed(*self.emotes_info))


def setup(bot):
    bot.add_cog(DestinyArt(bot))
