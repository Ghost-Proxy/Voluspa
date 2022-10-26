import logging

import discord
from discord import app_commands
from discord.ext import commands

from voluspa import CONFIG

logger = logging.getLogger('voluspa.cog.feedback')


class Feedback(commands.Cog):
    """Feedback System"""
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command()
    @app_commands.choices(anonymous=[
        app_commands.Choice(name='Yes',value=1),
        app_commands.Choice(name='No',value=0)
    ])
    @app_commands.checks.cooldown(2, 1800.0) # 2 uses permitted in case a mistake is made
    async def feedback(self, interaction: discord.Interaction, message: str, anonymous: app_commands.Choice[int]) -> None:
        """Sends feedback to @ghost-proxy-vanguard. Can be signed or anonymous."""
        feedback_channel = self.bot.get_channel(CONFIG.Voluspa.feedback_channel_id)
        await feedback_channel.send(f"Incoming message for the Vanguard:\n>>> {message}{'' if anonymous.value == 1 else f' _(sent by {interaction.user.name}#{interaction.user.discriminator}_)'}")

        await interaction.response.send_message(
            f"Your feedback has been sent {'anonymously' if anonymous.value == 1 else 'with your signature'}.",
            ephemeral=True
        )

        logger.info('Feedback has been sent.')


async def setup(bot):
    await bot.add_cog(Feedback(bot))
