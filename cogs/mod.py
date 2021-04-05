from discord import Embed
import discord
import asyncio
from discord.ext import commands


class Moderation(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.command(name="ban", aliases=['b'], brief='Bans the user mentioned from the guild')
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        if ctx.author.top_role < member.top_role:
            await ctx.send(f"Your top role {ctx.author.top_role.name} is lower than {member}\'s top role {member.top_role.name} You cannot moderate them!")
            return
        embed = discord.Embed(title = "Ban Successful", description = f"Banned {member} from {ctx.guild.name} with reason ```{reason}```")
        embed.footer = ctx.message.created_at
        embed.set_author(name = ctx.author, icon_url = ctx.author.avatar_url)
        await member.send(f"You were banned from {ctx.guild} for: {reason}") 
        await member.ban(reason = f"Action by {ctx.author} Reason: {reason}")
        await ctx.send(embed = embed)

    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.command(name="kick", brief='Kicks the user mentioned from the guild')
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        if ctx.author.top_role < member.top_role:
            await ctx.send(f"Your top role {ctx.author.top_role.name} is lower than {member}\'s top role {member.top_role.name} You cannot moderate them!")
            return
        embed = discord.Embed(title = "Kick Successful", description = f"Kicked {member} from {ctx.guild.name} with reason ```{reason}```")
        embed.footer = ctx.message.created_at
        embed.set_author(name = ctx.author, icon_url = ctx.author.avatar_url)
        await member.send(f"You were kicked from {ctx.guild} for: {reason}") 
        await member.kick(reason = f"Action by {ctx.author} Reason: {reason}")
        await ctx.send(embed = embed)



def setup(bot):
    bot.add_cog(Moderation(bot))
