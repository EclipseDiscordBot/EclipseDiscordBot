import discord
import asyncio
from discord.ext import commands


class Basic(commands.Cog):

    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(name="ping", aliases=['pong'], brief='Gives the bot\'s latency')
    async def ping(self, ctx):
        await ctx.message.reply(f"Pong! {round(self.bot.latency * 1000)} ms")



def setup(client):
    bot.add_cog(Basic(client))
