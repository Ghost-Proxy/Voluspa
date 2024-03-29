"""Systems Cog"""

import logging
import datetime

import discord
from discord.ext import commands

from voluspa import CONFIG
from modules.custom_embed import default_embed


logger = logging.getLogger('voluspa.cog.systems')


def get_bot_uptime(bot, *, brief=False):
    """Gets bot uptime stats"""
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
    """Systems Cog"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def info(self, ctx):
        """Information about Voluspa"""
        logger.info('ctx: %s', ctx)
        embed = discord.Embed(
            title="Völuspá",
            description="The Ghost Proxy Proto-Warmind AI <:ghost_proxy:455130405398380564>",
            color=0x009933
        )

        # Shows the number of servers the bot is member of.
        embed.add_field(name="Warsats", value=f"{len(self.bot.guilds)}")
        embed.add_field(name='Version', value=CONFIG['Voluspa']['version'])
        # embed.add_field(name='SHA', value=CONFIG.Voluspa.sha, inline=False)
        embed.add_field(name='Boot Time', value=CONFIG['Voluspa']['boot_time'], inline=False)
        embed.add_field(name='Uptime', value=f'{get_bot_uptime(self.bot)}', inline=False)
        embed.add_field(name='Developers', value='Mirage\nOxy\nStevenNic\nWindows98', inline=False)

        # give info about you here
        # embed.add_field(name='_ _', value="_Discovered by Mirage ,'}_")
        # embed.add_field(name='_ _', value="<:ghost_proxy:455130405398380564>")

        # Logo
        #embed.set_image(url=f"{CONFIG.Resources.image_bucket_root_url}/voluspa/Voluspa_icon_64x48.png")
        embed.set_thumbnail(url=f"{CONFIG['Resources']['image_bucket_root_url']}/voluspa/Voluspa_icon_64x48.png")

        embed.set_footer(
            text='via Völuspá with \u2764',
            icon_url=f"{CONFIG['Resources']['image_bucket_root_url']}/voluspa/Voluspa_icon_64x64.png"
        )
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
        """Voluspa's latency to Discord"""
        async with ctx.typing():
            # latencies = []
            # for _ in range(0, 5):
            #     latencies.append(self.bot.latency)
            #     await asyncio.sleep(1)
            # lat_results = ["_Ping #{} -- {:.3f} secs ({:.0f} ms)_".format(i + 1, p, p * 1000)
            #                for i, p in enumerate(latencies)]
            # mean_latency = statistics.mean(latencies)
            # msg = "**Latency Results**\n{}\n---\nAvg: {:.3f} secs ({:.0f} ms)".format(
            #     '\n'.join(lat_results),
            #     mean_latency,
            #     mean_latency * 1000
            # )
            # "Latency: {:.3f} secs ({:.0f} ms)".format(latency, latency * 1000)
            discord_latency = self.bot.latency
            msg = "**Latency Result:**\n\n" \
                  f"_Ping of {discord_latency:.3f} secs ({discord_latency * 1000:.0f} ms)_"
        confirm_embed = default_embed(
            title='Völuspá to Discord latency',
            description=f'\n{msg}'
        )
        await ctx.send(embed=confirm_embed)


async def setup(bot):
    """Cog Setup"""
    await bot.add_cog(Systems(bot))
