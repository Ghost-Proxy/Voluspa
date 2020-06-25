import asyncio

from modules.config import CONFIG

import discord
from discord.ext import commands

COC_STRING = f"""
--\u005c\u005c\u005c\u005c//--
Reminder: this is an NSFW channel, but the code of conduct still applies. Check yourself against the following before posting.

_No intolerant, offensive, sexist, racist, bigoted, homophobic, transphobic, xenophobic, harassing, inflammatory, derogatory, and/or toxic language or behavior is allowed._

_Have a good sense of humor. However, know your audience and what is appropriate. It is always better to err on the side of caution. And the best jokes are not at the expense of others. :)_

_Remember, you are a representative of our group and by extension all of us, so always be and set a good example._

_If it is not extreme, pornographic, or against the Rules and CoC, feel free to post NSFW things (err on the side of caution if possible)._

_Acceptable NSFW content are things that would potentially contain objectionable language or content/topics (like R-rated), however anything that is out-right pornographic or vile in nature is not allowed. Try to keep it classy._

\u005c\u005c\u005c\u005c KETCHUP LIMIT \u005c MAX INT \u005c
"""

class BackgroundTasks(commands.Cog):
    def __init__(self, bot):
        self._bot = bot
        self._coc_reminder_task = bot.loop.create_task(self.coc_reminder())

    def cog_unload(self):
        self._coc_reminder_task.cancel()

    async def coc_reminder(self):
        await self._bot.wait_until_ready()

        nsfw_channel = self._bot.get_channel(CONFIG.Voluspa.nsfw_channel_id)

        try:
            while not self._bot.is_closed():
                await nsfw_channel.send(COC_STRING)
                await asyncio.sleep(5)
        except asyncio.CancelledError:
            raise
        except (OSError, discord.ConnectionClosed):
            self._coc_reminder_task.cancel()
            self._coc_reminder_task = self._bot.loop.create_task(self._coc_reminder_task())

def setup(bot):
    bot.add_cog(BackgroundTasks(bot))
