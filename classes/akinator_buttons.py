from discord.ext import commands
from classes import akinator_callbacks
import discord


class YesButton(discord.ui.Button):
    def __init__(self, author: discord.User, callback):
        super().__init__(style=discord.ButtonStyle.success, label="Yes")
        self.author = author
        self.callback_command = callback

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.id == self.author.id:
            await interaction.response.send_message(
                f"{interaction.user.mention}! you cant play this game of akinator!, start your own!")
            return
        await self.callback_command(akinator_callbacks.YES)


class NoButton(discord.ui.Button):
    def __init__(self, author: discord.User, callback):
        super().__init__(style=discord.ButtonStyle.danger, label="No")
        self.author = author
        self.callback_command = callback

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.id == self.author.id:
            await interaction.response.send_message(
                f"{interaction.user.mention}! you cant play this game of akinator!, start your own!")
            return
        await self.callback_command(akinator_callbacks.NO)


class IdkButton(discord.ui.Button):
    def __init__(self, author: discord.User, callback):
        super().__init__(style=discord.ButtonStyle.blurple, label="I don't know")
        self.author = author
        self.callback_command = callback

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.id == self.author.id:
            await interaction.response.send_message(
                f"{interaction.user.mention}! you cant play this game of akinator!, start your own!")
            return
        await self.callback_command(akinator_callbacks.idk)


class ProbablyButton(discord.ui.Button):
    def __init__(self, author: discord.User, callback):
        super().__init__(style=discord.ButtonStyle.secondary, label="Probably")
        self.author = author
        self.callback_command = callback

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.id == self.author.id:
            await interaction.response.send_message(
                f"{interaction.user.mention}! you cant play this game of akinator!, start your own!")
            return
        await self.callback_command(akinator_callbacks.P)


class ProbablyNotButton(discord.ui.Button):
    def __init__(self, author: discord.User, callback):
        super().__init__(style=discord.ButtonStyle.secondary, label="Probably not")
        self.author = author
        self.callback_command = callback

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.id == self.author.id:
            await interaction.response.send_message(
                f"{interaction.user.mention}! you cant play this game of akinator!, start your own!")
            return
        await self.callback_command(akinator_callbacks.PN)


class GameOver(discord.ui.Button):
    def __init__(self, author: discord.User, callback):
        super().__init__(style=discord.ButtonStyle.success, label="You're right!")
        self.author = author
        self.callback_command = callback

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.id == self.author.id:
            await interaction.response.send_message(
                f"{interaction.user.mention}! you cant play this game of akinator!, start your own!")
            return
        await self.callback_command(True)
        await interaction.response.send_message("GGs, I WIN!")
        return


class NotRight(discord.ui.Button):
    def __init__(self, author: discord.User, callback):
        super().__init__(style=discord.ButtonStyle.danger, label="Nope!")
        self.author = author
        self.callback_command = callback

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.id == self.author.id:
            await interaction.response.send_message(
                f"{interaction.user.mention}! you cant play this game of akinator!, start your own!")
            return
        await self.callback_command(False)
        await interaction.response.send_message("Huh, I'll try again")
        return

class Back(discord.ui.Button):
    def __init__(self, author: discord.User, callback):
        super().__init__(style=discord.ButtonStyle.blurple, label="Back!")
        self.author = author
        self.callback_command = callback

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.id == self.author.id:
            await interaction.response.send_message(
                f"{interaction.user.mention}! you cant play this game of akinator!, start your own!")
            return
        await self.callback_command(akinator_callbacks.back)
        return


class AkinatorView(discord.ui.View):
    def __init__(self, author, callback):
        super().__init__()
        self.add_item(YesButton(author, callback))
        self.add_item(NoButton(author, callback))
        self.add_item(IdkButton(author, callback))
        self.add_item(ProbablyButton(author, callback))
        self.add_item(ProbablyNotButton(author, callback))
        self.add_item(Back(author, callback))


class AkinatorView2(discord.ui.View):
    def __init__(self, author, callback):
        super().__init__()
        self.add_item(GameOver(author, callback))
        self.add_item(NotRight(author, callback))
