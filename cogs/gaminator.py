import logging

from cogs.config.roles import ROLES
from modules.misc import chunk_list
from modules.custom_embed import default_embed

from discord.ext import commands

logger = logging.getLogger('voluspa.cog.gaminator')

async def set_page(page, chunked_lines, result_msg):
    description_string = ''
    react_char = '\U0001f1e6'
    for line in chunked_lines[page]:
        description_string += react_char + ' - ' + line + '\n'
        react_char = chr(ord(react_char) + 1)

    result_embed = default_embed(
        title='Other Games',
        description=description_string
    )

    await result_msg.clear_reactions()
    await result_msg.edit(embed=result_embed)

    if page > 0:
        await result_msg.add_reaction('\u2b05')

    react_char = '\U0001f1e6'
    for i in range(0, len(chunked_lines[page])):
        await result_msg.add_reaction(react_char)
        react_char = chr(ord(react_char) + 1)

    if page < len(chunked_lines) - 1:
        await result_msg.add_reaction('\u27a1')
    await result_msg.add_reaction('\u2705')

def chunk_lines(lines, max_lines=7):
    if max_lines < 0:
        max_lines = 0

    chunks = []

    curr_line = 0
    curr_chunk = []
    for line in lines:
        if curr_line % max_lines == 0 and curr_line > 0:
            chunks.append(curr_chunk)
            curr_chunk = []
        curr_chunk.append(line)
        curr_line += 1

    if len(curr_chunk) > 0:
        chunks.append(curr_chunk)

    return chunks

class Gaminator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='other-games')
    async def other_games(self, ctx):
        og_dict = ROLES['other_games']
        og_list = []

        for k, v in og_dict.items():
            og_list.append('`@' + k + '` - ' + v[0].title())

        chunked_lines = chunk_lines(og_list)

        base_embed = default_embed(
            title='Other Games'
        )
        add_embed = default_embed(
            title='You Will Add'
        )

        result_msg = await ctx.send(embed=base_embed)
        add_msg = await ctx.send(embed=add_embed)

        page = 0
        await set_page(page, chunked_lines, result_msg)

        while True:
            payload = await self.bot.wait_for('reaction_add', timeout=60.0)

            if payload[1].id != ctx.message.author.id:
                continue

            if payload[0].emoji == '\u2b05': # left arrow
                if page > 0:
                    page -= 1
                    await set_page(page, chunked_lines, result_msg)
            elif payload[0].emoji == '\u27a1': # right arrow
                if page < len(chunked_lines) - 1:
                    page += 1
                    await set_page(page, chunked_lines, result_msg)



def setup(bot):
    bot.add_cog(Gaminator(bot))
