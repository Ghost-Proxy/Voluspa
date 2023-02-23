import logging
from github import Github

from modules.ui_elements import FeedbackModal
from modules.config import CONFIG

import discord
from discord.ext import commands

logger = logging.getLogger('voluspa.cog.feedback')

class Feedback(commands.Cog):
    """Feedback System"""
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @discord.app_commands.command()
    @discord.app_commands.checks.cooldown(1, 1800.0)
    @discord.app_commands.checks.has_role('ghost-proxy-vanguard')
    async def issue(self, interaction: discord.Interaction, title: str, body: str) -> None:
        """Creates an issue in the Voluspa Github repository"""
        g = Github(CONFIG.Github.token)
        repo = g.get_repo(CONFIG.Github.repo_name)
        issue = repo.create_issue(title=title, body=body)

        await interaction.response.send_message(content=f'Your issue has been created _([#{issue.number}]({issue.html_url}))_', ephemeral=True)

    @discord.app_commands.command()
    @discord.app_commands.checks.cooldown(2, 1800.0) # 2 uses permitted in case a mistake is made
    async def feedback(self, interaction: discord.Interaction) -> None:
        """Sends anonymous feedback to @ghost-proxy-vanguard."""

        await interaction.response.send_modal(FeedbackModal())

        logger.info('Feedback has been sent.')

async def setup(bot):
    await bot.add_cog(Feedback(bot))
