from classes import CustomBotClass
import random
from discord.ext import commands
from discord_slash import cog_ext, SlashContext


class Fun(commands.Cog):

    def __init__(self, bot: CustomBotClass.CustomBot):
        self.bot = bot

    @cog_ext.cog_slash(name="choose")
    async def _choice(self, ctx: SlashContext, *, options: str):
        options = options.split(' ')
        choice = random.choice(options)
        await ctx.send(f"I choose..... {choice}")


def setup(bot):
    bot.add_cog(Fun(bot))
