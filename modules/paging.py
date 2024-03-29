# pylint: disable=too-few-public-methods
"""Logging Module"""

import logging
import asyncio
from textwrap import wrap

from emoji import emojize

from modules.custom_embed import default_embed
from modules.emoji_utils import ri_at_index, ri_alphabet, index_of_ri, normalize


logger = logging.getLogger('voluspa.module.paging')


class _MenuBase:
    LEFT_ARROW = '\u2b05'
    CHECK_MARK = '\u2705'
    RIGHT_ARROW = '\u27a1'

    def __init__(self, ctx, title, pages, timeout):
        logger.info('%s created a menu.', ctx.message.author)

        # Paramaters
        self._ctx = ctx
        self._pages = pages
        self._timeout = timeout

        # Internal
        self._menu_embed = default_embed(title=title)
        self._menu_msg = None
        self._menu_field_index = 0
        self._current_page_index = 0

    async def run(self):
        """Run the page"""
        self._init_menu_embed()
        self._menu_msg = await self._ctx.send(embed=self._menu_embed)
        await self._init_reactions()
        await self._control_loop()

    async def _init_reactions(self):
        """Empty stub for override"""

    def _init_menu_embed(self):
        menu_field = self._get_menu_field()
        self._menu_embed.add_field(
            name=f'Page {self._current_page_index + 1}/{len(self._pages)}',
            value=menu_field,
            inline=False
            )
        self._menu_field_index = len(self._menu_embed.fields) - 1

    async def _control_loop(self):
        try:
            def check_in_ctx(reaction):
                return reaction.message.id == self._menu_msg.id

            while True:
                reaction, user = await self._ctx.bot.wait_for('reaction_add', check=check_in_ctx, timeout=self._timeout)
                if user == self._ctx.message.author:
                    if reaction.emoji == Menu.LEFT_ARROW and len(self._pages) > 1:
                        await self._set_page(self._current_page_index - 1)
                    elif reaction.emoji == Menu.RIGHT_ARROW and len(self._pages) > 1:
                        await self._set_page(self._current_page_index + 1)
                    elif await self._reaction_handler(reaction):
                        break
                if not user.bot:
                    await reaction.remove(user)
        except asyncio.TimeoutError:
            logger.info('%s timed out.', self._ctx.message.author)
        finally:
            await self._ctx.message.delete()
            if self._menu_msg:
                await self._menu_msg.delete()

    async def _set_page(self, page_index):
        page_index %= len(self._pages)
        self._current_page_index = page_index

        menu_field = self._get_menu_field()
        self._menu_embed.set_field_at(
            self._menu_field_index,
            name=f'Page {self._current_page_index + 1}/{len(self._pages)}',
            value=menu_field,
            inline=False
            )

        self._menu_msg = await self._menu_msg.edit(embed=self._menu_embed)
        await self._set_reactions()


class Menu(_MenuBase):
    """Create a menu from a raw string, a list of lines or a list of pages."""
    def __init__(self,
                 ctx,
                 title,
                 raw=None,
                 lines=None,
                 pages=None,
                 max_chars_per_line=64,
                 max_lines_per_page=16,
                 timeout=60.0):
        """
        PARAMS
        ------
        ctx                   - message ctx
        title                 - title of embed
        raw=None              - raw string input, broken up automatically, takes precedence over pages
        lines=None            - list of strings, each index will be a line automatically broken up into pages,
                                takes precedence over raw
        pages=None            - list of strings, each index will be a page
        max_chars_per_line=64 - maximum characters per line
        max_lines_per_page=16 - maximum lines per page
        timeout=60.0          - menu timeout in seconds
        """
        super().__init__(ctx, title, pages, timeout)

        if raw or lines:
            self._pages = self._split(raw, lines, max_chars_per_line, max_lines_per_page)

    async def _init_reactions(self):
        if len(self._pages) > 1:
            await self._menu_msg.add_reaction(_MenuBase.LEFT_ARROW)
            await self._menu_msg.add_reaction(_MenuBase.RIGHT_ARROW)

    def _get_menu_field(self):
        return self._pages[self._current_page_index]

    def _split(self, raw, lines, max_chars_per_line, max_lines_per_page):
        i = 0
        if not lines:
            lines = wrap(text=raw, width=max_chars_per_line)
        pages = []
        while i + max_lines_per_page < len(lines):
            pages.append("\n".join(lines[i:i + max_lines_per_page]))
            i += max_lines_per_page

        if i < len(lines):
            pages.append("\n".join(lines[i:]))

        return pages


