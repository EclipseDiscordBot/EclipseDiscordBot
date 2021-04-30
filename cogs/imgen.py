import random
import urllib

import aiofiles
import aiohttp
import discord
from discord.ext import commands


class ImageGeneration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="youtube", aliases=['yt'], brief="Fakes a youtube comment")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def youtube(self, ctx, user: discord.User = None, *, comment: str):
        comment = urllib.parse.quote(comment)
        uname = urllib.parse.quote((str(ctx.author) if not user else str(user)))
        if len(comment) > 999:
            await ctx.reply("comment cant be more than 1000 chars long")
            return
        url = (ctx.author.avatar_url if not user else user.avatar_url)
        await ctx.reply(
            f"https://some-random-api.ml/canvas/youtube-comment?avatar={url}&username={uname}&comment={comment}")

    @commands.command(name="amongus", aliases=['amoongus', 'au'], brief="Fakes an among us death screen")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def au(self, ctx, user: discord.User = None, *, impostor: bool):
        async with ctx.channel.typing():
            uname = urllib.parse.quote((str(ctx.author) if not user else str(user)))
            url = (ctx.author.avatar_url if not user else user.avatar_url)
            impostor = ('true' if impostor else 'false')
            rand = random.randint(0, 10000)
            async with aiohttp.ClientSession() as session:
                url = f"https://some-random-api.ml/premium/amongus?avatar={url}&username={uname}&impostor={impostor}&key={self.bot.sra_api}"
                async with session.get(url) as resp:
                    if resp.status == 200:
                        f = await aiofiles.open(f'data/amongus.{rand}.gif', mode='wb')
                        await f.write(await resp.read())
                        await f.close()

            file = discord.File(open(f'data/amongus.{rand}.gif', 'rb'))
            await ctx.reply(file=file)


def setup(bot: commands.Bot):
    bot.add_cog(ImageGeneration(bot))
