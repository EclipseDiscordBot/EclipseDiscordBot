import discord
from discord.ext import commands


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['av'], brief="gives the mentioned user(you if nobody is mentioned)'s avatar")
    async def avatar(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        embed = discord.Embed(title=" ", description=" ", color=0x2F3136)
        embed.set_image(url=member.avatar_url)
        await ctx.reply(embed=embed)

    @commands.command(aliases=["ct", "timedif", "timediff"], brief="gives the difference between two ids (any ids)")
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


def setup(bot):
    bot.add_cog(Utility(bot))
