import asyncio
import random
import urllib.parse

import aiohttp
import discord
from discord.ext import commands


class Fun(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(brief="Chooses a random object from specified options",
                      aliases=["pick", "choose"])
    async def choice(self, ctx, *, options: str):
        options1 = options.split(' ')
        choice = random.choice(options1)
        await ctx.reply(f"I choose..... {choice}")

    @commands.command(brief="Repeats you", aliases=['echo'])
    async def say(self, ctx, *, words: str):
        txt = await commands.clean_content().convert(ctx, words)
        await ctx.reply(txt)

    @commands.command(brief="gives a random meme from r/memes")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def meme(self, ctx):
        random_post = self.bot.memes[random.randint(0, len(self.bot.memes))]
        await ctx.reply(embed=random_post)

    @commands.command(name="dbt", aliases=['discord_bot_token'], brief="Gives a fake random discord bot token")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def dbt(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://some-random-api.ml/bottoken") as r:
                res = await r.json()
                await ctx.reply(res['token'])
                await asyncio.sleep(2)
                await ctx.reply("lol thats a fake bot token :P")

    @commands.command(name="youtube", aliases=['yt'], brief="Fakes a youtube comment")
    @commands.cooldown(1,15,commands.BucketType.user)
    async def youtube(self, ctx, user: discord.User=None, *, comment:str):
        comment = urllib.parse.quote(comment)
        uname = urllib.parse.quote((str(ctx.author) if not user else str(user)))
        if len(comment) > 999:
            await ctx.reply("comment cant be more than 1000 chars long")
            return
        url = (ctx.author.avatar_url if not user else user.avatar_url)
        await ctx.reply(
            f"https://some-random-api.ml/canvas/youtube-comment?avatar={url}&username={uname}&comment={comment}")




def setup(bot):
    bot.add_cog(Fun(bot))
