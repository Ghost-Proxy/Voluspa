"""Shared UI elements"""

from github import Github

import discord

from modules.config import CONFIG


class FeedbackModal(discord.ui.Modal, title="Feedback"):
    """Creates and handles a Feedback Modal"""
    feedback = discord.ui.TextInput(label="Enter your feedback here:", style=discord.TextStyle.long)

    async def on_submit(self, interaction: discord.Interaction): # pylint: disable=arguments-differ
        """Submits the modal"""
        feedback_channel = interaction.client.get_channel(CONFIG['Voluspa']['feedback_channel_id'])
        await feedback_channel.send(f"Incoming message for the Vanguard:\n>>> {self.children[0].value}")
        await interaction.response.send_message(content="Your feedback has been sent.", ephemeral=True)

class IssueModal(discord.ui.Modal, title="New Github Issue"):
    """Creates and handles a GitHub Issue Modal"""
    issue_title = discord.ui.TextInput(label="Issue Title", style=discord.TextStyle.short)
    body = discord.ui.TextInput(label="Issue Body", style=discord.TextStyle.long)

    async def on_submit(self, interaction: discord.Interaction): # pylint: disable=arguments-differ
        """Submits the modal"""
        ghub = Github(CONFIG['Github']['token'])
        repo = ghub.get_repo(CONFIG['Github']['repo_name'])
        issue = repo.create_issue(title=str(self.issue_title), body=str(self.body))

        await interaction.response.send_message(
            content=f'Your issue has been created _([#{issue.number}]({issue.html_url}))_',
            ephemeral=True
            )
