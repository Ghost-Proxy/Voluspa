import logging

from cogs.config.roles import ROLES
<<<<<<< HEAD
from modules.custom_embed import default_embed
from modules.emoji_utils import ri_at_index, ri_alphabet

from discord.ext import commands

EMBED_MAX_LINES = 7
logger = logging.getLogger('voluspa.cog.gaminator')

def role_dict_list_to_role_ping_list(role_dict_list):
    role_names = []

    for d in role_dict_list:
        role_names.append('`@' + d['role-name'] + '`')

    return role_names

def get_current_page_dict(page):
    ret = {}
    for i in range(len(page)):
        ret[ri_at_index(i)] = {'role-name': list(page)[i], 'qualified-name': page[list(page)[i]]}

    return ret

async def set_page(current_page_dict, menu_msg, current_page_num, num_pages):
    menu_description = ''
    for k, v in current_page_dict.items():
        menu_description += k + ' - `@' + v['role-name'] + '` - ' + v['qualified-name'] + '\n'

    menu_embed = default_embed(title=f'Other Games {current_page_num + 1}/{num_pages}', description=menu_description)

    await menu_msg.clear_reactions()
    await menu_msg.edit(embed=menu_embed)

    if current_page_num > 0:
        await menu_msg.add_reaction('\u2b05') # Left arrow

    for k in current_page_dict.keys():
        await menu_msg.add_reaction(k)

    if current_page_num < num_pages - 1:
        await menu_msg.add_reaction('\u27a1') # Right arrow

    await menu_msg.add_reaction('\u2705') # Check mark

def page_dict_as_lines(d, max_lines=EMBED_MAX_LINES):
    pages = []
    current_page = {}
    current_line = 0
    for k, v in d.items():
        if current_line % max_lines == 0 and current_line > 0:
            pages.append(current_page)
            current_page = {}
        current_page[k] = v
        current_line += 1

    return pages

def format_roles_dict(raw):
    ret = {}

    for k, v in raw.items():
        ret[k] = v[0].title()

    return ret
=======
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
>>>>>>> b98dacf3841f966582bb0bbe1a2862e70874c165

class Gaminator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='other-games')
    async def other_games(self, ctx):
<<<<<<< HEAD
        formatted_roles_dict = format_roles_dict(ROLES['other_games'])
        pages = page_dict_as_lines(formatted_roles_dict)

        current_page_num = 0
        num_pages = len(pages)
        current_page_dict = get_current_page_dict(pages[current_page_num]) # Gets a dict indexed by emoji

        menu_embed = default_embed(title=f'Other Games {current_page_num + 1}/{num_pages}')
        role_embed = default_embed(title='Your Roles')
        role_embed.add_field(name='Adding', value='None')
        role_embed.add_field(name='Removing', value='None')

        role_msg = await ctx.send(embed=role_embed)
        menu_msg = await ctx.send(embed=menu_embed)
        await set_page(current_page_dict, menu_msg, current_page_num, num_pages)

        roles_to_add = []
        roles_to_remove = []
=======
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
>>>>>>> b98dacf3841f966582bb0bbe1a2862e70874c165

        while True:
            payload = await self.bot.wait_for('reaction_add', timeout=60.0)

<<<<<<< HEAD
            if payload[0].emoji == '\u2b05' and current_page_num > 0:
                current_page_num -= 1
                current_page_dict = get_current_page_dict(pages[current_page_num])
                await set_page(current_page_dict, menu_msg, current_page_num, num_pages)
            elif payload[0].emoji == '\u27a1' and current_page_num < num_pages - 1:
                current_page_num += 1
                current_page_dict = get_current_page_dict(pages[current_page_num])
                await set_page(current_page_dict, menu_msg, current_page_num, num_pages)
            elif payload[0].emoji in [e for e in ri_alphabet(len(current_page_dict))]:
                await payload[0].remove(payload[1])

                if current_page_dict[payload[0].emoji]['role-name'] in [role.name for role in payload[1].roles]:
                    if current_page_dict[payload[0].emoji] not in roles_to_remove:
                        roles_to_remove.append(current_page_dict[payload[0].emoji])
                    else:
                        roles_to_remove.remove(current_page_dict[payload[0].emoji])

                    roles_to_remove_field = "\n".join(role_dict_list_to_role_ping_list(roles_to_remove))
                    role_embed.set_field_at(1, name='Removing', value=('None' if len(roles_to_remove) == 0 else roles_to_remove_field))
                    await role_msg.edit(embed=role_embed)
                else:
                    if current_page_dict[payload[0].emoji] not in roles_to_add:
                        roles_to_add.append(current_page_dict[payload[0].emoji])
                    else:
                        roles_to_add.remove(current_page_dict[payload[0].emoji])

                    roles_to_add_field = "\n".join(role_dict_list_to_role_ping_list(roles_to_add))
                    role_embed.set_field_at(0, name='Adding', value=('None' if len(roles_to_add) == 0 else roles_to_add_field))
                    await role_msg.edit(embed=role_embed)
=======
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


>>>>>>> b98dacf3841f966582bb0bbe1a2862e70874c165

def setup(bot):
    bot.add_cog(Gaminator(bot))
