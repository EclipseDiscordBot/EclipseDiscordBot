import discord
from discord.ext import commands
import asyncio
from constants.basic import *
from urllib.parse import quote
import aiohttp


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['av'],
                      brief="gives the mentioned user(you if nobody is mentioned)'s avatar")
    async def avatar(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        embed = discord.Embed(title=" ", description=" ", color=0x2F3136)
        embed.set_image(url=member.avatar_url)
        await ctx.reply(embed=embed)

    @commands.command(aliases=["ct", "timedif", "timediff"],
                      brief="gives the difference between two ids (any ids)")
    async def snowflake(self, ctx, win_id: int, dm_id: int):
        win_time = discord.utils.snowflake_time(win_id)
        dm_time = discord.utils.snowflake_time(dm_id)
        diff = dm_time - win_time
        seconds = diff.total_seconds()
        seconds_str = str(seconds)
        final = seconds_str
        if seconds_str.startswith("-"):
            final = seconds_str[1:]
        await ctx.send(f"Difference between the two message ID's is `{final}` seconds!")

    @commands.command(name="suggest", brief="Suggest a command to the devs")
    @commands.cooldown(5, 5, discord.ext.commands.BucketType.user)
    async def suggest(self, ctx: commands.Context, *, suggestion=None):
        if suggestion is None:
            def chek(u1):
                return u1.author == ctx.author
            await ctx.reply(
                "Great! your suggestion is valuable! Now send what the new suggestion will do in brief in **1 SINGLE MESSAGE** \n\n **Pro tip: using shift+enter creates a new line without sending the message**")
            try:
                message = await self.bot.wait_for('message', timeout=60.0, check=chek)
            except asyncio.TimeoutError:
                await ctx.reply("time's up mate, try again!")
                return
            else:
                await ctx.reply("Great! now send some detailed description on the new feature in **1 SINGLE MESSAGE**")
                try:
                    message2 = await self.bot.wait_for('message', timeout=300.0, check=chek)
                except asyncio.TimeoutError:
                    await ctx.reply("time's up mate, try again!")
                    return
                else:
                    await ctx.reply("Great! Sending the suggestion...")
                    brief = message.content
                    detailed = message2.content
        else:
            brief = "Not specified"
            detailed = suggestion
        suggestion_channel = self.bot.get_channel(834442086513508363)
        dsc = f"""


**Brief:** ```{brief}```
**Detailed Description:** ```{detailed}```

"""
        embed = discord.Embed(
            title="New Suggestion",
            description=dsc,
            color=self.bot.color)
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        embed.set_footer(text=f"From {ctx.guild if ctx.guild else None}")
        embed.timestamp = ctx.message.created_at
        suggestion_msg = await suggestion_channel.send(embed=embed)
        await suggestion_msg.add_reaction('✅')
        await suggestion_msg.add_reaction('🚫')
        await ctx.reply(f"Done! you can check the your suggestion's reviews in {support_server} <#834442086513508363>")

    @commands.command(description="QRifies your text")
    @commands.cooldown(15, 15, commands.BucketType.user)
    async def qr(self, ctx, *, text: str):
        final_text = quote(text)
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"https://chart.googleapis.com/chart?chl={final_text}&chs=200x200&cht=qr&chld=H%7C0") as res:
                await ctx.reply(res.url)

    @commands.command(description="MINECRAFTifies your text",
                      aliases=["achievements"])
    @commands.cooldown(15, 15, commands.BucketType.user)
    async def achievement(self, ctx, *, text: str):
        final_text = quote(text)
        await ctx.reply(f"https://minecraftskinstealer.com/achievement/13/Achievement+Acquired%21/{final_text}")

    @commands.Cog.listener("on_message")
    async def on_msg(self, msg: discord.message):
        if not msg.guild:
            return
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                data = await conn.fetch("SELECT * FROM config WHERE server_id=$1", msg.guild.id)
                if not data[0]['math']:
                    return
        if msg.author == self.bot.user:
            return
        try:
            allowed_names = {"sum": sum}
            code = compile(msg.content, "<string>", "eval")
            for name in code.co_names:
                if name not in allowed_names:
                    return
            result = eval(code, {"__builtins__": {}}, allowed_names)
            await msg.reply(result)
        except Exception:
            return

    @commands.command(name="ar", aliases=['autoresponse'])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def ar(self, ctx, option: str, toggle: bool):
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                if option == "math":
                    await conn.execute("UPDATE config SET math=$1 WHERE server_id=$2", toggle, ctx.guild.id)
                else:
                    await ctx.reply("unknown cmd!")
                    return
        await ctx.reply("done!")


def setup(bot):
    bot.add_cog(Utility(bot))
