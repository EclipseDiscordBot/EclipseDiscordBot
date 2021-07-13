import discord
from discord.ext import commands

class ServerConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(2, 30, commands.BucketType.user)
    @commands.has_permissions(manage_guild=True)
    @commands.group(invoke_without_command=True)
    async def chatbot(self, ctx):
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                data = await conn.fetchrow('SELECT * FROM chatbot WHERE guild_id = $1', ctx.guild.id)
                if data:
                    channel = f"<#{data['channel_id']}>"
                else:
                    channel = "Disabled"
                e = discord.Embed(title=":robot: Chatbot", description=f"The chatbot is currently {'set to' if data else ''} **{channel}**\n\n**Here are all the commands that you can use to configure them:**\n\n-`{ctx.prefix}chatbot channel <#channel>` - To enable/update chatbot.\n-`{ctx.prefix}chatbot disable` - To disable chatbot", color=discord.Colour.random())
                await ctx.reply(embed=e)
                return

    @commands.cooldown(2, 30, commands.BucketType.user)
    @chatbot.command()
    async def set(self, ctx, channel:discord.TextChannel=None):
        if not channel:
            return await ctx.reply(
                embed = discord.Embed(
                    title = f"No Channel!",
                    description = "Please provide a channel for me to set.",
                    color = discord.Colour.red()
                )
            )
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                data = await conn.fetchrow('SELECT * FROM chatbot WHERE guild_id = $1', ctx.guild.id)
                if not data:
                    await conn.execute('INSERT INTO chatbot(channel_id, guild_id) VALUES($1, $2)', channel.id, ctx.guild.id)
                else:
                    await conn.execute('UPDATE chatbot SET channel_id = $1 WHERE guild_id = $2', ctx.guild.id)
                await channel.edit(slowmode_delay=5)
                await ctx.reply(f"The chatbot channel has been set to {channel.mention}!\nNow you can chat with me there.")

    @commands.cooldown(2, 30, commands.BucketType.user)
    @chatbot.command()
    async def disable(self, ctx):
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                data = await conn.fetchrow('SELECT * FROM chatbot WHERE guild_id = $1', ctx.guild.id)
                if not data:
                    return await ctx.reply("The chatbot for this server is already disabled!")
                await conn.execute('DELETE FROM chatbot WHERE guild_id = $1', ctx.guild.id)
                await ctx.reply("I have disabled the chatbot for this server!")

def setup(bot):
    bot.add_cog(ServerConfig(bot))