import discord
from discord.ext import tasks, commands
import logging
import asyncio
from modules.external_services.bungie import async_bungie_request_handler
from modules.config import CONFIG
from modules.custom_embed import default_embed

logger = logging.getLogger('voluspa.cog.reminder')


async def get_pending_applications():
    raw_json = await async_bungie_request_handler(f'/GroupV2/{CONFIG.Bungie.clan_group_id}/Members/Pending/')
    return [application['destinyUserInfo']['displayName'] for application in raw_json['Response']['results']]


class RosterReminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reminder_task = bot.loop.create_task(self.roster_reminder())

    def cog_unload(self):
        self.reminder_task.cancel()

    async def roster_reminder(self):
        await self.bot.wait_until_ready()

        feedback_channel = self.bot.get_channel(CONFIG.Voluspa.feedback_channel_id)

        try:
            while not self.bot.is_closed():
                application_list = await get_pending_applications()

                if len(application_list) > 0:
                    logger.info("Sending roster reminder.")
                    description_string = "\n".join(application_list)

                    embed = default_embed(
                        title="Pending Applications",
                        description=description_string
                    )

                    await feedback_channel.send(embed=embed)

                await asyncio.sleep(14400)
        except asyncio.CancelledError:
            raise
        except (OSError, discord.ConnectionClosed):
            self.reminder_task.cancel()
            self.reminder_task = self.bot.loop.create_task(self.roster_reminder())

    @commands.command(name='restart-reminder')
    async def task_restart(self, ctx):
        self.reminder_task.cancel()
        self.reminder_task = self.bot.loop.create_task(self.roster_reminder())

def setup(bot):
    bot.add_cog(RosterReminder(bot))
