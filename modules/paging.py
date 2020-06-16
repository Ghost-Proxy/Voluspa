import logging
from textwrap import wrap
import asyncio

from modules.custom_embed import default_embed

logger = logging.getLogger('voluspa.module.paging')

class _MenuBase:
    LEFT_ARROW = '\u2b05'
    RIGHT_ARROW = '\u27a1'

    def __init__(self, ctx, title, timeout):
        # Paramaters
        self._ctx = ctx
        self._timeout = timeout

        # Internal
        self._menu_embed = default_embed(title=title)
        self._menu_msg = None
        self._menu_field_index = 0
        self._current_page_index = 0

    async def run(self):
        self._init_menu_embed()
        self._menu_msg = await self._ctx.send(embed=self._menu_embed)
        await self._init_reactions()
        await self._control_loop()

    def _init_menu_embed(self):
        menu_field = self._get_menu_field()
        self._menu_embed.add_field(name=f'Page {self._current_page_index + 1}/{len(self._pages)}', value=menu_field)
        self._menu_field_index = len(self._menu_embed.fields) - 1

    async def _init_reactions(self):
        logger.error('_init_reactions was not overriden.')

    async def _control_loop(self):
        try:
            def check_in_ctx(reaction, user):
                return reaction.message.id == self._menu_msg.id

            while True:
                reaction, user = await self._ctx.bot.wait_for('reaction_add', check=check_in_ctx, timeout=self._timeout)
                if user == self._ctx.message.author:
                    if reaction.emoji == Menu.LEFT_ARROW:
                        await self._set_page(self._current_page_index - 1)
                    elif reaction.emoji == Menu.RIGHT_ARROW:
                        await self._set_page(self._current_page_index + 1)
                if not user.bot:
                    await reaction.remove(user)
        except asyncio.TimeoutError:
            logger.info(f'{self._ctx.message.author} timed out.')
        finally:
            await self._ctx.message.delete()
            await self._menu_msg.delete()

    def _get_menu_field(self):
        logger.error('_get_menu_field was not overriden.')

    async def _set_page(self, page_index):
        page_index %= len(self._pages)
        self._current_page_index = page_index

        menu_field = self._get_menu_field()
        self._menu_embed.set_field_at(self._menu_field_index, name=f'Page {self._current_page_index + 1}/{len(self._pages)}', value=menu_field)

        await self._menu_msg.edit(embed=self._menu_embed)

class Menu(_MenuBase):
    def __init__(self, ctx, title, raw=None, pages=None, max_chars_per_line=64, max_lines_per_page=16, timeout=60.0):
        logger.info(f'{ctx.message.author} created a menu.')

        super().__init__(ctx, title, timeout)

        if raw:
            self._pages = self._split(raw, max_chars_per_line, max_lines_per_page)
        else:
            self._pages = pages

    async def _init_reactions(self):
        await self._menu_msg.add_reaction(_MenuBase.LEFT_ARROW)
        await self._menu_msg.add_reaction(_MenuBase.RIGHT_ARROW)

    def _get_menu_field(self):
        return self._pages[self._current_page_index]

    def _split(self, raw, max_chars_per_line, max_lines_per_page):
        i = 0
        lines = wrap(raw, width=max_chars_per_line)
        pages = []
        while i + max_lines_per_page < len(lines):
            pages.append("\n".join(lines[i:i + max_lines_per_page]))
            i += max_lines_per_page

        if i < len(lines):
            pages.append("\n".join(lines[i:]))

        return pages
