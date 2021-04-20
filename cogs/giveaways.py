import discord
import datetime
import humanize
import re
import random
from discord.ext import commands
from discord.ext import tasks


class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def gend(self, gw):
        guild = self.bot.get_guild(gw["guild_id"])
        ch = guild.get_channel(gw["channel_id"])
        msg = ch.fetch_message(gw["msg_id"])
        host = guild.get_member(gw["host"])
        prize = gw["prize"]
        winners = gw["winners"]
        new_embed = msg.embeds[0].copy()
        new_embed.description = f"React with 🎉 to enter!\n**Giveaway Ended**\nWinners: **{winners} winners**\nHosted By: {host.mention}"
        await msg.edit(embed=new_embed)
        reactions = msg.reactions[0]
        raffle = await reactions.users().flatten()
        raffle.pop(raffle.index(self.bot.user))
        try:
            winner = random.choice(raffle)
        except Exception:
            await ch.send(f"There were no entrants to the giveaway lol\n {msg.jump_url}")
            return
        cleaned_prize = ""
        for word in prize:
            for i in word:
                cleaned_prize += f"{i}\u200b"
        await ch.send(f"🎉 Congratulations {winner.mention}!, you won **{cleaned_prize}**! \n {msg.jump_url}")




    @commands.command(brief="Starts a GIVEAWAY")
    @commands.cooldown(1, 15, commands.BucketType.member)
    async def gstart(self, ctx, time, winners ,*, prize):
        def convert(t):
            pos = ["s", "m", "h", "d"]

            time_dict = {"s": 1, "m": 60, "h": 3600, "d": 3600 * 24}

            unit = t[-1]

            if unit not in pos:
                return -1
            try:
                val = int(time[:-1])
            except:
                return -2

            return val * time_dict[unit]

        seconds_duration = convert(time)
        if seconds_duration == -1:
            await ctx.send("Failed to parse time. Please try again")
            return
        if seconds_duration == -2:
            await ctx.send("Failed to parse time. Please try again")
            return
        duration = datetime.timedelta(seconds = seconds_duration)
        if duration > datetime.timedelta(days = 30):
            await ctx.send("Time too long, maximum value is 30 days")
            return
        len_winners = winners[:-1]
        start_time = datetime.datetime.now()
        end_time = start_time + duration
        duration_humanized = humanize.naturaldelta(duration)
        embed = discord.Embed(title=prize,
                              description=f"React with 🎉 to enter!\nTime Left: **{duration_humanized}**\nWinners: **{winners[:-1]} winners**\nHosted By: {ctx.author.mention}",
                              color=discord.Color.random())
        embed.timestamp = end_time
        embed.set_footer(text="Ending Time:")
        gw_msg = await ctx.send("🎉 **GIVEAWAY** 🎉", embed=embed)
        await gw_msg.add_reaction("🎉")
        end_timestamp = end_time.timestamp()
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "INSERT INTO giveaways (msg_id, channel_id, guild_id, host, winners, end_time, prize) VALUES ($1, $2, $3, $4, $5, $6, $7)",
                    gw_msg.id, ctx.channel.id, ctx.guild.id, ctx.author.id, int(winners[:-1]), end_timestamp, prize)

    @commands.command(brief="Rerolls the giveaway")
    @commands.cooldown(1, 5, commands.BucketType.member)
    async def greroll(self, ctx, id=None):
        msg_id = 0
        if not id:
            async for msg in ctx.channel.history(limit=50):
                if msg.author == self.bot.user and "🎉" in msg.content:
                    if msg.embeds:
                        msg_id += msg.id
                        break
        if msg_id == 0:
            if not id:
                await ctx.send("I couldn't find any recent giveaways!")
                return
            else:
                msg_id += id
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                gw = await conn.fetch("SELECT 1 FROM giveaways WHERE msg_id = $1", msg_id)
                await self.gend(gw)


        @tasks.loop(seconds = 5)
        async def end_gws(self):
            await self.bot.wait_until_ready()
            async with self.bot.pool.acquire() as conn:
                async with conn.transaction():
                    res = await conn.fetch("SELECT * FROM giveaways")
            for row in res:
                end_time = datetime.datetime.fromtimestamp(row["end_time"])
                if datetime.datetime.now() - end_time < datetime.timedelta(seconds = 5):
                    await self.gend(row)

        end_gws.start()


def setup(bot):
    bot.add_cog(Giveaway(bot))
