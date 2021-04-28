import discord
from discord.ext import commands


class Logging(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(brief="Sets the log channel and toggles logging")
    @commands.has_permissions(manage_guild=True)
    async def log(self, ctx, channel: discord.TextChannel, toggle: bool):
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("UPDATE logging "
                                   "SET channel_id=$1,"
                                   "enabled=$2 "
                                   "WHERE server_id=$3",
                                   channel.id,
                                   toggle,
                                   ctx.guild.id)
        await ctx.reply(f"Aight! logging is now " + ("enabled" if toggle else "disabled"))


def setup(bot: commands.Bot):
    bot.add_cog(Logging(bot))
