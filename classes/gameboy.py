import pyboy
import discord
from discord import ButtonStyle, Interaction
from discord.ext import commands


class Btn(discord.ui.Button):
    def __init__(self, *, label: str, style: ButtonStyle, GB_inst: pyboy.PyBoy, press_key: pyboy.WindowEvent,
                 release_key: pyboy.WindowEvent, author: discord.User):
        super().__init__(label=label, style=style)
        self.gb_inst = GB_inst
        self.press_key = press_key
        self.release_key = release_key
        self.author = author

    async def callback(self, interaction: Interaction):
        if not self.author.id == interaction.user.id:
            await interaction.response.send_message(
                "HEY! You're not the person whose playing! I'm not letting you :unamused:")
            return
        self.gb_inst.send_input(self.press_key)
        self.gb_inst.send_input(self.release_key)


class EmptyBtn(discord.ui.Button):
    def __init__(self):
        super().__init__(style=ButtonStyle.secondary)

    def callback(self, interaction: Interaction):
        return


class SpecialBtn(discord.ui.Button):
    def __init__(self, *, label: str, style: ButtonStyle, GB_inst: pyboy.PyBoy, press_key: pyboy.WindowEvent,
                 author: discord.User):
        super().__init__(label=label, style=style)
        self.gb_inst = GB_inst
        self.press_key = press_key
        self.author = author

    async def callback(self, interaction: Interaction):
        if not self.author.id == interaction.user.id:
            await interaction.response.send_message(
                "HEY! You're not the person whose playing! I'm not letting you :unamused:")
            return
        self.gb_inst.send_input(self.press_key)


layout = [
    [None, None, None, ]
]


class GameBoy:
    def __init__(self, user: discord.User):
        pass
