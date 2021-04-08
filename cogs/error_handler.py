import discord
import asyncio
from discord.ext import commands


class ErrorHandler(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: discord.ext.commands.Context, error: Exception):
        if isinstance(error, discord.ext.commands.CommandNotFound):
            return
        if isinstance(error, discord.ext.commands.MissingPermissions):
            await ctx.send("Sorry, You don't have permission to execute this command!")
            return
        if isinstance(error, discord.ext.commands.MissingRequiredArgument):
            cmd1 = str(ctx.message.content).split(' ')[0][2:]
            usage = self.bot.get_command(cmd1)
            usage2 = f'e!{cmd1} {usage.signature}'
            await ctx.send(usage2)
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
