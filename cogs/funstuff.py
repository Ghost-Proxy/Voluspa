import asyncio
import logging
import re
from random import randint

from modules.fun import Quotes, RandomQuotes, get_xkcd_comic
from modules.custom_embed import default_embed

import discord
from discord.ext import commands

quotes = Quotes()
random_quotes = RandomQuotes()

logger = logging.getLogger('voluspa.cog.funstuff')

REAL_DICE = ['d4', 'd6', 'd8', 'd10', 'd12', 'd20']
REGEX_NUMERICAL = '[0-9]+'

class FunStuff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=REAL_DICE)
    async def roll(self, ctx, *dice):
        """Random number utilities"""
        d = 20
        if ctx.invoked_with in REAL_DICE:
            d = int(ctx.invoked_with[1:])
        elif dice:
            d_str = re.findall(REGEX_NUMERICAL, ' '.join(dice))
            if d_str:
                d = int(d_str[0])
            else:
                raise commands.UserInputError
        msg = f'You rolled a d{d}, It landed on {randint(1, d)}!'
        await ctx.send(msg)

    @commands.command()
    async def hello(self, ctx):
        """Say hello to Voluspa"""
        logger.info('CTX INFO: {}'.format(ctx))
        await ctx.send(await quotes.pick_quote('greetings', ctx.message.author.mention))

    @commands.command()
    async def goodbye(self, ctx):
        """Say goodbye to Voluspa"""
        logger.info('CTX INFO: {}'.format(ctx))
        await ctx.send(await quotes.pick_quote('goodbyes', ctx.message.author.mention))

    @commands.command()
    async def xkcd(self, ctx):
        """Display a random XKCD comic :)"""
        xkcd_comic = await get_xkcd_comic()
        xkcd_embed = discord.Embed(
            title=xkcd_comic['safe_title'],
            # description=,
            color=0x96A8C8,  # rgb(150,168,200)
            # footer=xkcd_comic['alt'],
            # img=xkcd_comic['img'],
            # thumbnail='img'
        )
        xkcd_embed.set_author(name=f'xkcd #{xkcd_comic["num"]} - {xkcd_comic["date"]}', url=xkcd_comic['url'])
        xkcd_embed.set_image(url=xkcd_comic['img'])
        xkcd_embed.set_footer(text=xkcd_comic['alt'])
        await ctx.send(embed=xkcd_embed)

    @commands.command()
    async def random(self, ctx):
        """Random things from the net..."""
        rand_quote = await random_quotes.get_random_quote()
        await ctx.send(rand_quote)

    # TODO: This might be a little too mean at times...
    # @commands.command()
    # async def inspire(self, ctx):
    #     """"Inspirational" quotes from InspiroBot"""
    #     req = requests.get('http://inspirobot.me/api?generate=true')
    #     logger.info('InspiroBot.me Request Result - req.text: {}'.format(req.text))
    #     # TODO: Validate a png with regex
    #     # http://generated.inspirobot.me/079/aXm1831xjU.jpg
    #     await ctx.send(req.text)


def setup(bot):
    bot.add_cog(FunStuff(bot))
