import discord
from discord.ext import commands

class owner_cmds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="PING SPAM(owner only to call other devs on, so nobody use it pls)", name="spamping")
    @commands.is_owner()
    async def spamping(self, ctx: discord.ext.commands.Context, times: int, member: discord.Member):
        for i in range(times):
            await ctx.reply(member.mention)

    @commands.command(breif = "Perform SQL commands ")
    @commands.is_owner()
    async def sql(self, ctx, query, vals=None):
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                if query.startswith("SELECT"):
                    try:
                        ret = await conn.fetchval(query, vals)
                        await ctx.send(f"The query returned {ret}")
                    except Exception:
                        await ctx.message.add_reaction("‼️")
                    else:
                        await ctx.message.add_reaction("✅")
                else:
                    if val is None:
                        try:
                            await conn.execute(query, vals)
                        except Exception:
                            await ctx.message.add_reaction("‼️")
                        else:
                            await ctx.message.add_reaction("✅")
                    else:
                        try:
                            await conn.execute(query, vals)
                        except Exception:
                            await ctx.message.add_reaction("‼️")
                        else:
                            await ctx.message.add_reaction("✅")


def setup(bot):
    bot.add_cog(owner_cmds(bot))
