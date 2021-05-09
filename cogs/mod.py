import discord
from classes import CustomBotClass
from discord.ext import commands, flags


class Moderation(commands.Cog):

    def __init__(self, bot: CustomBotClass.CustomBot):
        self.bot = bot

    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.command(name="ban",
                      brief='Bans the user mentioned from the guild')
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        if ctx.author.top_role < member.top_role:
            await ctx.reply(
                f"Your top role {ctx.author.top_role.name} is lower than {member}\'s top role {member.top_role.name}"
                f" You cannot moderate them!")
            return
        embed = discord.Embed(
            title="Ban Successful",
            description=f"Banned {member} from {ctx.guild.name} with reason ```{reason}```",
            footer=ctx.message.created_at,
            color=self.bot.color)
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        try:
            await member.send(f"You were banned from {ctx.guild} for: {reason}")
        except Exception:
            pass
        await member.ban(reason=f"Action by {ctx.author} Reason: ```{reason}```")
        await ctx.reply(embed=embed)

    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.command(name="kick",
                      brief='Kicks the user mentioned from the guild')
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        if ctx.author.top_role < member.top_role:
            await ctx.reply(
                f"Your top role {ctx.author.top_role.name} is lower than {member}\'s top role {member.top_role.name}"
                f" You cannot moderate them!")
            return
        embed = discord.Embed(
            title="Kick Successful",
            description=f"Kicked {member} from {ctx.guild.name} with "
                        f"reason ```{reason}```",
            footer=ctx.message.created_at,
            color=self.bot.color)
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        try:
            await member.send(f"You were kicked from {ctx.guild} for: {reason}")
        except Exception:
            pass
        await member.kick(reason=f"Action by {ctx.author} Reason: {reason}")
        await ctx.reply(embed=embed)

    @commands.command(name="nuke",
                      brief="Clones the channel, deletes the old one and rearranges the cloned channel")
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def nuke(self, ctx):
        await ctx.reply(f"Purging {ctx.channel.mention}...")
        pos = ctx.channel.position
        new_channel = await ctx.channel.clone(reason=f"Nuked by {ctx.author}")
        await ctx.channel.delete(reason=f"Nuked by {ctx.author}")
        await new_channel.edit(position=pos)
        await new_channel.send("Nuked this channel!")

    @commands.command(name="lock",
                      brief="Locks the channel so only admins can send messages")
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def lock(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await channel.send(f"{channel.mention} is now locked for everyone.")
        if channel != ctx.channel:
            await ctx.reply(f"{channel.mention} is now locked for everyone.")

    @commands.command(name="unlock",
                      brief="unlocks the channel so anybody with the default role can send messages")
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def unlock(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await channel.send(f"{channel.mention} is now unlocked for everyone.")
        if channel != ctx.channel:
            await ctx.reply(f"{channel.mention} is now unlocked for everyone.")

    @commands.command(name="purge",
                      brief="Bulk deletes messages")
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def purge(self, ctx, amount: int = 20, *, full=None):
        if not full:
            await ctx.message.delete()
            await ctx.channel.purge(limit=amount)
            return
        if "--bots" in full:
            def check(m):
                return m.author.bot

            await ctx.message.delete()
            await ctx.channel.purge(limit=amount, check=check)
            return
        elif "--content" in full:
            key_msg = await ctx.send("What should be in the messages to be deleted?")

            def check_for(m):
                return m.author == ctx.author and m.channel.id == ctx.channel.id

            keyword_msg = await self.bot.wait_for('message', check=check_for)

            def check(m):
                return keyword_msg.content in m.content

            await ctx.message.delete()
            await key_msg.delete()
            await keyword_msg.delete()
            await ctx.channel.purge(limit=amount, check=check)


def setup(bot):
    bot.add_cog(Moderation(bot))
