from discord import Embed
import discord
import asyncio
from discord.ext import commands


class Moderation(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.command(name="ban", aliases=['ban_hammer'], brief='Bans the user mentioned')
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        if not member:
            await ctx.send("usage: ban <member> <reason>")
        if ctx.author.top_role < member.top_role:
            await ctx.send("LOL NO YOU DON'T HAVE PERMS")
            return
        await member.send(f"Banned from {ctx.guild.name}. reason: ```{reason}```")
        await ctx.guild.ban(member)
        await ctx.send(f"Banned {member.display_name}. reason: ```{reason}```")

    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.command(name="kick", brief='Kicks the user mentioned')
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        if not member:
            await ctx.send("usage: kick <member> <reason>")
        if ctx.author.top_role < member.top_role:
            await ctx.send("LOL NO YOU DON'T HAVE PERMS")
            return
        await member.send(f"kicked from {ctx.guild.name}. reason: ```{reason}```")
        await ctx.guild.ban(member)
        await ctx.send(f"Kicked {member.display_name}. reason: ```{reason}```")


def setup(bot):
    bot.add_cog(Moderation(bot))
