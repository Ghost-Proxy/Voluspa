from discord.ext import commands
from jishaku.cog import JishakuBase, jsk
from jishaku.metacog import GroupCogMeta


@commands.group(alias=['>'])
async def jk(self, ctx):
    pass


class Console(JishakuBase, metaclass=GroupCogMeta, command_parent=jk):
    pass


def setup(bot: commands.Bot):
    bot.add_cog(Console(bot))
