from discord import Embed
import discord
from discord.ext import commands


class BasicCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.message.reply(f"Pong! {round(self.bot.latency * 1000)} ms")


def setup(bot):
    bot.add_cog(BasicCog(bot))
