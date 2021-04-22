import discord
import os
import asyncio
import constants.basic as basicC
from discord.ext import commands
from discord_slash import cog_ext, SlashContext


class Basic(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @cog_ext.cog_slash(name="invite")
    async def _invite(self, ctx: SlashContext):
        await ctx.send(f"{basicC.invite} ,I'll be waiting!")


def setup(bot):
    bot.add_cog(Basic(bot))
