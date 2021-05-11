import discord
from discord.ext import commands
from classes import CustomBotClass, indev_check
from constants import emojis


class TicketingSystem(commands.Cog):
    def __init__(self, bot: CustomBotClass.CustomBot):
        self.bot = bot

    # TODO Finish this

    @commands.command()
    @indev_check.command_in_development()
    @commands.cooldown(1, 600, commands.BucketType.member)
    async def ticket(self, ctx: commands.Context, reason: str):
        data = await self.bot.pool.fetch("SELECT * FROM tickets WHERE creator_uid=$1 AND guild_uid=$2", ctx.author.id,
                                         ctx.guild.id)
        if data[0]['ticket_no'] == 0:
            await ctx.reply(
                "Sorry but you already have a ticket in this server. currently you cannot open multiple tickets in the same server!")
            return
        data2 = await self.bot.pool.fetch("SELECT * FROM tickets WHERE guild_uid=$1", ctx.guild.id)
        list_of_counter = []
        for row in data2:
            list_of_counter.append(row['counter'])
        highest_counter = (max(list_of_counter) if not list_of_counter == [] else 0)
        guild: discord.Guild = ctx.guild
        channel: discord.TextChannel = await guild.create_text_channel(f"ticket-{highest_counter}")
        await channel.set_permissions(guild.default_role, send_messages=False, read_messages=False)
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "INSERT INTO tickets(creator_uid,channel_uid,guild_uid,ticket_no,reason,counter) VALUES($1,$2,$3,$4,$5,$6)",
                    ctx.author.id, channel.id, ctx.guild.id, 0,  reason, highest_counter + 1)
                e = discord.Embed(title=f'New ticket!', description=reason)
                e.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
                message: discord.Message = await channel.send(embed=e)
                await message.add_reaction(emoji=emojis.lock)
                await ctx.reply(f"ticket opened! {channel.mention}")

    @commands.Cog.listener('on_raw_reaction_add')
    async def ticket_close_listener(self, payload: discord.RawReactionActionEvent):
        emoji = emojis.lock
        if str(payload.emoji) == str(emoji):
            data = await self.bot.pool.fetch("SELECT * FROM tickets WHERE creator_uid=$1 AND channel_uid=$2", payload.user_id, payload.channel_id)
            if not data:
                return
            if data[0]['ticket_no'] == 1:
                return
            channel: discord.TextChannel = await self.bot.fetch_channel(data[0]['channel_uid'])
            # ticket_name = channel.name
            await channel.delete()
            async with self.bot.pool.acquire() as conn:
                async with conn.transaction():
                    await conn.execute("UPDATE tickets SET ticket_no=1 WHERE creator_uid=$1 AND channel_uid=$2", payload.user_id, payload.channel_id)



def setup(bot: CustomBotClass.CustomBot):
    bot.add_cog(TicketingSystem(bot))
