import asyncio
import json

import discord
import os
import sys
from discord.ext import commands


class OwnerOnlyCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
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

    @commands.command(name="disablecog", brief="disables a cog")
    @commands.is_owner()
    async def _disable(self, ctx, cog: str):
        self.bot.config['cogs'][cog] = False
        with open('constants/config.json', 'w') as file:
            json.dump(self.bot.config, file, sort_keys=True,
                      indent=2, separators=(',', ': '))
            file.flush()
        await ctx.reply(f"{cog} has been disabled until re-enabled! rebooting!")
        await asyncio.sleep(2)
        await self.restart(ctx)

    @commands.command(name="enablecog", brief="enables a cog")
    @commands.is_owner()
    async def _enable(self, ctx, cog: str):
        self.bot.config['cogs'][cog] = True
        with open('constants/config.json', 'w') as file:
            json.dump(self.bot.config, file, sort_keys=True,
                      indent=2, separators=(',', ': '))
            file.flush()
        await ctx.reply(f"{cog} has been enabled! rebooting!")
        await asyncio.sleep(2)
        await self.restart(ctx)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def restart(self, ctx):
        await ctx.reply("Restarting...")
        sys.exit(0)


def setup(bot):
    bot.add_cog(OwnerOnlyCommands(bot))
