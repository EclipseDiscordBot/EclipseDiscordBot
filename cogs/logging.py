import discord
from discord.ext import commands
from discord import Embed


class Logging(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(brief="Sets the log channel and toggles logging")
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
        await ctx.reply(f"Aight! logging is now " + ("enabled" if toggle else "disabled"))

    @commands.Cog.listener("on_raw_message_delete")
    async def msg_del(self, msg: discord.RawMessageDeleteEvent):
        channel = self.bot.get_guild(msg.guild_id).get_channel(msg.channel_id)
        deleted_msg_content = msg.cached_message.content if msg.cached_message else "Message not found in cache"
        e = Embed(
            title="Message deleted",
            description=f"Message deleted in {channel.mention}")
        e.add_field(name="Content: ", value=deleted_msg_content)
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                log_channel_ids = await conn.fetch("SELECT * FROM logging WHERE server_id=$1", msg.guild_id)
                log_channel_id = log_channel_ids[0]['channel_id']
                await self.bot.get_guild(msg.guild_id).get_channel(log_channel_id).send(embed=e)


def setup(bot: commands.Bot):
    bot.add_cog(Logging(bot))
