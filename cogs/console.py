"""Secret debug console via Jishaku"""

from discord.ext import commands
from jishaku.cog import JishakuBase, jsk
from jishaku.metacog import GroupCogMeta


@commands.group(alias=['>'])
async def jk(self, ctx):
    """Jishaku command"""


class Console(JishakuBase, metaclass=GroupCogMeta, command_parent=jk):
    """Jishaku console"""


async def setup(bot: commands.Bot):
    """Cog Setup"""
    await bot.add_cog(Console(bot))
