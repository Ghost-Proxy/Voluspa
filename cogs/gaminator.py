import logging

from cogs.config.roles import ROLES
from modules.custom_embed import default_embed
from modules.emoji_utils import ri_at_index, ri_alphabet

from discord.ext import commands

EMBED_MAX_LINES = 7
logger = logging.getLogger('voluspa.cog.gaminator')

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

class Gaminator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='other-games')
    async def other_games(self, ctx):
        formatted_roles_dict = format_roles_dict(ROLES['other_games'])
        pages = page_dict_as_lines(formatted_roles_dict)

        current_page_num = 0
        num_pages = len(pages)
        current_page_dict = get_current_page_dict(pages[current_page_num]) # Gets a dict indexed by emoji

        menu_embed = default_embed(title=f'Other Games {current_page_num + 1}/{num_pages}')
        role_embed = default_embed(title='Your Roles')
        role_embed.add_field(name='Adding', value='None')
        role_embed.add_field(name='Removing', value='None')

        menu_msg = await ctx.send(embed=menu_embed)
        role_msg = await ctx.send(embed=role_embed)
        await set_page(current_page_dict, menu_msg, current_page_num, num_pages)

        roles_to_add = []
        roles_to_remove = []

        while True:
            payload = await self.bot.wait_for('reaction_add', timeout=60.0)

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
                        
                else:
                    if current_page_dict[payload[0].emoji] not in roles_to_add:
                        roles_to_add.append(current_page_dict[payload[0].emoji])
                    else:
                        roles_to_add.remove(current_page_dict[payload[0].emoji])

def setup(bot):
    bot.add_cog(Gaminator(bot))
