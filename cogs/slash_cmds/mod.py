import discord
import asyncio
from discord.ext import commands
from discord_slash import cog_ext, SlashContext


class Moderation(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @cog_ext.cog_slash(name="ban")
    async def _ban(self, ctx: SlashContext, member: discord.Member, *, reason=None):
        if ctx.author.top_role < member.top_role:
            await ctx.send(
                f"Your top role {ctx.author.top_role.name} is lower than {member}\'s top role {member.top_role.name}"
                f" You cannot moderate them!")
            return
        embed = discord.Embed(title="Ban Successful",
                              description=f"Banned {member} from {ctx.guild.name} with reason ```{reason}```",
                              footer=ctx.message.created_at,
                              color=discord.Color.random())
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        try:
            await member.send(f"You were banned from {ctx.guild} for: {reason}")
        except Exception:
            pass
        await member.ban(reason=f"Action by {ctx.author} Reason: ```{reason}```")
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @cog_ext.cog_slash(name="kick")
    async def _kick(self, ctx: SlashContext, member: discord.Member, *, reason=None):
        if ctx.author.top_role < member.top_role:
            await ctx.send(
                f"Your top role {ctx.author.top_role.name} is lower than {member}\'s top role {member.top_role.name}"
                f" You cannot moderate them!")
            return
        embed = discord.Embed(title="Kick Successful", description=f"Kicked {member} from {ctx.guild.name} with "
                                                                   f"reason ```{reason}```",
                              footer=ctx.message.created_at, color=discord.Color.random())
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        try:
            await member.send(f"You were kicked from {ctx.guild} for: {reason}")
        except Exception:
            pass
        await member.kick(reason=f"Action by {ctx.author} Reason: {reason}")
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Moderation(bot))