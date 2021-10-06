from discord.ext import commands
import discord


class Website(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.link, label="Website", url="https://satyamedh.ml")


class Invite(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.link, label="Invite",
                         url="https://bit.ly/EclipseDiscordBotInviteWithSlashCommandsSupport")


class Links(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(Website())
        self.add_item(Invite())
