from discord.ext import commands
from classes import CustomBotClass


class TicketingSystem(commands.Cog):
    def __init__(self, bot: CustomBotClass.CustomBot):
        self.bot = bot

    # TODO Finish this


def setup(bot: CustomBotClass.CustomBot):
    bot.add_cog(TicketingSystem(bot))
