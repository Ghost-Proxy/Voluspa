import logging
import asyncio

from cogs.config.roles import ROLES
from modules.custom_embed import default_embed
from modules.emoji_utils import ri_alphabet, ri_at_index

from discord.ext import commands

logger = logging.getLogger('voluspa.cog.gaminator')

EMBED_MAX_LINES = 8
LEFT_ARROW = '\u2b05'
CHECK_MARK = '\u2705'
RIGHT_ARROW = '\u27a1'

def role_dict_list_to_role_ping_list(role_dict_list):
    role_names = []

    for d in role_dict_list:
        role_names.append('`@' + d['role-name'] + '`')

    return role_names

async def update_roles_to_add(reaction, user, current_page_dict, roles_to_add):
    if current_page_dict[reaction.emoji] not in roles_to_add:
        roles_to_add.append(current_page_dict[reaction.emoji])
    else:
        roles_to_add.remove(current_page_dict[reaction.emoji])

    return roles_to_add, 0

async def update_roles_to_remove(reaction, user, current_page_dict, roles_to_remove):
    if current_page_dict[reaction.emoji] not in roles_to_remove:
        roles_to_remove.append(current_page_dict[reaction.emoji])
    else:
        roles_to_remove.remove(current_page_dict[reaction.emoji])

    return roles_to_remove, 1

def get_menu_field(current_page_dict):
    menu_field = ''
    for k, v in current_page_dict.items():
        menu_field += k + ' - `@' + v['role-name'] + '` - ' + v['qualified-name'] + '\n'

    return menu_field

async def set_page(ctx, current_page_dict, menu_embed, num_pages, current_page_num, menu_msg):
    menu_field = get_menu_field(current_page_dict)
    menu_embed.set_field_at(2, name=f'Page {current_page_num + 1}/{num_pages}', value=menu_field, inline=False)
    await menu_msg.edit(embed=menu_embed)

    menu_msg = await ctx.fetch_message(menu_msg.id)

    last_index = len(current_page_dict) - 1 + 3
    current_index = len(menu_msg.reactions) - 1
    if current_index < last_index:
        current_index += 1
        while current_index <= last_index:
            await menu_msg.add_reaction(ri_at_index(current_index - 3))
            current_index += 1
    elif current_index > last_index:
        while current_index > last_index:
            await menu_msg.remove_reaction(ri_at_index(current_index - 3), ctx.bot.user)
            current_index -= 1

async def init_menu(ctx, current_page_dict, menu_embed, num_pages):
    menu_field = get_menu_field(current_page_dict)

    menu_embed.add_field(name='Adding', value='None')
    menu_embed.add_field(name='Removing', value='None')
    menu_embed.add_field(name=f'Page 1/{num_pages}', value=menu_field, inline=False)

    menu_msg = await ctx.send(embed=menu_embed)

    await menu_msg.add_reaction(LEFT_ARROW)
    await menu_msg.add_reaction(CHECK_MARK)
    await menu_msg.add_reaction(RIGHT_ARROW)

    for k in current_page_dict.keys():
        await menu_msg.add_reaction(k)

    return menu_msg

def get_current_page_dict(page):
    ret = {}
    for i in range(len(page)):
        ret[ri_at_index(i)] = {'role-name': list(page)[i], 'qualified-name': page[list(page)[i]]}

    return ret

def page_dict_as_lines(d, max_lines=EMBED_MAX_LINES):
    if max_lines > 17:
        max_lines = 17
    elif max_lines < 2:
        max_lines = 2

    pages = []
    current_page = {}
    current_line = 0
    for k, v in d.items():
        if current_line % max_lines == 0 and current_line > 0:
            pages.append(current_page)
            current_page = {}
        current_page[k] = v
        current_line += 1

    if len(current_page) > 0:
        pages.append(current_page)

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
        logger.info(f'{ctx.message.author} called other_games')

        formatted_roles_dict = format_roles_dict(ROLES['other_games'])
        pages = page_dict_as_lines(formatted_roles_dict)
        num_pages = len(pages)

        current_page_num = 0
        current_page_dict = get_current_page_dict(pages[current_page_num]) # Gets a dict indexed by emoji

        menu_embed = default_embed(title=f'Other Games')
        menu_msg = await init_menu(ctx, current_page_dict, menu_embed, num_pages)

        roles_to_add = []
        roles_to_remove = []

        try:
            while True:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0)

                if user == ctx.message.author:
                    if reaction.emoji == LEFT_ARROW or reaction.emoji == RIGHT_ARROW:
                        await reaction.remove(user)
                        i = -1 if reaction.emoji == LEFT_ARROW else 1
                        current_page_num = (current_page_num + i) % num_pages
                        current_page_dict = get_current_page_dict(pages[current_page_num])
                        await set_page(ctx, current_page_dict, menu_embed, num_pages, current_page_num, menu_msg)
                    elif reaction.emoji == CHECK_MARK:
                        autorole = self.bot.get_cog('Autorole')
                        await autorole.other_game_add(ctx, *[role['qualified-name'] for role in roles_to_add])
                        await autorole.other_game_remove(ctx, *[role['qualified-name'] for role in roles_to_remove])
                        break
                    elif reaction.emoji in [e for e in ri_alphabet(len(current_page_dict))]:
                        await reaction.remove(user)
                        if current_page_dict[reaction.emoji]['role-name'] not in [role.name for role in user.roles]:
                            update_list, field_index = await update_roles_to_add(reaction, user, current_page_dict, roles_to_add)
                        else:
                            update_list, field_index = await update_roles_to_remove(reaction, user, current_page_dict, roles_to_remove)
                        update_field = '\n'.join(role_dict_list_to_role_ping_list(update_list))
                        menu_embed.set_field_at(field_index, name=('Adding' if field_index == 1 else 'Removing'), value=('None' if len(update_list) == 0 else update_field))
                        await menu_msg.edit(embed=menu_embed)
                elif not user.bot:
                    await reaction.remove(user)
        except asyncio.TimeoutError:
            logger.info(f'{ctx.message.author} timed out.')
        finally:
            await ctx.message.delete()
            await menu_msg.delete()

def setup(bot):
    bot.add_cog(Gaminator(bot))
