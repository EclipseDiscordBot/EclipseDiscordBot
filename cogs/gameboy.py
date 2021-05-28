from discord.ext import commands
import discord
from classes import CustomBotClass, indev_check, ignore

class GameBoy(commands.Cog):
    def __init__(self, bot: CustomBotClass.CustomBot):
        self.bot = bot

def setup(bot):
    bot.add_cog(GameBoy(bot))