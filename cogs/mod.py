import discord
import asyncio
from discord.ext import commands


class Moderation(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.command(name="ban", brief='Bans the user mentioned from the guild')
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        if ctx.author.top_role < member.top_role:
            await ctx.send(
                f"Your top role {ctx.author.top_role.name} is lower than {member}\'s top role {member.top_role.name}"
                f" You cannot moderate them!")
            return
        embed = discord.Embed(title="Ban Successful",
                              description=f"Banned {member} from {ctx.guild.name} with reason ```{reason}```",
                              footer=ctx.message.created_at,
                              color=self.bot.color)
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        try:
            await member.send(f"You were banned from {ctx.guild} for: {reason}")
        except Exception:
            pass
        await member.ban(reason=f"Action by {ctx.author} Reason: ```{reason}```")
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.command(name="kick", brief='Kicks the user mentioned from the guild')
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        if ctx.author.top_role < member.top_role:
            await ctx.send(
                f"Your top role {ctx.author.top_role.name} is lower than {member}\'s top role {member.top_role.name}"
                f" You cannot moderate them!")
            return
        embed = discord.Embed(title="Kick Successful", description=f"Kicked {member} from {ctx.guild.name} with "
                                                                   f"reason ```{reason}```",
                              footer=ctx.message.created_at, color=self.bot.color)
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        try:
            await member.send(f"You were kicked from {ctx.guild} for: {reason}")
        except Exception:
            pass
        await member.kick(reason=f"Action by {ctx.author} Reason: {reason}")
        await ctx.send(embed=embed)

    @commands.command(name="nuke", brief="Clones the channel, deletes the old one and rearranges the cloned channel")
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def nuke(self, ctx):
        await ctx.send(f"Purging {ctx.channel.mention}...")
        pos = ctx.channel.position
        new_channel = await ctx.channel.clone(reason=f"Nuked by {ctx.author}")
        await ctx.channel.delete(reason=f"Nuked by {ctx.author}")
        await new_channel.edit(position=pos)
        await new_channel.send("Nuked this channel!")

    @commands.command(name="lock", brief="Locks the channel so only admins can send messages")
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def lock(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await channel.send(f"{channel.mention} is now locked for everyone.")
        if channel != ctx.channel:
            await ctx.send(f"{channel.mention} is now locked for everyone.")

    @commands.command(name="unlock", brief="unlocks the channel so anybody with the default role can send messages")
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def unlock(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await channel.send(f"{channel.mention} is now unlocked for everyone.")
        if channel != ctx.channel:
            await ctx.send(f"{channel.mention} is now unlocked for everyone.")


def setup(bot):
    bot.add_cog(Moderation(bot))
