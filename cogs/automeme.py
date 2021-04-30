import discord
from discord.ext import commands


class AutoMeme(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = commands.Bot

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def automeme(self, ctx, toggle: bool, channel: discord.TextChannel=None):
        if toggle and channel is None:
            await ctx.reply("Woah! please specify a channel mate!")
            return
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("UPDATE automeme SET channel_id=$1,enabled=$2 WHERE server_id=$3", (0 if not toggle else channel.id), toggle, ctx.guild.id)


def setup(bot: commands.Bot):
    bot.add_cog(AutoMeme(bot))
