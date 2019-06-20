import time
import logging
import datetime
import statistics

from voluspa import CONFIG, VOLUSPA_VERSION, VOLUSPA_SHA

import discord
from discord.ext import commands

logger = logging.getLogger('voluspa.cog.systems')


def get_bot_uptime(bot, *, brief=False):
    now = datetime.datetime.utcnow()
    delta = now - bot.uptime
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)

    if not brief:
        if days:
            fmt = '{d} days, {h} hours, {m} minutes, and {s} seconds'
        else:
            fmt = '{h} hours, {m} minutes, and {s} seconds'
    else:
        fmt = '{h}h {m}m {s}s'
        if days:
            fmt = '{d}d ' + fmt

    return fmt.format(d=days, h=hours, m=minutes, s=seconds)


class Systems(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def info(self, ctx):
        """Information about Voluspa"""
        logger.info('ctx: {}'.format(ctx))
        embed = discord.Embed(
            title="Völuspá",
            description="The Ghost Proxy Proto-Warmind AI <:ghost_proxy:455130405398380564>",
            color=0x009933
        )

        # Shows the number of servers the bot is member of.
        embed.add_field(name="Warsats", value=f"{len(self.bot.guilds)}")

        embed.add_field(name='Version', value=VOLUSPA_VERSION, inline=False)
        # embed.add_field(name='SHA', value=VOLUSPA_SHA, inline=False)
        embed.add_field(name='Boot Time', value=CONFIG.Voluspa.boot_time)

        # give info about you here
        # embed.add_field(name='_ _', value="_Discovered by Mirage ,'}_")
        # embed.add_field(name='_ _', value="<:ghost_proxy:455130405398380564>")
        embed.add_field(name='Uptime', value=f'{get_bot_uptime(self.bot)}', inline=False)

        # Logo
        embed.set_image(url=f"{CONFIG.Resources.image_bucket_root_url}/voluspa/Voluspa_icon_64x48.png")

        # give users a link to invite this bot to their server
        # embed.add_field(name="Invite", value="[Invite link](<insert your OAuth invitation link here>)")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def uptime(self, ctx):
        """Voluspa's uptime"""
        await ctx.send(f'Uptime: **{get_bot_uptime(self.bot)}**')

    @commands.command()
    async def status(self, ctx):
        """Voluspa's current status"""
        # await ctx.send("https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif")
        # await ctx.send(bot.uptime)
        await ctx.send("\n// Currently Operational... \n// Rebasing Core Subnets... (WIP)")

    @commands.command()
    async def ping(self, ctx):
        """Voluspa's latency"""
        async with ctx.typing():
        # Get the latency of the bot
        # latency = bot.latency  # Included in the Discord.py library

            # async def get_latency():
            #     d_client = discord.Client()
            #     time.sleep(5)
            #     lat = d_client.latency
            #     await d_client.close()
            #     return lat
            # TODO: Fix?
            # latencies = [await get_latency() for _ in range(0, 1)]
            latencies = [self.bot.latency for _ in range(0, 1)]
            lat_results = ["\t_Ping #{} -- {:.3f} secs ({:.0f} ms)_".format(i + 1, p, p * 1000)
                           for i, p in enumerate(latencies)]
            mean_latency = statistics.mean(latencies)
            msg = "---\nLatency Results **(WIP)**:\n{}\n---\nAvg: {:.3f} secs ({:.0f} ms)".format(
                '\n'.join(lat_results),
                mean_latency,
                mean_latency * 1000
            )
        # "Latency: {:.3f} secs ({:.0f} ms)".format(latency, latency * 1000)
        # Send it to the user
        await ctx.send(msg)


def setup(bot):
    bot.add_cog(Systems(bot))
