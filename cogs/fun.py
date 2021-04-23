
import random
from discord.ext import commands


class Fun(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(brief="Chooses a random object from specified options",
                      aliases=["pick", "choose"])
    async def choice(self, ctx, *, options: str):
        options1 = options.split(' ')
        choice = random.choice(options1)
        await ctx.reply(f"I choose..... {choice}")


def setup(bot):
    bot.add_cog(Fun(bot))
