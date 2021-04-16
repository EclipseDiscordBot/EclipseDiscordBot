import discord
from discord.ext import commands
import datetime
import humanize
import re
import asyncio
import random


class giveaways(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Starts a GIVEAWAY")
    @commands.cooldown(1, 15, commands.BucketType.member)
    async def gstart(self, ctx, time, winners, *, prize):
        if time.endswith('s'):
            seconds = time[:-1]
            duration = datetime.timedelta(seconds=int(seconds))
        if time.endswith('m'):
            minutes = time[:-1]
            duration = datetime.timedelta(minutes=int(minutes))
        elif time.endswith('h'):
            hours = time[:-1]
            duration = datetime.timedelta(hours=int(hours))
        elif time.endswith('d'):
            days = time[:-1]
            duration = datetime.timedelta(days=int(days))
        start_time = datetime.datetime.now()
        end_time = start_time + duration
        duration_humanized = humanize.naturaldelta(duration)
        embed = discord.Embed(title=prize,
                              description=f"React with 🎉 to enter!\nTime Left: **{duration_humanized}**\nHosted By: {ctx.author.mention}",
                              color=discord.Color.random())
        embed.timestamp = end_time
        embed.set_footer(text="Ending Time:")
        gw_msg = await ctx.send("🎉 **GIVEAWAY** 🎉", embed=embed)
        await gw_msg.add_reaction("🎉")
        while datetime.datetime.now() < end_time:
            await asyncio.sleep(
                duration.total_seconds() / 10)  # edits the embed only 10 times regardless of duration to prevent ratelimitation
            remaining_time = humanize.precisedelta((end_time - datetime.datetime.now()).total_seconds())
            new_embed = gw_msg.embeds[0].copy()
            new_embed.description = f"React with 🎉 to enter!\nTime Left: **{remaining_time}**\nHosted By: {ctx.author.mention}"
            await gw_msg.edit(embed=new_embed)
        new_embed = gw_msg.embeds[0].copy()
        new_embed.description = f"React with 🎉 to enter!\n**Giveaway Ended**\nHosted By: {ctx.author.mention}"
        await gw_msg.edit(embed=new_embed)
        new_msg = await ctx.channel.fetch_message(gw_msg.id)
        reactions = new_msg.reactions[0]
        raffle = await reactions.users().flatten()
        raffle.pop(raffle.index(self.bot.user))
        try:
            winner = random.choice(raffle)
        except Exception:
            await ctx.send(f"There were no entrants to the giveaway lol\n {gw_msg.jump_url}")
            return
        cleaned_prize = ""
        for word in prize:
            for i in word:
                cleaned_prize += f"{i}\u200b"
        await ctx.send(f"🎉 Congratulations {winner.mention}!, you won **{cleaned_prize}**! \n {new_msg.jump_url}")

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
        gw_msg = await ctx.channel.fetch_message(msg_id)
        new_embed = gw_msg.embeds[0].copy()
        prize = gw_msg.embeds[0].title
        e = [int(x) for x in re.findall(r'<@!?([0-9]+)>', new_embed.description)]
        host = ctx.guild.get_member(e[0])
        new_embed.description = f"React with 🎉 to enter!\n**Giveaway Ended**\nHosted By: {host.mention}"
        await gw_msg.edit(embed=new_embed)
        new_msg = await ctx.channel.fetch_message(gw_msg.id)
        reactions = new_msg.reactions[0]
        raffle = await reactions.users().flatten()
        raffle.pop(raffle.index(self.bot.user))
        try:
            winner = random.choice(raffle)
        except Exception:
            await ctx.send(f"There were no entrants to the giveaway lol\n {gw_msg.jump_url}")
            return
        cleaned_prize = ""
        for word in prize:
            for i in word:
                cleaned_prize += f"{i}\u200b"
        await ctx.send(f"🎉 Congratulations {winner.mention}!, you won **{cleaned_prize}**! \n {new_msg.jump_url}")



def setup(bot):
    bot.add_cog(giveaways(bot))
