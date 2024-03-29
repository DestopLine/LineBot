from collections.abc import Iterable
from typing import Self

import discord

import core
import db


class Page:
    """This class stores a message content and embed.

    This is meant to be used with a Paginator object.
    """

    __slots__ = ('content', 'embed')

    def __init__(self, content: str | None = None, *, embed: discord.Embed | None = None):
        self.content = content
        self.embed = embed

    @classmethod
    def from_list(
        cls,
        interaction: discord.Interaction,
        title: str,
        iterable: Iterable[str],
        *,
        colour=None,
    ) -> list[Self]:
        """Return a list of Page from an iterable of strings.

        Each string gets enumerated and each page can contain up to
        20 of these strings (20 lines).
        """
        formated: list[str] = []

        if colour is None:
            colour = db.default_color(interaction)

        for i, s in enumerate(iterable):
            formated.append(f'{i}. {s}')

        pages: list[Self] = []
        entries_per_page = 20

        for chunk in core.split_list(formated, entries_per_page):
            pages.append(
                cls(embed=discord.Embed(title=title, description='\n'.join(chunk), colour=colour)),
            )

        return pages


class Paginator(discord.ui.View):
    """A View that contains buttons for page navigation."""

    def __init__(
        self,
        interaction: discord.Interaction,
        *,
        pages: list[Page] = [],
        entries: int | None = None,
        timeout: float = 180.0,
    ):
        super().__init__(timeout=timeout)
        self.interaction = interaction
        self.page_num = 1
        self.page: Page | None = None
        self.pages: list[Page] = []
        self.entries = entries
        self.set_pages(pages)
        self.children: list[discord.ui.Button]  # type: ignore [no-redef]

    @classmethod
    def optional(
        cls,
        interaction: discord.Interaction,
        *,
        pages: list[Page] = [],
        entries: int | None = None,
        timeout: float = 180.0,
    ) -> Self | core.Missing:
        """Returns MISSING if there's only one page"""
        if len(pages) == 1:
            return discord.utils.MISSING

        return cls(interaction, pages=pages, entries=entries, timeout=timeout)

    def set_pages(self, pages: list[Page]) -> Self:
        """Set the internal list of Page objects.

        This method appends the page number and total amount
        of entries to the footer of the embed of each page.
        """
        self.pages = []
        final_length = len(pages)

        for i, page in enumerate(pages, start=1):
            if page.embed is None:
                continue

            footer_parts: list[str] = []

            if final_length > 1:
                footer_parts.append(f'Página {i} de {final_length}')

            if self.entries is not None:
                footer_parts.append(f'{self.entries} resultados')

            if page.embed.footer.text is not None:
                footer_parts.append(page.embed.footer.text)

            footer = ' | '.join(footer_parts)
            page.embed.set_footer(text=footer)
            self.pages.append(page)

        return self

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return self.interaction.user.id == interaction.user.id

    @discord.ui.button(emoji=core.first_emoji, style=discord.ButtonStyle.blurple, disabled=True)
    async def first(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await self.set_page(interaction, 1)

    @discord.ui.button(emoji=core.back_emoji, style=discord.ButtonStyle.blurple, disabled=True)
    async def back(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await self.set_page(interaction, self.page_num - 1)

    @discord.ui.button(emoji=core.next_emoji, style=discord.ButtonStyle.blurple)
    async def next(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await self.set_page(interaction, self.page_num + 1)

    @discord.ui.button(emoji=core.last_emoji, style=discord.ButtonStyle.blurple)
    async def last(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await self.set_page(interaction, len(self.pages))

    @discord.ui.button(emoji=core.search_emoji, style=discord.ButtonStyle.blurple)
    async def search(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        total_pages = len(self.pages)

        class SearchModal(discord.ui.Modal, title='Escribe un número de página'):
            answer = discord.ui.TextInput(
                label=f'Escribe un número de página (1-{total_pages})',
                required=True,
                min_length=1,
                max_length=len(str(total_pages)),
            )

        async def on_submit(modal: SearchModal):
            async def func(interaction: discord.Interaction) -> None:
                try:
                    value = int(modal.answer.value)
                    if 0 < value <= total_pages:
                        await self.set_page(interaction, value)
                    else:
                        await interaction.response.send_message(
                            core.Warning.error(f'Escribe un número entre el 1 y el {total_pages}'),
                            ephemeral=True,
                        )
                except ValueError:
                    await interaction.response.send_message(
                        core.Warning.error('Valor incorrecto. Escribe un número'),
                        ephemeral=True,
                    )

            return func

        modal = SearchModal()
        modal.timeout = self.timeout
        modal.on_submit = await on_submit(modal)
        await interaction.response.send_modal(modal)

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True
        await self.interaction.edit_original_response(view=self)

    async def set_page(self, interaction: discord.Interaction, page: int) -> Self:
        """Set the current page index and change button state.

        Indeces start at one.
        """
        self.page = self.pages[page-1]
        self.page_num = page
        self.children[0].disabled = self.page_num == 1
        self.children[1].disabled = self.page_num == 1
        self.children[2].disabled = self.page_num == len(self.pages)
        self.children[3].disabled = self.page_num == len(self.pages)
        await interaction.response.defer()
        await self.interaction.edit_original_response(
            content=self.page.content,
            embed=self.page.embed,
            view=self,
        )
        return self
