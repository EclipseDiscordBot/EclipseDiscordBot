import discord
from discord.ext import commands


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def nuke(self, ctx):
        await ctx.send(f"Purging {ctx.channel.mention}...")
        pos = ctx.channel.position
        new_channel = await ctx.channel.clone(reason=f"Nuked by {ctx.author}")
        await ctx.channel.delete(reason=f"Nuked by {ctx.author}")
        await new_channel.edit(position=pos)
        await new_channel.send("Nuked this channel!")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def lock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send(f"{ctx.channel.mention} is now locked for everyone.")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def unlock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send(f"{ctx.channel.mention} is now unlocked for everyone.")


def setup(bot):
    bot.add_cog(Utility(bot))
