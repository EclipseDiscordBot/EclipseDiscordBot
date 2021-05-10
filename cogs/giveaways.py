import discord
from discord.ext import commands
import datetime
import random


class Giveaways(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
# # (msg_id BIGINT, ch_id BIGINT, g_id BIGINT, end_timestamp BIGINT, winners BIGINT, host_id BIGINT, prize TEXT)
    async def force_end(self, msg_id):
        g_rows = await self.bot.pool.fetch("SELECT * FROM giveaways WHERE msg_id = $1", msg_id)
        await self.bot.pool.execute("DELETE FROM giveaways WHERE msg_id = $1", g_rows[0][0])
        g_row = g_rows[0]
        message_id = g_row['msg_id']
        channel = self.bot.get_channel(g_row['ch_id'])
        prize = g_row['prize']
        num_winners = int(g_row['winners'])
        if not channel:
            return
        message = await channel.fetch_message(message_id)
        if not message:
            return
        reaction = message.reactions[0]
        entries = await reaction.users().flatten()
        winners = random.choices(entries, k=num_winners)
        win_str = "Congratulations!, "
        for winner in winners:
            win_str += f"{winner.mention}, "
        win_str += f"you won {prize}!\n{message.jump_url}"
        await channel.send(win_str)








    def time_converter(self, time):
        time = time.lower()
        if time.endswith('s'):
            return datetime.timedelta(seconds=int(time[:-1]))
        if time.endswith('m'):
            return datetime.timedelta(minutes=int(time[:-1]))
        if time.endswith('h'):
            return datetime.timedelta(hours=int(time[:-1]))
        if time.endswith('d'):
            return datetime.timedelta(days=int(time[:-1]))
        else:
            return None
# (msg_id BIGINT, ch_id BIGINT, g_id BIGINT, end_timestamp BIGINT, winners BIGINT, host_id BIGINT, prize TEXT)
    @commands.command()
    async def gstart(self, ctx, time, winners, *, prize):
        duration = self.time_converter(time)
        if not duration:
            await ctx.send("Invalid time format. Example time usage: `5d`, `2m`, `30s`, `2h`")
            return
        if duration > datetime.timedelta(days=30):
            await ctx.send("Time shouldn't be bigger than 30 days!")
            return
        end_time = datetime.datetime.now() + duration
        embed=discord.Embed(title=prize,
                            description=f"React with 🎉 to enter!\nHosted by: {ctx.author.mention}",
                            color=self.bot.user.color)
        embed.timestamp = end_time
        embed.set_footer(text="Ends at")
        msg = await ctx.send(embed=embed)
        msg.add_reaction("🎉")
        end_timestamp = datetime.datetime.timestamp(end_time)

        await self.bot.pool.execute("INSERT INTO giveaways (msg_id, ch_id, g_id, end_timestamp, host_id, prize) "
                                    "VALUES $1, $2, $3, $4, $5, $6)", msg.id, ctx.channel.id, ctx.guild.id,
                                    end_timestamp, ctx.author.id, prize)


    @commands.command()
    async def gend(self, message_id:int=None):
        msg_id = 0
        if not message_id:
            all_gws_in_channel = await self.bot.fetch("SELECT * FROM giveaways WHERE ch_id = $1", ctx.channel.id)
            async for msg in ctx.channel.history(limit=50):
                if msg.id in all_gws_in_channel[0]:
                    msg_id += msg.id

        if msg_id == 0:
            if not message_id:
                await ctx.send("I couldn't find any recent giveaways!")
                return
            elif message_id:
                await ctx.send("The giveaway doesn't exist :/")
                return
        msg_id += message_id
        await self.force_end(msg_id)


def setup(bot):
    bot.add_cog(Giveaways(bot))




