import discord
from discord.ext import commands
from classes import indev_check
import asyncio
from classes import CustomBotClass
from num2words import num2words

from constants.basic import support_server


class Utility(commands.Cog):
    def __init__(self, bot: CustomBotClass.CustomBot):
        self.bot = bot

    @commands.command(aliases=['av'],
                      brief="gives the mentioned user(you if nobody is mentioned)'s avatar")
    async def avatar(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        embed = discord.Embed(title=" ", description=" ", color=0x2F3136)
        embed.set_image(url=member.avatar_url)
        await ctx.reply(embed=embed)

    @commands.command(aliases=["ct", "timedif", "timediff"],
                      brief="gives the difference between two ids (any ids)")
    async def snowflake(self, ctx, win_id: int, dm_id: int):
        win_time = discord.utils.snowflake_time(win_id)
        dm_time = discord.utils.snowflake_time(dm_id)
        diff = dm_time - win_time
        seconds = diff.total_seconds()
        seconds_str = str(seconds)
        final = abs(int(seconds_str))
        await ctx.send(f"Difference between the two message ID's is `{final}` seconds!")

    @commands.command(name="suggest", brief="Suggest a command to the devs")
    @commands.cooldown(1, 900, discord.ext.commands.BucketType.user)
    async def suggest(self, ctx: commands.Context, *, suggestion=None):
        if suggestion is None:
            def chek(u1):
                return u1.author == ctx.author

            await ctx.reply(
                "Great! your suggestion is valuable! Now send what the new suggestion will do in brief in **1 SINGLE MESSAGE** \n\n **Pro tip: using shift+enter creates a new line without sending the message**")
            try:
                message = await self.bot.wait_for('message', timeout=60.0, check=chek)
            except asyncio.TimeoutError:
                await ctx.reply("time's up mate, try again!")
                return
            else:
                await ctx.reply("Great! now send some detailed description on the new feature in **1 SINGLE MESSAGE**")
                try:
                    message2 = await self.bot.wait_for('message', timeout=300.0, check=chek)
                except asyncio.TimeoutError:
                    await ctx.reply("time's up mate, try again!")
                    return
                else:
                    await ctx.reply("Great! Sending the suggestion...")
                    brief = message.content
                    detailed = message2.content
        else:
            brief = "Not specified"
            detailed = suggestion
        suggestion_channel = self.bot.get_channel(840528236597477377)
        dsc = f"""


**Brief:** ```{brief}```
**Detailed Description:** ```{detailed}```

"""
        embed = discord.Embed(
            title="New Suggestion",
            description=dsc,
            color=self.bot.color)
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        embed.set_footer(text=f"From {ctx.guild if ctx.guild else None}")
        embed.timestamp = ctx.message.created_at
        suggestion_msg = await suggestion_channel.send(embed=embed)
        await suggestion_msg.add_reaction('✅')
        await suggestion_msg.add_reaction('🚫')
        await ctx.reply(f"Done! you can check the your suggestion's reviews in {support_server} <#834442086513508363>")

    @commands.Cog.listener("on_message")
    async def on_msg(self, msg: discord.message):
        if not msg.guild:
            return
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                data = await conn.fetch("SELECT * FROM config WHERE server_id=$1", msg.guild.id)
                if not data:
                    return
                if not data[0]['math']:
                    return
        if msg.author == self.bot.user:
            return
        try:
            allowed_names = {"sum": sum}
            code = compile(msg.content, "<string>", "eval")
            for name in code.co_names:
                if name not in allowed_names:
                    return
            result = eval(code, {"__builtins__": {}}, allowed_names)
            await msg.reply(result)
        except BaseException:
            return

    @commands.command(name="ar", aliases=['autoresponse'])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def ar(self, ctx, option: str, toggle: bool):
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                if option == "math":
                    await conn.execute("UPDATE config SET math=$1 WHERE server_id=$2", toggle, ctx.guild.id)
                else:
                    await ctx.reply("unknown cmd!")
                    return
        await ctx.reply("done!")

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def poll(self, ctx, que=None, opt0=None, opt1=None, opt2=None, opt3=None, opt4=None, opt5=None, opt6=None,
                   opt7=None,
                   opt8=None, opt9=None, test=None):
        if test is None:
            if que is None:
                await ctx.send('Tell me a question.')
            elif opt0 is None or opt1 is None:
                await ctx.send('need at least 2 options.')
            else:
                listl = [
                    opt0,
                    opt1,
                    opt2,
                    opt3,
                    opt4,
                    opt5,
                    opt6,
                    opt7,
                    opt8,
                    opt9]
                embed = discord.Embed(
                    title=que, description='choose one of these options! \n')
                for i in listl:
                    if i is None:
                        pass
                    else:
                        idn = listl.index(i) + 1
                        embed.add_field(
                            name=':' + num2words(idn) + ':', value=i, inline=False)
                msg = await ctx.send(embed=embed)
                for i in listl:
                    if i is None:
                        pass
                    else:
                        idn = listl.index(i) + 1
                        if idn == 10:
                            await msg.add_reaction('0️⃣')
                        if idn == 1:
                            await msg.add_reaction('1️⃣')
                        if idn == 2:
                            await msg.add_reaction('2️⃣')
                        if idn == 3:
                            await msg.add_reaction('3️⃣')
                        if idn == 4:
                            await msg.add_reaction('4️⃣')
                        if idn == 5:
                            await msg.add_reaction('5️⃣')
                        if idn == 6:
                            await msg.add_reaction('6️⃣')
                        if idn == 7:
                            await msg.add_reaction('7️⃣')
                        if idn == 8:
                            await msg.add_reaction('8️⃣')
                        if idn == 9:
                            await msg.add_reaction('9️⃣')
        else:
            await ctx.send('no more that 9 options.:P')

    @commands.command()
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def prefix(self, ctx, prefix):
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("UPDATE prefixes SET prefix = $1 WHERE guild_id = $2", prefix, ctx.guild.id)
        await ctx.send(f"My prefix in this server has successfully been changed to {prefix}\n\n **TIP:** To include "
                       f"spaces in the prefix do use quotes like {prefix}prefix \"hey \"")

    @commands.command(aliases=['sniper'])
    @commands.guild_only()
    async def snipe(self, ctx, index: int = 1, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                data2 = await conn.fetch("SELECT * FROM logs WHERE channel_id=$1", channel.id)
                try:
                    select_number = -index
                    select = data2[select_number]
                except IndexError:
                    await ctx.reply(f"Too big or Too small index `{index}`")
                    return
                e = discord.Embed(title=select['reason'][19:len(select['reason'])], description=select['msg'],
                                  colour=discord.Color.random())
                await ctx.reply(embed=e)


def setup(bot):
    bot.add_cog(Utility(bot))
