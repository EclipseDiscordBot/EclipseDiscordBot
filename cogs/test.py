from discord.ext import commands
from classes import CustomBotClass, indev_check
import discord



class TestCog(commands.Cog):
    def __init__(self, bot: CustomBotClass.CustomBot):
        self.bot = bot


def setup(bot):
    bot.add_cog(TestCog(bot))
