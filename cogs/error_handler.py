import discord
import asyncio
from discord.ext import commands


class ErrorHandler(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error: Exception):
        if isinstance(error, discord.ext.commands.CommandNotFound):
            return
        e = discord.Embed(title=f"Sorry! the bot has run into an Error `{error}`",
                          description="It has been reported to the "
                                      "devs! *if you're a dev PRs are "
                                      "open("
                                      "https://github.com"
                                      "/EclipseDiscordBot"
                                      "/EclipseDiscordBot)")
        await ctx.send(embed=e)

    @commands.is_owner()
    @commands.command(name="test", hidden=True)
    async def test(self, ctx, cmd: str):
        await ctx.send(f"ok! testing {cmd}")
        if cmd == "errorhandler" or cmd == "error":
            raise Exception


def setup(bot: commands.Bot):
    bot.add_cog(ErrorHandler(bot))
