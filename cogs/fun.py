
import random

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

    @commands.command(brief="Repeats you")
    async def say(self, ctx, *, words: str):
        txt = await commands.clean_content().convert(ctx, words)
        await ctx.reply(txt)

    @commands.command(brief="gives a random meme from r/memes")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def meme(self, ctx):
        random_post = self.bot.memes[random.randint(0, len(self.bot.memes))]
        await ctx.reply(embed=random_post)


def setup(bot):
    bot.add_cog(Fun(bot))
