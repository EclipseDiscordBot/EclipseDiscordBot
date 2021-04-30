from discord.ext import commands


class AutoMeme(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = commands.Bot


def setup(bot: commands.Bot):
    bot.add_cog(AutoMeme(bot))