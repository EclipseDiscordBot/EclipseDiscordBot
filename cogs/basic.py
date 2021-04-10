import discord
import os
import asyncio
import constants.basic as basicC
from discord.ext import commands


class Basic(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="ping", aliases=['pong'], brief='Gives the bot\'s latency')
    async def ping(self, ctx):
        await ctx.reply(f"Pong! {round(self.bot.latency * 1000)} ms")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def restart(self, ctx):
        await ctx.reply("Restarting...")
        os.system("sh startupfile.sh")
        await asyncio.sleep(2)
        exit(0)

    @commands.command(name="version", brief="Gives the bot's version")
    async def version(self, ctx):
        await ctx.reply(basicC.version)

    @commands.command(name="invite", brief="Gives the bot's invite link!")
    async def invite(self, ctx):
        await ctx.reply(f"{basicC.invite} ,I'll be waiting!")


def setup(bot):
    bot.add_cog(Basic(bot))
