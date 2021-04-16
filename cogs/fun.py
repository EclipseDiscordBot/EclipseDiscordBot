import discord
import os
import random
import asyncio
from discord.ext import commands
from discord_slash import cog_ext, SlashContext


class Fun(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(brief="Chooses a random object from specified options", aliases=["pick", "choose"])
    async def choice(self, ctx, *, options: str):
        options = options.split(' ')
        choice = random.choice(options)
        await ctx.reply(f"I choose..... {choice}")



def setup(bot):
    bot.add_cog(Fun(bot))
