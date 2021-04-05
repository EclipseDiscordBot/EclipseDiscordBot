import discord
import asyncio
from discord.ext import commands


class Basic(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="ping", aliases=['pong'], brief='Gives the bot\'s latency')
    async def ping(self, ctx):
        await ctx.message.reply(f"Pong! {round(self.bot.latency * 1000)} ms")



def setup(bot):
    bot.add_cog(Basic(bot))
