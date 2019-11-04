import logging

import discord
from discord.ext import commands

from voluspa import CONFIG

logger = logging.getLogger('voluspa.cog.feedback')


class Feedback(commands.Cog):
    """Helpful utility functions"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['f'])
    @commands.cooldown(2, 1800, type=commands.cooldowns.BucketType.user)  # 2 uses permitted in case a mistake is made
    async def feedback(self, ctx, *, message):
        """Sends an anonymous feedback message

        You can write your message across multiple lines
        Sign your message if you would like to be contacted for follow-up"""
        feedback_channel = ctx.bot.get_channel(CONFIG.Voluspa.feedback_channel_id)
        await feedback_channel.send("Incoming message for the Vanguard:\n>>> " + message)

        if isinstance(ctx.message.channel, discord.abc.GuildChannel):
            await ctx.send(
                "Your feedback has been sent. These messages will self-destruct in one minute.",
                delete_after=60
            )
            await ctx.message.delete(delay=60)
        else:
            await ctx.send("Your feedback has been sent.")

        logger.info('Feedback has been sent.')


def setup(bot):
    bot.add_cog(Feedback(bot))
