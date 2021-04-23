import discord
from discord.ext import commands
import asyncio

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
        await ctx.reply("Done! you can check the your suggestion's reviews in https://discord.gg/qNwb6zdjJ6 <#834442086513508363>")


def setup(bot):
    bot.add_cog(Utility(bot))
