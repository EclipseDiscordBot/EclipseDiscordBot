import asyncio
import random
from classes import CustomBotClass
import aiohttp
from prsaw import RandomStuff
from discord.ext import commands

rs = RandomStuff()

class Fun(commands.Cog):

    def __init__(self, bot: CustomBotClass.CustomBot):
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

    @commands.command(name="dbt",
                      aliases=['discord_bot_token'],
                      brief="Gives a fake random discord bot token")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def dbt(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://some-random-api.ml/bottoken") as r:
                res = await r.json()
                await ctx.reply(res['token'])
                await asyncio.sleep(2)
                await ctx.reply("lol thats a fake bot token :P")


    @commands.command(name="chatbot",
                      aliases=['chat', 'chatb', 'cb'],
                      brief="Start a talking session with the bot!")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def _chatbot(self, ctx):
        session = True
        await ctx.send("The talking session between you and me started! Why not say something like `hi`\nIf you want to end this talking session, type `Cancel`")

        while session is True:
            try:
                message = await self.bot.wait_for('message', timeout = 30, check = lambda m : (ctx.author == m.author and ctx.channel == m.channel))
            except asyncio.TimeoutError:
                session = False
                await ctx.send("Timed out! Talking session with me has automatically ended!")
            else:
                if message.content.lower() == "cancel":
                    session = False
                    await ctx.send("Talking session with me has ended!")
                else:
                    async with ctx.channel.typing():
                        response = rs.get_ai_response(message.content)
                        await ctx.reply(response, mention_author=False)




def setup(bot):
    bot.add_cog(Fun(bot))
