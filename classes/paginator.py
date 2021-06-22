import discord
from discord import ButtonStyle, Interaction


class PageButton(discord.ui.Button):
    def __init__(self, message: discord.Message, embed: discord.Embed, page_no: int, page_prefix: str):
        super().__init__(style=ButtonStyle.blurple, label=f'{page_prefix} {page_no+1}')
        self.message = message
        self.embed = embed

    async def callback(self, interaction: Interaction):
        await self.message.edit(embed=self.embed)


class Paginator(discord.ui.View):
    def __init__(self, message, embeds, page_prefix: str):
        super().__init__()
        for embed in embeds:
            self.add_item(PageButton(message, embed, (embeds.index(embed)), page_prefix))
