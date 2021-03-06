import discord
from discord.ext import commands
import datetime
import humanize
import random
from matplotlib import pyplot as plt


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
    async def gstart(self, ctx, time, winners: int, *, prize):
        duration = self.time_converter(time)
        if not duration:
            await ctx.send("Invalid time format. Example time usage: `5d`, `2m`, `30s`, `2h`")
            return
        if duration > datetime.timedelta(days=30):
            await ctx.send("Time shouldn't be bigger than 30 days!")
            return
        end_time = datetime.datetime.now() + duration
        embed = discord.Embed(
            title=prize,
            description=f"React with ???? to enter!\nTime Remaining: {humanize.precisedelta(duration)}Hosted by: {ctx.author.mention}",
            color=self.bot.user.color)
        embed.timestamp = end_time
        embed.set_footer(text="Ends at")
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("????")
        end_timestamp = datetime.datetime.timestamp(end_time)

        await self.bot.pool.execute("INSERT INTO giveaways (msg_id, ch_id, g_id, end_timestamp, host_id, prize, winners) VALUES ($1, $2, $3, $4, $5, $6, $7)", msg.id, ctx.channel.id, ctx.guild.id,
                                    end_timestamp, ctx.author.id, prize, winners)
        while datetime.datetime.now() < end_time:
            new_emb: discord.Embed = msg.embeds[0].copy()
            new_emb.description = f"React with ???? to enter!\nTime Remaining: {humanize.precisedelta(datetime.datetime.now() - end_time)}Hosted by: {ctx.author.mention}"
            await msg.edit(embed=new_emb)

    @commands.command()
    async def gend(self, ctx, id: int = None):
        msg_id = 0
        if id is None:
            all_gws = await self.bot.pool.fetch("SELECT msg_id FROM giveaways WHERE ch_id= $1", ctx.channel.id)
            async for message in ctx.channel.history(limit=50):
                if message.id in all_gws:
                    msg_id = message.id
                    break

            if msg_id is None:
                await ctx.send("I couldn't find any recent giveaways!")
                return
        await self.force_end(id)

    @commands.command()
    async def lucky_draw(self, ctx: commands.Context):
        members_bots = ctx.guild.members
        members = []
        for member in members_bots:
            if member.bot:
                continue
            members.append(member)
        rando_user = random.choice(members)
        await ctx.reply(f"GGs {rando_user.mention} HAS WON THE LUCKY DRAW")

    @commands.command()
    async def luck(self, ctx: commands.Context, iterations: int):
        if iterations > 10000:
            await ctx.reply("NONONONONO I DONT WANNA CRASH")
            return
        members_bots = ctx.guild.members
        members = []
        for member in members_bots:
            if member.bot:
                continue
            members.append(member)
        luck_list = []
        for i in range(iterations):
            rando_user: discord.Member = random.choice(members)
            luck_list.append(rando_user)
        final_str = ""
        biggest_no = -1
        biggest_user = ""
        for member in members:
            final_str = f'{final_str}\n`{member.display_name}`: {luck_list.count(member)}'
            if luck_list.count(member) > biggest_no:
                biggest_no = luck_list.count(member)
                biggest_user = member
        final_str = f'{final_str}\n`{biggest_user.display_name}` has the highest luck, with {biggest_no} choices in {iterations}'
        await ctx.reply(final_str)




def setup(bot):
    bot.add_cog(Giveaways(bot))
