import asyncio
import json
import os
import discord
from classes import CustomBotClass
import sys
import pickle
from discord.ext import commands


class OwnerOnlyCommands(commands.Cog, name="DevCommands"):
    def __init__(self, bot: CustomBotClass.CustomBot):
        self.bot = bot

    @commands.command(hidden=True,
                      brief="PING SPAM(owner only to call other devs on, so nobody use it pls)",
                      name="spamping")
    @commands.is_owner()
    async def spamping(self, ctx: discord.ext.commands.Context, times: int, member: discord.Member):
        for i in range(times):
            await ctx.reply(f"{member.mention} {i}")

    @commands.command(hidden=True, brief="Perform SQL commands ")
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

    @commands.command(hidden=True, name="disablecog", brief="disables a cog")
    @commands.is_owner()
    async def _disable(self, ctx, cog: str):
        self.bot.config['cogs'][cog] = False
        with open('config/config.json', 'w') as file:
            json.dump(self.bot.config, file, sort_keys=True,
                      indent=2, separators=(',', ': '))
            file.flush()
        await ctx.reply(f"{cog} has been disabled until re-enabled! rebooting!")
        await self.restart(ctx)

    @commands.command(hidden=True, name="enablecog", brief="enables a cog")
    @commands.is_owner()
    async def _enable(self, ctx, cog: str):
        self.bot.config['cogs'][cog] = True
        with open('config/config.json', 'w') as file:
            json.dump(self.bot.config, file, sort_keys=True,
                      indent=2, separators=(',', ': '))
            file.flush()
        await ctx.reply(f"{cog} has been enabled! rebooting!")
        await self.restart(ctx)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def restart(self, ctx):
        await ctx.reply("Restarting...")
        os.system("bash startupfile.sh")
        await self.bot.logout()

    @commands.command(hidden=True, name="updatesra",
                      aliases=["sra"], brief="Updates SRA key")
    @commands.is_owner()
    async def updatesra(self, ctx, key: str):
        prev_credd = pickle.load(open('credentials.pkl', 'rb'))
        prev_credd['some_random_api'] = key
        pickle.dump(prev_credd, open('credentials.pkl', 'wb'))
        await ctx.reply("Done! rebooting!")
        await self.restart(ctx)


def setup(bot):
    bot.add_cog(OwnerOnlyCommands(bot))
