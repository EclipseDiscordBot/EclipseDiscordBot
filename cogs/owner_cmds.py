import discord
from discord.ext import commands


class OwnerOnlyCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        brief="PING SPAM(owner only to call other devs on, so nobody use it pls)",
        name="spamping")
    @commands.is_owner()
    async def spamping(self, ctx: discord.ext.commands.Context, times: int, member: discord.Member):
        for i in range(times):
            await ctx.reply(f"{member.mention} {i}")

    @commands.command(breif="Perform SQL commands ")
    @commands.is_owner()
    async def sql(self, ctx, query, vals=None):
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                if query.startswith("SELECT"):
                    ret = await conn.fetchval(query, vals)
                    await ctx.send(f"The query returned {ret}")
                else:
                    if vals is None:
                        await conn.execute(query)
                    else:
                        await conn.execute(query, vals)


def setup(bot):
    bot.add_cog(OwnerOnlyCommands(bot))
