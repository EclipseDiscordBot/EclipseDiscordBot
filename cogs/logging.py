import discord
from discord.ext import commands
from classes import CustomBotClass
from discord import Embed
import humanize
import datetime


class Logging(commands.Cog):
    def __init__(self, bot: CustomBotClass.CustomBot):
        self.bot = bot

    async def get_log_channel(self, server_id):
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                log_channel_ids = await conn.fetch(
                    'SELECT * FROM logging WHERE server_id = $1', server_id
                )
                try:
                    log_channel_id = log_channel_ids[0]['channel_id']
                except IndexError:
                    return
                return log_channel_id

    @commands.command(name="log",
                      brief="Sets the log channel and toggles logging")
    @commands.has_permissions(manage_guild=True)
    async def log(self, ctx, channel: discord.TextChannel, toggle: bool):
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("UPDATE logging "
                                   "SET channel_id=$1,"
                                   "enabled=$2 "
                                   "WHERE server_id=$3",
                                   channel.id,
                                   toggle,
                                   ctx.guild.id)
        await ctx.reply("Aight! logging is now " + ("enabled" if toggle else "disabled"))

    @commands.Cog.listener("on_raw_message_delete")
    async def msg_del(self, msg: discord.RawMessageDeleteEvent):
        channel = self.bot.get_guild(msg.guild_id).get_channel(msg.channel_id)
        deleted_msg_content = msg.cached_message.content if msg.cached_message else "Message not found in cache"
        e = Embed(
            title="Message deleted",
            description=f"Message deleted in {channel.mention}")
        e.add_field(
            name="Content: ", value=(
                deleted_msg_content if not len(deleted_msg_content) == 0 else "Empty msg"))
        e.timestamp = datetime.datetime.utcnow()
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "INSERT INTO logs(server_id,channel_id,msg_id,reason,timestamp,type,mod_id,punished_id,msg)"
                    "VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9)", msg.guild_id, msg.channel_id, msg.message_id,
                    ("Message deleted by " + str(msg.cached_message.author.name) if msg.cached_message else "Unknown"),
                    datetime.datetime.now().timestamp(), 0, 0, 0,
                    (msg.cached_message.content if msg.cached_message else "Message not found in cache"))
                log_channel_ids = await conn.fetch("SELECT * FROM logging WHERE server_id=$1", msg.guild_id)
                try:
                    log_channel_id = log_channel_ids[0]['channel_id']
                except IndexError:
                    return
                log_chnl = self.bot.get_guild(
                    msg.guild_id).get_channel(log_channel_id)
                if log_chnl is None:
                    return
                await log_chnl.send(embed=e)

    @commands.Cog.listener("on_raw_message_edit")
    async def msg_edit(self, msg: discord.RawMessageUpdateEvent):
        channel: discord.TextChannel = self.bot.get_guild(
            msg.guild_id).get_channel(msg.channel_id)
        try:
            new_edited_msg_content = await channel.fetch_message(msg.message_id)
        except discord.errors.NotFound:
            new_edited_msg_content = "Message was deleted through an edit"
        e = Embed(
            title="Message Edited",
            description=f"Message Edited in {channel.mention}")
        e.add_field(
            name="New message: ",
            value=(
                new_edited_msg_content.content if not isinstance(
                    new_edited_msg_content,
                    str) else new_edited_msg_content))
        e.timestamp = datetime.datetime.utcnow()
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "INSERT INTO logs(server_id,channel_id,msg_id,reason,timestamp,type,mod_id,punished_id,msg)"
                    "VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9)", msg.guild_id, msg.channel_id, msg.message_id,
                    f"Message Edited by {new_edited_msg_content.author}",
                    datetime.datetime.now().timestamp(), 1, 0, 0, new_edited_msg_content.content)
                log_channel_ids = await conn.fetch("SELECT * FROM logging WHERE server_id=$1", msg.guild_id)
                try:
                    log_channel_id = log_channel_ids[0]['channel_id']
                except IndexError:
                    return
                log_chnl = self.bot.get_guild(
                    msg.guild_id).get_channel(log_channel_id)
                if log_chnl is None:
                    return
                try:
                    await log_chnl.send(embed=e)
                except discord.HTTPException:
                    pass

    @commands.Cog.listener("on_member_join")
    async def member_join(self, member: discord.Member):
        created = list(
            str(datetime.datetime.utcnow() - member.created_at.replace(tzinfo=None))[:-7])

        x = 0
        for char in created:
            if char == ":":
                created[x] = " hours, "
                break
            x += 1

        x = 0
        for char in created:
            if char == ":":
                created[x] = " minutes and "
                break
            x += 1

        created = "".join(created)
        embed = discord.Embed(
            title="Member Joined",
            color=self.bot.user.color,
            description=f"{member.mention} has joined the server!\nCreated {created} seconds ago.",
            timestamp=datetime.datetime.utcnow())
        embed.set_author(name=member, icon_url=member.avatar.url)
        embed.set_footer(text=f"ID: {member.id}")
        embed.timestamp = datetime.datetime.utcnow()
        log_channel_id = await self.get_log_channel(member.guild.id)
        log_chnl = self.bot.get_guild(member.guild.id).get_channel(log_channel_id)
        if log_chnl == None:
            return
        await log_chnl.send(embed=embed)

    @commands.Cog.listener("on_member_remove")
    async def member_leave(self, member):
        joined = humanize.precisedelta(datetime.datetime.now() - member.joined_at.replace(tzinfo=None))
        embed = discord.Embed(
            title="Member left",
            color=discord.Colour.red(),
            description=f"{member.mention} left the server.\nJoined {joined} seconds ago.",
            timestamp=datetime.datetime.utcnow())
        embed.set_author(name=member, icon_url=member.avatar.url)
        embed.set_footer(text=f"ID: {member.id}")
        embed.timestamp = datetime.datetime.utcnow()
        log_channel_id = await self.get_log_channel(member.guild.id)
        log_chnl = self.bot.get_guild(member.guild.id).get_channel(log_channel_id)
        if log_chnl is None:
            return
        await log_chnl.send(embed=embed)

    @commands.Cog.listener("on_guild_role_update")
    async def guild_role_update(self, before, after):
        if before.name != after.name:
            e = discord.Embed(
                title="Role Name Changed",
                color=discord.Colour.blurple())
            e.add_field(name="Before:", value=before.name)
            e.add_field(name="After:", value=after.name)
            e.add_field(name="Role:", value=before.mention)
        elif before.color != after.color:
            e = discord.Embed(
                title="Role Colour Changed",
                color=discord.Colour.blue())
            e.add_field(name="Before:", value=before.color)
            e.add_field(name="After:", value=after.color)
            e.add_field(name="Role:", value=before.mention)
        elif before.mentionable != after.mentionable:
            e = discord.Embed(
                title="Role Mentionable Changed",
                color=discord.Colour.green())
            e.add_field(
                name="Before:",
                value=f"{'Yes' if before.mentionable else 'No'}")
            e.add_field(
                name="After:",
                value=f"{'Yes' if after.mentionable else 'No'}")
        else:
            return
        log_channel_id = await self.get_log_channel(after.guild.id)
        log_chnl = self.bot.get_guild(
            after.guild.id).get_channel(log_channel_id)

        if log_chnl is None:
            return
        await log_chnl.send(embed=e)

    @commands.Cog.listener("on_guild_update")
    async def guild_update(self, before, after):
        if before.name != after.name:
            embed = discord.Embed(
                title="Server Changed Name",
                color=discord.Colour.blurple()
            )
            embed.add_field(name="Before:", value=before.name)
            embed.add_field(name="After:", value=after.name)
        elif before.owner != after.owner:
            embed = discord.Embed(
                title="Server Owner Changed",
                color=discord.Colour.green()
            )
            embed.add_field(name="Before:", value=before.owner)
            embed.add_field(name="After:", value=after.owner)
        elif before.afk_channel != after.afk_channel:
            embed = discord.Embed(
                title="Server Afk Channel Changed",
                color=discord.Colour.blue()
            )
            embed.add_field(
                name="Before:",
                value=before.afk_channel
            )
            embed.add_field(
                name="After:",
                value=after.afk_channel
            )
        elif before.banner_url != after.banner_url:
            embed = discord.Embed(
                title="Server Banner Changed",
                description=f"Before Banner: {before.banner_url}\nAfter Banner: {after.banner_url}")
            embed.add_field(
                name="Before:",
                value=before.banner_url
            )
            embed.add_field(
                name="After:",
                value=after.banner_url
            )
        else:
            return
        log_channel_id = await self.get_log_channel(after.guild.id)
        log_chnl = self.bot.get_guild(after.guild.id).get_channel(log_channel_id)
        embed.timestamp = datetime.datetime.utcnow()
        if log_chnl == None:
            return
        await log_chnl.send(embed=embed)

    @commands.Cog.listener("on_guild_update")
    async def guild_update(self, before, after):
        if before.name != after.name:
            embed = discord.Embed(
                title="Server Changed Name",
                color=discord.Colour.blurple()
            )
            embed.add_field(name="Before:", value=before.name)
            embed.add_field(name="After:", value=after.name)
        elif before.owner != after.owner:
            embed = discord.Embed(
                title="Server Owner Changed",
                color=discord.Colour.green()
            )
            embed.add_field(name="Before:", value=before.owner)
            embed.add_field(name="After:", value=after.owner)
        elif before.afk_channel != after.afk_channel:
            embed = discord.Embed(
                title="Server Afk Channel Changed",
                color=discord.Colour.blue()
            )
            embed.add_field(
                name="Before:",
                value=before.afk_channel
            )
            embed.add_field(
                name="After:",
                value=after.afk_channel
            )
        elif before.banner.url != after.banner.url:
            embed = discord.Embed(
                title="Server Banner Changed",
                description=f"Before Banner: {before.banner_url}\nAfter Banner: {after.banner_url}"
            )
            embed.add_field(
                name="Before:",
                value=before.banner_url
            )
            embed.add_field(
                name="After:",
                value=after.banner_url
            )
        else:
            return
        embed.timestamp = datetime.datetime.utcnow()
        log_channel_id = await self.get_log_channel(after.guild.id)
        log_chnl = self.bot.get_guild(after.guild.id).get_channel(log_channel_id)
        if log_chnl == None:
            return
        await log_chnl.send(embed=embed)

    @commands.Cog.listener("on_voice_state_update")
    async def voice_state_update(self, member, before, after):
        if before.channel == None:
            embed = discord.Embed(
                title="Member joined voice channel",
                description=f"**{member}** joined `#{after.channel.name}`",
                color=discord.Colour.green(),
                timestamp=datetime.datetime.utcnow()
            )
        elif after.channel == None:
            embed = discord.Embed(
                title="Member left voice channel",
                description=f"**{member}** left `#{before.channel.name}`",
                color=discord.Colour.red(),
                timestamp=datetime.datetime.utcnow()
            )
        elif before.channel != after.channel:
            embed = discord.Embed(
                title="Member switched voice channel",
                description=f"**{member}** switched `#{before.channel.name}` --> `#{after.channel.name}`",
                color=discord.Colour.blue(),
                timestamp=datetime.datetime.utcnow()
            )
        elif after.self_stream:
            embed = discord.Embed(
                title="Member started streaming",
                description=f"**{member}** started streaming in `#{before.channel.name}`",
                color=discord.Colour.purple(),
                timestamp=datetime.datetime.utcnow()
            )
        elif before.self_stream and after.self_stream == False:
            embed = discord.Embed(
                title="Member stopped streaming",
                description=f"**{member}** stopped streaming in `#{before.channel.name}`",
                color=discord.Colour.purple(),
                timestamp=datetime.datetime.utcnow()
            )
        else:
            return
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_author(name=member, icon_url=member.avatar.url)
        embed.set_footer(text=f"ID: {member.id}")
        log_channel_id = await self.get_log_channel(member.guild.id)
        log_chnl = self.bot.get_guild(member.guild.id).get_channel(log_channel_id)

        if log_chnl == None:
            return
        await log_chnl.send(embed=embed)

    @commands.Cog.listener("on_member_update")
    async def member_update(self, before, after):
        member = after
        if before.nick != after.nick:
            embed = discord.Embed(
                title="Member updated nickname",
                color=discord.Colour.blue(),
                timestamp=datetime.datetime.utcnow()
            )
            embed.add_field(name="Before:", value=before.nick)
            embed.add_field(name="After:", value=after.nick)

        elif before.roles != after.roles:
            add = list(set(after.roles) - set(before.roles))
            rem = list(set(before.roles) - set(after.roles))
            try:
                if add[0] in after.roles:
                    embed = discord.Embed(
                        title="Member updated roles",
                        color=discord.Colour.blue(),
                        timestamp=datetime.datetime.utcnow(),
                        description=f"Added `{add[0].name}` role"
                    )
            except IndexError:
                try:
                    if rem[0] in before.roles:
                        embed = discord.Embed(
                            title="Member updated roles",
                            color=discord.Colour.blue(),
                            timestamp=datetime.datetime.utcnow(),
                            description=f"Removed `{rem[0].name}` role"
                        )
                except IndexError:
                    return
        else:
            return

        embed.set_author(name=member, icon_url=member.avatar.url)
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text=f"ID: {member.id}")
        log_channel_id = await self.get_log_channel(after.guild.id)
        log_chnl = self.bot.get_guild(after.guild.id).get_channel(log_channel_id)
        if log_chnl == None:
            return
        await log_chnl.send(embed=embed)


def setup(bot):
    bot.add_cog(Logging(bot))
