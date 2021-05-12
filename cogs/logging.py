import discord
from discord.ext import commands
from classes import CustomBotClass
from discord import Embed
import datetime


class Logging(commands.Cog):
    def __init__(self, bot: CustomBotClass.CustomBot):
        self.bot = bot


    async def get_log_channel(self, server_id):
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                await conn.fetch(
                    'SELECT * FROM logging WHERE server_id = $1', server_id
                )
                log_channel_id = log_channel_ids[0]['channel_id']
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
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "INSERT INTO logs(server_id,channel_id,msg_id,reason,timestamp,type,mod_id,punished_id,msg)"
                    "VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9)", msg.guild_id, msg.channel_id, msg.message_id,
                    ("Message deleted by " + str(msg.cached_message.author.name) if msg.cached_message else "Unknown"),
                    datetime.datetime.now().timestamp(), 0, 0, 0,
                    (msg.cached_message.content if msg.cached_message else "Message not found in cache"))
                log_channel_ids = await conn.fetch("SELECT * FROM logging WHERE server_id=$1", msg.guild_id)
                log_channel_id = log_channel_ids[0]['channel_id']
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
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "INSERT INTO logs(server_id,channel_id,msg_id,reason,timestamp,type,mod_id,punished_id,msg)"
                    "VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9)", msg.guild_id, msg.channel_id, msg.message_id,
                    f"Message Edited by {new_edited_msg_content.author}",
                    datetime.datetime.now().timestamp(), 1, 0, 0, new_edited_msg_content.content)
                log_channel_ids = await conn.fetch("SELECT * FROM logging WHERE server_id=$1", msg.guild_id)
                log_channel_id = log_channel_ids[0]['channel_id']
                log_chnl = self.bot.get_guild(
                    msg.guild_id).get_channel(log_channel_id)
                if log_chnl is None:
                    return
                await log_chnl.send(embed=e)

    @commands.Cog.listener("on_member_join")
    async def member_join(self, member):
        created = list(str(datetime.datetime.utcnow() - member.created_at)[:-7])

        x = 0
        for char in created:
            if char == ":":
                created[x] == " hours, "
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
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_author(name=member, icon_url=member.avatar_url)
        embed.set_footer(text=f"ID: {member.id}")
        log_channel_id = self.get_log_channel(member.guild.id)
        log_chnl = self.bot.get_guild(member.guild.id).get_channel(log_channel_id)
        if log_chnl == None:
            return
        await log_chnl.send(embed=embed)


    @commands.Cog.listener("on_member_remove")
    async def member_remove(self, member):
        joined = list(str(datetime.datetime.utcnow() - member.joined_at)[:-7])

        x = 0
        for char in joined:
            if char == ':':
                joined[x] = " hours, "
                break
            x += 1

        x = 0
        for char in joined:
            if char == ':':
                joined[x] = " minutes and "
                break
            x += 1

        joined = "".join(joined)

        embed = discord.Embed(
            title="Member left",
            color=discord.Colour.red(),
            description=f"{member.mention} left the server.\nJoined {joined} seconds ago.",
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_author(name=member, icon_url=member.avatar_url)
        embed.set_footer(text=f"ID: {member.id}")
        log_channel_id = self.get_log_channel(member.guild.id)
        log_chnl = self.bot.get_guild(member.guild.id).get_channel(log_channel_id)
        if log_chnl == None:
            return
        await log_chnl.send(embed=embed)



    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        if before.name != after.name:
            e = discord.Embed(title="Role Name Changed", color=discord.Colour.blurple())
            e.add_field(name="Before:", value=before.name)
            e.add_field(name="After:", value=after.name)
            e.add_field(name="Role:", value=before.mention)
        elif before.color != after.color:
            e = discord.Embed(title="Role Colour Changed", color=discord.Colour.blue())
            e.add_field(name="Before:", value=before.color)
            e.add_field(name="After:", value=after.color)
            e.add_field(name="Role:", value=before.mention)
        elif before.mentionable != after.mentionable:
            e = discord.Embed(title="Role Mentionable Changed", color=discord.Colour.green())
            e.add_field(name="Before:", value=f"{'Yes' if before.mentionable else 'No'}")
            e.add_field(name="After:", value=f"{'Yes' if after.mentionable else 'No'}")
        else:
            return
        log_channel_id = self.get_log_channel(after.guild.id)
        log_chnl = self.bot.get_guild(after.guild.id).get_channel(log_channel_id)

        if log_chnl == None:
            return
        await log_chnl.send(embed=embed)


def setup(bot):
    bot.add_cog(Logging(bot))
