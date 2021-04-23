import discord
import datetime
import humanize
import random
from discord.ext import commands


class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def force_gend(self, gw):
        guild = self.bot.get_guild(gw["guild_id"])
        ch = guild.get_channel(gw["channel_id"])
        msg = await ch.fetch_message(gw["msg_id"])
        host = guild.get_member(gw["host"])
        prize = gw["prize"]
        winners = gw["winners"]
        new_embed = msg.embeds[0].copy()
        reactions = msg.reactions[0]
        raffle = await reactions.users().flatten()
        raffle.pop(raffle.index(self.bot.user))
        if winners > 1:
            try:
                winner = random.choice(raffle)
                winner_str = winner.mention
            except Exception:
                await ch.send(f"There were no entrants to the giveaway lol\n {msg.jump_url}")
                return
        else:
            new_list = []
            for entrant in raffle:
                new_list.append(entrant.mention)
            final_set = set(new_list)
            winner_list = random.sample(final_set, winners)
            winner_str = ""
            for win in winner_list:
                winner_str += f"{win.mention}, "

        new_embed.description = f"Winner(s): {winner_str}\n Hosted by: {host.mention}"
        new_embed.timestamp = datetime.datetime.now()
        if winners > 1:
            new_embed.set_footer(text=f"{winners} winners • Ended at")
        else:
            new_embed.set_footer(text="Ended at")
        cleaned_prize = ""
        for word in prize:
            for i in word:
                cleaned_prize += f"{i}\u200b"
        await ch.send(f"🎉 Congratulations {winner_str}! You won **{cleaned_prize}**! \n {msg.jump_url}")
        await self.bot.pool.execute("DELETE FROM giveaways WHERE msg_id = $1", gw["msg_id"])

    @commands.command(brief="Starts a GIVEAWAY")
    @commands.cooldown(1, 15, commands.BucketType.member)
    async def gstart(self, ctx, time, winners, *, prize):
        def convert(t):
            pos = ["s", "m", "h", "d"]

            time_dict = {"s": 1, "m": 60, "h": 3600, "d": 3600 * 24}

            unit = t[-1]

            if unit not in pos:
                return -1
            try:
                val = int(time[:-1])
            except BaseException:
                return -2

            return val * time_dict[unit]

        seconds_duration = convert(time)
        if seconds_duration == -1:
            await ctx.send("Failed to parse time. Please try again")
            return
        if seconds_duration == -2:
            await ctx.send("Failed to parse time. Please try again")
            return
        duration = datetime.timedelta(seconds=seconds_duration)
        if duration > datetime.timedelta(days=30):
            await ctx.send("Time too long, maximum value is 30 days")
            return

        start_time = datetime.datetime.now()
        end_time = start_time + duration
        duration_humanized = humanize.naturaldelta(duration)
        iso = end_time.isoformat()
        embed = discord.Embed(
            title=prize,
            description=f"React with 🎉 to enter!\nTime Left: [Timer](https://www.timeanddate.com/countdown/generic?iso={iso}Z&p0=%3A&msg=test&font=sanserif&csz=1\nWinners: **{winners[:-1]} winners**\nHosted By: {ctx.author.mention}",
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

    @commands.command(name="gend", brief="Ends an ongoing giveaway")
    async def gend(self, ctx, id: int = None):
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
            msg_id += id
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                gw = await conn.fetch("SELECT 1 FROM giveaways WHERE msg_id = $1", msg_id)
                await self.force_gend(gw)

    @commands.command(brief="Rerolls a giveaway")
    @commands.cooldown(1, 5, commands.BucketType.member)
    async def greroll(self, ctx, id=None):
        msg_id = 0
        if not id:
            async with self.bot.pool.acquire() as conn:
                async with conn.transaction():
                    async for msg in ctx.channel.history(limit=50):
                        res = await conn.fetch("SELECT * FROM giveaways WHERE msg_id = $1", msg_id)
                        if res is None:
                            continue
                        msg_id += res[0]["msg_id"]
                        break
        if msg_id == 0:
            if not id:
                await ctx.send("I couldn't find any recent giveaways!")
                return
            msg_id += id

        gw_msg = await ctx.channel.fetch_message(msg_id)
        if gw_msg is None:
            await ctx.send("I couldn't find the giveaway :/")
            return
        reactions = gw_msg.reactions[0]
        raffle = await reactions.users().flatten()
        raffle.pop(raffle.index(self.bot.user))
        try:
            winner = random.choice(raffle)
        except Exception:
            await ctx.send(f"There were no entrants to the giveaway lol\n {gw_msg.jump_url}")
            return
        cleaned_prize = ""
        for word in gw_msg.embeds[0].title:
            for i in word:
                cleaned_prize += f"{i}\u200b"
        await ctx.send(f"🎉 Congratulations {winner.mention}!, you won **{cleaned_prize}**! \n {gw_msg.jump_url}")


def setup(bot):
    bot.add_cog(Giveaway(bot))
