import discord
from discord.ext import commands
import jishaku
from constants.basic import owners
from classes import CustomBotClass, context


class Snipe(commands.Cog):
    def __init__(self, bot: CustomBotClass.CustomBot):
        self.bot = bot

    @commands.command("snipe", brief="Gets a deleted message")
    async def _snipe(self, ctx: context.Context, count: int = 1, channel: discord.TextChannel = None):
        if not channel:
            channel = ctx.channel
        rows = await self.bot.pool.fetch("SELECT * FROM snipe WHERE guild=$1 AND channel=$2", ctx.guild.id, channel.id)
        if len(rows) < abs(count):
            await ctx.reply("theres nothing at that position!")
            return
        row = rows[-(abs(count))]
        author: discord.User = self.bot.get_user(row['author'])
        if author is None:
            author_name = "Unknown User"
            author_pfp = ""
        else:
            author_name = author.display_name
            author_pfp = author.avatar.url
        e = discord.Embed(
            description=(
                row["message_content"] if row["message_content"] else None))
        e.set_author(name=author_name, icon_url=author_pfp)
        await ctx.reply(row["attachment"], embed=e)
        await self.bot.pool.fetch("DELETE FROM snipe WHERE guild=$1 AND message_content=$2", ctx.guild.id, row["message_content"])

    @commands.Cog.listener("on_message_delete")
    async def _snipe_listener(self, payload: discord.Message):
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("INSERT INTO snipe(guild,channel,message_content,attachment,author) VALUES($1,$2,$3,$4,$5)", payload.guild.id, payload.channel.id, payload.content, ("\n".join(a.url for a in payload.attachments)), payload.author.id)


def setup(bot):
    bot.add_cog(Snipe(bot))
