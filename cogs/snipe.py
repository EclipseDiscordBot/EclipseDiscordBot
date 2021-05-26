import discord
from discord.ext import commands
from classes import indev_check
import humanize
import datetime


class SnipeCog(commands.Cog):
    def __init__(self, bot):
        self.bot=bot


    @commands.Cog.listener('on_message_delete')
    async def snipe_listener(self, message):
        msg_created = datetime.datetime.timestamp(message.created_at)
        msg_deleted = datetime.datetime.timestamp(datetime.datetime.now())
        all = await self.bot.fetch("SELECT * FROM snipe WHERE ch_id=$1", message.channel.id)
        if len(all) >= 10:
            last = all[9]['msg_id']

            await self.bot.pool.execute("DELETE FROM snipe WHERE msg_id = $1", last)

        await self.bot.pool.execute("INSERT INTO snipe (ch_id, msg_id, msg_created, msg_author, msg_content, "
                                    "msg_deleted) VALUES ($1, $2, $3, $4, $5, $6)", message.channel.id, message.id,
                                    msg_created, message.author.id, message.content, msg_deleted)










    @commands.command()
    @commands.guild_only()
    @indev_check.command_in_development()
    async def snipe(self, ctx, channel:discord.TextChannel=None, index:int=1):
        if channel is None:
            channel = ctx.channel
        all = await self.bot.pool.fetch("SELECT * FROM snipe WHERE ch_id = $1", channel.id)
        row = all[index-1]
        author= self.bot.get_user(row['msg_author'])
        created = humanize.naturaltime(datetime.datetime.fromtimestamp(row['msg_created']))
        embed=discord.Embed(title=f"in {channel.mention} {created}", description=row['msg_content'], color=self.bot.color)
        embed.set_author(name=author, icon_url=author.avatar_url)
        embed.timestamp = datetime.datetime.fromtimestamp(row['msg_deleted'])
        embed.set_footer(text=f"Message ID {row['msg_id']} • Message deleted at")
        await ctx.send(embed=embed)




def setup(bot):
    bot.add_cog(SnipeCog(bot))
