import discord
import os
import asyncio
import constants.basic as basicC
from common_functions.discord_checks import *
from discord.ext import commands
from discord_slash import cog_ext, SlashContext


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
        exit(0)

    @commands.command(name="version", brief="Gives the bot's version")
    async def version(self, ctx):
        await ctx.reply(basicC.version)

    @commands.command(name="invite", brief="Gives the bot's invite link!")
    async def invite(self, ctx):
        await ctx.reply(f"{basicC.invite} ,I'll be waiting!")

    @commands.command(name="test", brief="Tests an aspect of the bot")
    @commands.is_owner()
    async def test(self, ctx, aspect: str):
        aspect = aspect.lower()
        if aspect == "error" or aspect == "exception":
            await ctx.reply("ok, testing!")
            raise Exception("TESTTTTTTT")

    @commands.command(name="servers", aliases=["servercount"], brief="Tests an aspect of the bot")
    @commands.is_owner()
    async def servers(self, ctx):
        await ctx.send(len(self.bot.guilds))

    @commands.command(name="suggest", brief="Suggest a command to the devs")
    @commands.cooldown(5, 5, discord.ext.commands.BucketType.user)
    async def suggest(self, ctx: commands.Context):
        def chek(u1):
            return u1.author == ctx.author
        await ctx.reply(
            "Great! your suggestion is valuable! Now send what the new suggestion will do in brief in **1 SINGLE MESSAGE** \n\n **Pro tip: using shift+enter creates a new line without sending the message**")
        try:
            message = await self.bot.wait_for('message', timeout=60.0, check=chek)
        except asyncio.TimeoutError:
            await ctx.reply("time's up mate, try again!")
        else:
            await ctx.reply("Great! now send some detailed description on the new feature in **1 SINGLE MESSAGE**")
            try:
                message2 = await self.bot.wait_for('message', timeout=300.0, check=chek)
            except asyncio.TimeoutError:
                await ctx.reply("time's up mate, try again!")
            else:
                await ctx.reply("Great! Sending the suggestion to the devs")
                suggestion_channel = await self.bot.fetch_channel(834442086513508363)
                suggestion_msg = await suggestion_channel.send(f"""

NEW SUGGESTION FROM {ctx.author}

Brief: ```{message.content}```
Detailed Description: ```{message2.content}```

""")
                #await suggestion_msg.add_reaction(':white_check_mark:')
                #await suggestion_msg.add_reaction(':negative_squared_cross_mark:')
                await ctx.reply("Done! Thanks for suggesting! keep your DMs open from me, so that I can inform you about your suggestion's status")


def setup(bot):
    bot.add_cog(Basic(bot))
