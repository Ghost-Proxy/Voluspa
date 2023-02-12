from modules.config import CONFIG

import discord

class FeedbackModal(discord.ui.Modal, title="Feedback"):
    feedback = discord.ui.TextInput(label="Enter your feedback here:", style=discord.TextStyle.long)

    async def on_submit(self, interaction: discord.Interaction):
        feedback_channel = interaction.client.get_channel(CONFIG.Voluspa.feedback_channel_id)
        await feedback_channel.send(f"Incoming message for the Vanguard:\n>>> {self.children[0].value}")
        await interaction.response.send_message(content="Your feedback has been sent.", ephemeral=True)
