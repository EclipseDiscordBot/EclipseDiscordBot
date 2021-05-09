import discord
from discord.ext import commands
from classes import CustomBotClass
from discord import Embed
import datetime


class Logging(commands.Cog):
    def __init__(self, bot: CustomBotClass.CustomBot):
        self.bot = bot

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
                log_channel_ids = await conn.fetch("SELECT * FROM logging WHERE server_id=$1", msg.guild_id)
                log_channel_id = log_channel_ids[0]['channel_id']
                log_chnl = self.bot.get_guild(
                    msg.guild_id).get_channel(log_channel_id)
                if log_chnl is None:
                    return
                await log_chnl.send(embed=e)
                await conn.execute("INSERT INTO logs(server_id,channel_id,msg_id,reason,timestamp,type,mod_id,punished_id)"
                                   "VALUES($1,$2,$3,$4,$5,$6,$7,$8)", msg.guild_id, msg.channel_id, msg.message_id, "Message deleted by " + str(msg.cached_message.author.name) if msg.cached_message else "Unknown", datetime.datetime.now().timestamp(), 0, 0, 0)

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
                log_channel_ids = await conn.fetch("SELECT * FROM logging WHERE server_id=$1", msg.guild_id)
                log_channel_id = log_channel_ids[0]['channel_id']
                log_chnl = self.bot.get_guild(
                    msg.guild_id).get_channel(log_channel_id)
                if log_chnl is None:
                    return
                await log_chnl.send(embed=e)
                await conn.execute(
                    "INSERT INTO logs(server_id,channel_id,msg_id,reason,timestamp,type,mod_id,punished_id)"
                    "VALUES($1,$2,$3,$4,$5,$6,$7,$8)", msg.guild_id, msg.channel_id, msg.message_id,
                    f"Message Edited by {new_edited_msg_content.author}",
                    datetime.datetime.now().timestamp(), 1, 0, 0)


def setup(bot):
    bot.add_cog(Logging(bot))