class MenuWithOptions(_MenuBase):
    """
    Create a menu with options from a list of options or a list of pages.

    OVERRIDES
    ---------
    init_feedback_ui()
    update_feedback_ui()
    option_to_string(option: Any) -> str

    API
    ---
    get_ctx() -> discord.ext.commands.Context
    get_selected_option() -> list
    add_feedback_ui_field(name: str, value: str, inline=True: boolean)
    set_feedback_ui_field_at(index: int, name: str, value: str, default: str, inline=True: boolean)
    """
    def __init__(self, ctx, title, options=None, pages=None, max_lines_per_page=5, option_padding=2, timeout=60.0):
        """
        PARAMS
        ------
        ctx                   - message ctx
        title                 - title of embed
        options=None          - list of options, broken up automatically, takes precedence over:
        pages=None            - list of lists of options, each index will be a page
        max_lines_per_page=5  - maximum number of options per page
        option_padding=2      - number of \u2000 between option emoji and option string
        timeout=60.0          - menu timeout in seconds
        """
        super().__init__(ctx, title, pages, timeout)

        self._padding = option_padding

        self._feedback_ui_field_indicies = []
        self._selected_options = []

        if options:
            self._pages = self._split(options, max_lines_per_page)

    # Overrides
    def init_feedback_ui(self):
        """Initialise fields in the menu embed that represent the feedback ui."""

    def update_feedback_ui(self):
        """Repaint feedback ui on option select."""

    def option_to_string(self, option):
        """Must return a string representation of an option (returns 'option' by default)."""
        return option

    # API
    def get_ctx(self):
        """Returns menu instance's context"""
        return self._ctx

    def get_selected_options(self):
        """Returns a list of currently selected options."""
        return self._selected_options

    def add_feedback_ui_field(self, name, value, inline=True):
        """Adds a field to the menu embed."""
        self._menu_embed.add_field(name=name, value=value, inline=inline)
        self._feedback_ui_field_indicies.append(len(self._menu_embed.fields) - 1)

    def set_feedback_ui_field_at(self, index, name, value, default, inline=True):
        """
        Sets the field at index in the menu embed (must be a field created with add_feedback_ui_field).
        If value is empty, value = default.
        """
        if index not in self._feedback_ui_field_indicies:
            logger.error('index not in _feedback_ui_field_indicies')
        else:
            self._menu_embed.set_field_at(index, name=name, value=(value if len(value) > 0 else default), inline=inline)

    # Implementation
    def _init_menu_embed(self):
        self.init_feedback_ui()
        super()._init_menu_embed()

    async def _init_reactions(self):
        draw_arrows = False
        if len(self._pages) > 1:
            draw_arrows = True

        if draw_arrows:
            await self._menu_msg.add_reaction(_MenuBase.LEFT_ARROW)
        await self._menu_msg.add_reaction(_MenuBase.CHECK_MARK)
        if draw_arrows:
            await self._menu_msg.add_reaction(_MenuBase.RIGHT_ARROW)

        for i in range(len(self._pages[self._current_page_index])):
            await self._menu_msg.add_reaction(ri_at_index(i))

    def _get_menu_field(self):
        option_strings = [self.option_to_string(o) for o in self._pages[self._current_page_index]]
        padding = self._padding * '\u2000'

        for i, option_string in enumerate(option_strings):
            option_strings[i] = f'{ri_at_index(i)}{padding}{option_string}'

        return '\n'.join(option_strings)

    async def _reaction_handler(self, reaction):
        if reaction.emoji == _MenuBase.CHECK_MARK:
            return True

        if reaction.emoji in list(ri_alphabet(len(self._pages[self._current_page_index]))):
            if self._pages[self._current_page_index][index_of_ri(reaction.emoji)] not in self._selected_options:
                self._selected_options.append(self._pages[self._current_page_index][index_of_ri(reaction.emoji)])
            else:
                self._selected_options.remove(self._pages[self._current_page_index][index_of_ri(reaction.emoji)])

            self.update_feedback_ui()
            self._menu_msg = await self._menu_msg.edit(embed=self._menu_embed)

            return False

    async def _set_reactions(self):
        self._menu_msg = await self._ctx.fetch_message(self._menu_msg.id)

        last_index = len(self._pages[self._current_page_index]) - 1 + 3
        current_index = len(self._menu_msg.reactions) - 1
        if current_index < last_index:
            current_index += 1
            while current_index <= last_index:
                await self._menu_msg.add_reaction(ri_at_index(current_index - 3))
                current_index += 1
        elif current_index > last_index:
            while current_index > last_index:
                await self._menu_msg.remove_reaction(ri_at_index(current_index - 3), self._ctx.bot.user)
                current_index -= 1

    def _split(self, options, max_lines_per_page):
        current_line = 0
        pages = []
        current_page = []
        for option in options:
            if current_line % max_lines_per_page == 0 and current_line > 0:
                pages.append(current_page)
                current_page = []
            current_page.append(option)
            current_line += 1

        if len(current_page) > 0:
            pages.append(current_page)

        return pages


