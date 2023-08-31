# pylint: disable=too-few-public-methods
"""Secret debug console via Jishaku"""

from discord.ext import commands

# from jishaku.cog import Jishaku
# from jishaku.features.python import PythonFeature
# from jishaku.features.root_command import RootCommand
from jishaku.cog import STANDARD_FEATURES, OPTIONAL_FEATURES

class CustomDebugCog(*OPTIONAL_FEATURES, *STANDARD_FEATURES):
    """Jishaku Debug Cog"""


async def setup(bot: commands.Bot):
    """Cog Setup"""
    await bot.add_cog(CustomDebugCog(bot=bot))
