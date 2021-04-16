import discord
from discord.ext import commands


class greet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def greet(self, ctx):
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                ch_id, msg, del_after = await conn.fetchval("SELECT channel_id, msg, delafter FROM greet WHERE guild_id = $1", ctx.guild.id)
        channel = ctx.guild.get_channel(ch_id)
        embed = discord.Embed(title = "Greet configuration", description = f"These are the current "
                                                                                            f"greet configurations of"
                                                                                            f" **{ctx.guild.name}**",
                              color = self.bot.color)
        embed.add_field(name="Message", value = msg)
        embed.add_field(name = "Channel", value = channel.mention)
        embed.add_field(name = "Message will be deleted after", value = str(del_after))
        embed.add_field(name = "Variables", value = "You can use these keywords that will be replaced accordingly. \n **{mc}** - Will be replaced with the guilds' member count \n **{mention}** - Will be replaced with the joined member's mention")
        embed.set_author(name = ctx.author, icon_url = ctx.author.avatar_url)
        await ctx.send(embed = embed)



    @greet.command()
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def channel(self, ctx, channel:discord.TextChannel):
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("UPDATE greet SET channel_id = $1 WHERE guild_id = $2", ctx.channel.id, ctx.guild.id)
                del_after, msg = await conn.fetchval("SELECT delafter, msg FROM greet WHERE guild_id = $1", ctx.guild.id)
        embed = discord.Embed(title = "Greet configuration has been updated", description = f"These are the current "
                                                                                            f"greet configurations of"
                                                                                            f" **{ctx.guild.name}**",
                              color = self.bot.color)
        embed.add_field(name="Message", value = msg)
        embed.add_field(name = "Channel", value = channel.mention)
        embed.add_field(name = "Message will be deleted after", value = str(del_after))
        embed.set_author(name = ctx.author, icon_url = ctx.author.avatar_url)
        await ctx.send(embed = embed)

    @greet.command()
    async def msg(self, ctx, *, msg):
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("UPDATE greet SET msg = $1 WHERE guild_id = $2", msg, ctx.guild.id)
                del_after, ch_id = await conn.fetchval("SELECT delafter, channel_id FROM greet WHERE guild_id = $1", ctx.guild.id)
        embed = discord.Embed(title = "Greet configuration has been updated", description = f"These are the current "
                                                                                            f"greet configurations of"
                                                                                            f" **{ctx.guild.name}**",
                              color = self.bot.color)
        channel = ctx.guild.get_channel(ch_id)
        embed.add_field(name="Message", value = msg)
        embed.add_field(name = "Channel", value = channel.mention)
        embed.add_field(name = "Message will be deleted after", value = str(del_after))
        embed.set_author(name = ctx.author, icon_url = ctx.author.avatar_url)
        await ctx.send(embed = embed)

    @greet.command()
    @commands.guild_only()
    @commands.has_permissions(manage_messages = True)
    async def delafter(self,ctx,amt:int):
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("UPDARE greet SET delafter = $1 WHERE guild_id = $2", amt, ctx.guild.id)
                ch_id, msg = await conn.fetchval("SELECT channel_id, msg FROM greet WHERE guild_id = $1",ctx.guild.id)
        embed = discord.Embed(title = "Greet configuration has been updated", description = f"These are the current "
                                                                                            f"greet configurations of"
                                                                                            f" **{ctx.guild.name}**",
                              color = self.bot.color)
        channel = ctx.guild.get_channel(ch_id)
        embed.add_field(name="Message", value = msg)
        embed.add_field(name = "Channel", value = channel.mention)
        embed.add_field(name = "Message will be deleted after", value = str(del_after))
        embed.set_author(name = ctx.author, icon_url = ctx.author.avatar_url)
        await ctx.send(embed = embed)


    @greet.command()
    @commands.has_permissions(manage_messages = True)
    @commands.guild_only()
    async def enable(self, ctx):
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("UPDATE greet SET config = $1", 1)
        embed = discord.Embed(title = "Greet is now ENABLED", description = f"These are the current "
                                                                                            f"greet configurations of"
                                                                                            f" **{ctx.guild.name}**",
                              color = self.bot.color)
        channel = ctx.guild.get_channel(ch_id)
        embed.add_field(name="Message", value = msg)
        embed.add_field(name = "Channel", value = channel.mention)
        embed.add_field(name = "Message will be deleted after", value = str(del_after))
        embed.set_author(name = ctx.author, icon_url = ctx.author.avatar_url)
        embed.set_thumbnail(url = "https://cdn.discordapp.com/attachments/829735317966815273/832573291775787038/dbd26c4768e6ce541f5b857b4973226e.png")
        await ctx.send(embed = embed)

    @greet.command()
    @commands.has_permissions(manage_messages = True)
    @commands.guild_only()
    async def disable(self, ctx):
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("UPDATE greet SET config = $1", 0)
                ch_id, msg, del_after = await conn.fetchval("SELECT channel_id, msg, delafter FROM greet WHERE guild_id = $1", ctx.guild.id)
        embed = discord.Embed(title = "Greet is now DISABLED", description = "", color = self.bot.color)
        embed.set_author(name = ctx.author, icon_url = ctx.author.avatar_url)
        embed.set_thumbnail(url = "https://media.discordapp.net/attachments/720573752278253668/832576467619414036/a0a7f6cf67b863940eceaa40397e2030.png?width=135&height=135")
        await ctx.send(embed = embed)

    @commands.Cog.listener('on_member_join')
    async def greet_people(self, member:discord.Member):
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                config = await conn.fetchval("SELECT config FROM greet WHERE guild_id = $1", member.guild.id)
                if config == 0:
                    return
                elif config == 1:
                    ch_id, msg, delafter = await conn.fetchval("SELECT channel_id, msg, delafter FROM greet WHERE guild_id = $1", member.guild.id)
                    channel = member.guild.get_channel(ch_id)
                    text = msg.replace("{mc}", member.guild.member_count).replace("{mention}", member.mention)
                    await channel.send(text, delete_after = int(delafter))



def setup(bot):
    bot.add_cog(greet(bot))