class MenuWithCustomOptions(MenuWithOptions):
    """Create a menu with custom options from a list of options or pages."""
    def __init__(self, ctx, title, options=None, pages=None, max_lines_per_page=5, option_padding=2, timeout=60.0):
        """
        PARAMS
        ------
        ctx                   - message ctx
        title                 - title of embed
        options=None          - dict of options, broken up automatically, takes precedence over:
        pages=None            - list of dicts of options, each index will be a page
        max_lines_per_page=5  - maximum number of options per page
        option_padding=2      - number of \u2000 between option emoji and option string
        timeout=60.0          - menu timeout in seconds
        """
        super().__init__(ctx, title, options, pages, max_lines_per_page, option_padding, timeout)

        for i, page in enumerate(self._pages):
            temp = {}
            for key, val in page.items():
                temp[emojize(normalize(key), language='alias')] = val
            self._pages[i] = temp

    async def _init_reactions(self):
        draw_arrows = False
        if len(self._pages) > 1:
            draw_arrows = True

        if draw_arrows:
            await self._menu_msg.add_reaction(_MenuBase.LEFT_ARROW)
        await self._menu_msg.add_reaction(_MenuBase.CHECK_MARK)
        if draw_arrows:
            await self._menu_msg.add_reaction(_MenuBase.RIGHT_ARROW)

        for k in self._pages[self._current_page_index].keys():
            await self._menu_msg.add_reaction(k)

    def _get_menu_field(self):
        option_strings = []
        padding = self._padding * '\u2000'

        for key, val in self._pages[self._current_page_index].items():
            option_strings.append(f'{key}{padding}{self.option_to_string(val)}')

        return '\n'.join(option_strings)

    async def _reaction_handler(self, reaction):
        if reaction.emoji == _MenuBase.CHECK_MARK:
            return True

        if reaction.emoji in list(self._pages[self._current_page_index].keys()):
            if self._pages[self._current_page_index][reaction.emoji] not in self._selected_options:
                self._selected_options.append(self._pages[self._current_page_index][reaction.emoji])
            else:
                self._selected_options.remove(self._pages[self._current_page_index][reaction.emoji])

            self.update_feedback_ui()
            self._menu_msg = await self._menu_msg.edit(embed=self._menu_embed)

            return False

    async def _set_reactions(self):
        await self._menu_msg.clear_reactions()
        await self._init_reactions()

    def _split(self, options, max_lines_per_page):
        current_line = 0
        pages = []
        current_page = {}
        for key, val in options.items():
            if current_line % max_lines_per_page == 0 and current_line > 0:
                pages.append(current_page)
                current_page = {}
            current_page[key] = val
            current_line += 1

        if len(current_page) > 0:
            pages.append(current_page)

        return pages
