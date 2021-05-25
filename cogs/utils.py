import discord
from discord.ext import commands, flags
from classes import indev_check
import asyncio
from classes import CustomBotClass, checks
from num2words import num2words
from constants import emojis
from constants.basic import support_server
import humanize
import datetime


def text_to_emoji(count):
    base = 0x1f1e6
    return chr(base + count)


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
        await suggestion_msg.add_reaction(emojis.white_check_mark)
        await suggestion_msg.add_reaction(emojis.no_entry_sign)
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
    async def poll(self, ctx, *, question):
        messages = [ctx.message]
        answers = []

        def check(m):
            return m.author.id == ctx.author.id and m.channel == ctx.channel and len(
                m.content) <= 100

        for i in range(50):
            messages.append(await ctx.send(f"Say the poll options or say cancel to publish the poll."))

            try:
                options = await self.bot.wait_for("message", check=check, timeout=90.0)
            except asyncio.TimeoutError:
                break

            messages.append(options)

            if options.clean_content.startswith("cancel"):
                break

            answers.append((text_to_emoji(i), options.clean_content))

        try:
            await ctx.channel.delete_messages(messages)
        except BaseException:
            pass

        answer = "\n".join(
            f"{keycap}: {content}" for keycap,
                                       content in answers)
        actual_poll = await ctx.send(f"{ctx.author} asks: {question}\n\n{answer}")
        for emoji, _ in answers:
            await actual_poll.add_reaction(emoji)

    @commands.command()
    async def quickpoll(self, ctx, *questions_and_choices: str):
        if len(questions_and_choices) < 3:
            return await ctx.send("Need at least 1 question with 2 choices.")
        elif len(questions_and_choices) > 21:
            return await ctx.send("You can only have up to 20 choices.")
        perms = ctx.channel.permissions_for(ctx.me)
        if not (perms.read_message_history or perms.add_reactions):
            return await ctx.send("I need Read Message History and Add Reactions permissions.")

        question = questions_and_choices[0]
        choices = [(text_to_emoji(e), v)
                   for e, v in enumerate(questions_and_choices[1:])]

        try:
            await ctx.message.delete()
        except BaseException:
            pass

        body = "\n".join(f"{key}: {c}" for key, c in choices)
        poll = await ctx.send(f"Question: {question}\n\n{body}")
        for emoji, _ in choices:
            await poll.add_reaction(emoji)

    @commands.command()
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def prefix(self, ctx: commands.Context):
        e = discord.Embed(title=f'My prefixes in {str(ctx.guild)}')
        data = await self.bot.pool.fetch("SELECT * FROM prefixes WHERE guild_id=$1", ctx.guild.id)
        desc = ''
        for prefix in data:
            desc = f'{desc}\n:{num2words(data.index(prefix))}: `' + \
                   prefix['prefix'] + '`'
        desc = f'{desc}\n{emojis.heave_plus_sign} adds a new prefix'
        e.description = desc
        message: discord.Message = await ctx.reply(embed=e)
        for prefix in data:
            await message.add_reaction(emojis.numbers[num2words(data.index(prefix)).lower()])

        if not len(data) == 10:
            await message.add_reaction(emojis.heave_plus_sign)

        allowed_emojis = [emojis.heave_plus_sign] + \
                         list(emojis.numbers.values())

        def check(reactions, users):
            return users == ctx.author and str(
                reactions.emoji) in allowed_emojis

        allowed_emojis2 = [emojis.pencil, emojis.no_entry_sign]

        allowed_emojis3 = [emojis.white_check_mark, emojis.no_entry_sign]

        def check3(reactions, users):
            return users == ctx.author and str(
                reactions.emoji) in allowed_emojis2

        def check4(reactions, users):
            return users == ctx.author and str(
                reactions.emoji) in allowed_emojis3

        def check2(message5: discord.Message):
            return message5.author == ctx.author

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            return
        else:
            if reaction.emoji == emojis.heave_plus_sign:
                await ctx.reply(
                    'aight send me da prefix mate! remember, if the prefix is a word, add a space after it, '
                    'and put it in a code block. like: `hey ` or `!`, if you do something like: `hey` then you '
                    'will have to do something like `heyhelp` not `hey help` so mind the space. How to put in '
                    'a code block: put a backtick(that one below escape), then your new prefix and then '
                    'another backtick. easy right?')
                try:
                    message2 = await self.bot.wait_for('message', timeout=60.0, check=check2)
                except asyncio.TimeoutError:
                    return
                else:
                    async with self.bot.pool.acquire() as conn:
                        async with conn.transaction():
                            await conn.execute("INSERT INTO prefixes(guild_id,prefix) VALUES($1,$2)", ctx.guild.id,
                                               message2.content[1:-1])
                            await ctx.reply("Done! the prefix has been added to my list!")
                            return
            emoji = emojis.numbers_inverted[reaction.emoji]
            prefix = data[emoji]['prefix']
            if emoji == emojis.heave_plus_sign and len(data) == 10:
                return
            desc = f'{emojis.no_entry_sign} Delete this prefix\n{emojis.pencil} Edit this prefix'
            e = discord.Embed(
                title="What to do with this prefix?",
                description=desc)
            message2 = await ctx.reply(embed=e)
            await message2.add_reaction(emojis.no_entry_sign)
            await message2.add_reaction(emojis.pencil)
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check3)
            except asyncio.TimeoutError:
                return
            else:
                if reaction.emoji == emojis.pencil:
                    await ctx.reply(
                        'aight send me da prefix mate! remember, if the prefix is a word, add a space after it, '
                        'and put it in a code block. like: `hey ` or `!`, if you do something like: `hey` then you '
                        'will have to do something like `heyhelp` not `hey help` so mind the space. How to put in '
                        'a code block: put a backtick(that one below escape), then your new prefix and then '
                        'another backtick. easy right?')
                    try:
                        message2 = await self.bot.wait_for('message', timeout=60.0, check=check2)
                    except asyncio.TimeoutError:
                        return
                    else:
                        async with self.bot.pool.acquire() as conn:
                            async with conn.transaction():
                                await conn.execute("UPDATE prefixes SET prefix=$1 WHERE guild_id=$2 AND prefix=$3",
                                                   message2.content[1:-1],
                                                   ctx.guild.id, prefix)
                                await ctx.reply("Done! the prefix has been edited!")
                                return
                elif reaction.emoji == emojis.no_entry_sign:
                    e = discord.Embed(
                        title="Sure??",
                        description=f"Are you sure you want to delete the prefix `{prefix}`?")
                    message3: discord.Message = await ctx.reply(embed=e)
                    await message3.add_reaction(emojis.white_check_mark)
                    await message3.add_reaction(emojis.no_entry_sign)
                    try:
                        reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check4)
                    except asyncio.TimeoutError:
                        return
                    else:
                        if reaction.emoji == emojis.no_entry_sign:
                            await ctx.reply("Ok! I will not delete this prefix")
                            return
                        elif reaction.emoji == emojis.white_check_mark:
                            async with self.bot.pool.acquire() as conn:
                                async with conn.transaction():
                                    await conn.execute("DELETE FROM prefixes WHERE guild_id=$1 AND prefix=$2",
                                                       ctx.guild.id, prefix)
                                    await ctx.reply("okey! that prefix has been deleted!")

    @commands.command(aliases=['sniper'])
    @commands.guild_only()
    async def snipe(self, ctx, index: int = 1, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                data2 = await conn.fetch("SELECT * FROM logs WHERE channel_id=$1 AND TYPE=0", channel.id)
                try:
                    select_number = -index
                    select = data2[select_number]
                except IndexError:
                    await ctx.reply(f"Too big or Too small index `{index}`")
                    return
                e = discord.Embed(title=select['reason'][18:len(
                    select['reason'])], description=select['msg'], colour=discord.Color.random())
                await ctx.reply(embed=e)

    @commands.command(aliases=['esnipe', 'esniper'])
    @commands.guild_only()
    @indev_check.command_in_development()
    async def editsnipe(self, ctx, index: int = 1, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                data2 = await conn.fetch("SELECT * FROM logs WHERE channel_id=$1 AND TYPE=1", channel.id)
                try:
                    select_number = -index
                    select = data2[select_number]
                except IndexError:
                    await ctx.reply(f"Too big or Too small index `{index}`")
                    return
                e = discord.Embed(title=select['reason'][18:len(
                    select['reason'])], description=select['msg'], colour=discord.Color.random())
                await ctx.reply(embed=e)

    @commands.command(name="userinfo", aliases=["ui"])
    async def userinfo(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        embed = discord.Embed(title=f"Information on {member}", description=member.mention, color=self.bot.color)
        perms_list = []
        for permission, value in member.guild_permissions:
            if value:
                perms_list.append(permission.replace("_", " ").title())
        for perm in perms_list:
            ignored_perms = ["Add Reactions", "Priority Speaker", "Stream", "Embed Links", "Read Message History",
                             "External Emojis", "Connect", "Speak", "Mute Members", "Deafen Members", "Move Members",
                             "Use Voice Activation", "Change Nickname", "Manage Webhooks", "Request To Speak"]
            if perm in ignored_perms:
                perms_list.pop(perms_list.index(perm))
        permissions_str = ", ".join(perm for perm in perms_list)
        joined = humanize.precisedelta(datetime.datetime.now() - member.joined_at)
        created = humanize.precisedelta(datetime.datetime.now() - member.created_at)
        embed.add_field(name=f"Joined {ctx.guild.name} on", value=joined)
        embed.add_field(name="Created account on", value=created)
        embed.add_field(name="Permissions", value=permissions_str)
        embed.add_field(name="Status",
                        value=str(member.status).replace("dnd", "<:status_dnd:844215897206947930> DND").replace(
                            "do_not_disturb", "<:status_dnd:844215897206947930> DND").replace("online",
                                                                                              "Online <:status_online:844215865951911968>").replace(
                            "idle", "Idle <:status_idle:844216072265531452>").replace("offline",
                                                                                      "Offline <:status_offline:844216076543721523>"))
        embed.add_field(name=f"Roles [{len(member.roles)}]", value=member.top_role.mention)
        await ctx.send(embed=embed)

    @flags.add_flag("--role", type=discord.Role)
    @flags.add_flag("--discrim", type=str)
    @flags.add_flag("--name", type=str)
    @flags.add_flag("--activity", type=str)
    @flags.add_flag("--status", type=str)
    @commands.command(cls=flags.FlagCommand)
    async def memberswith(self, ctx, **flags):
        conv_dict = {}
        total_list = ctx.guild.members

        async def filter_role(conv_dict, flags, total_list):
            try:
                role = flags["role"]
                conv_dict["role"] = role.id
            except KeyError:
                conv_dict["role"] = ctx.guild.default_role.id
            finally:
                for member in total_list:
                    role = ctx.guild.get_role(int(conv_dict["role"]))
                    if role not in member.roles:
                        total_list.pop(total_list.index(member))

        async def filer_discrim(conv_dict, flags, total_list):

            try:
                discriminator = flags["discrim"]
                conv_dict["discrim"] = discriminator
            except KeyError:
                conv_dict["discrim"] = "0"
            finally:
                if conv_dict["discrim"] != "0":
                    discriminator = conv_dict["discrim"]
                    for member in total_list:
                        if not str(discriminator) == str(member.discriminator):
                            total_list.pop(total_list.index(member))

        async def filter_name(conv_dict, flags, total_list):
            try:
                name = flags["name"]
                conv_dict["name"] = name
            except KeyError:
                conv_dict["name"] = " "
            finally:
                name = conv_dict["name"]
                if conv_dict["name"] != " ":
                    for member in total_list:
                        if not str(name) == str(member.name):
                            total_list.pop(total_list.index(member))

        async def filter_activity(conv_dict, flags, total_list):
            try:
                activity = flags["activity"]
                conv_dict["activity"] = activity
            except KeyError:
                conv_dict["activity"] = " "
            finally:
                activity = conv_dict["activity"]
                if conv_dict["activity"] != " ":
                    for member in total_list:
                        if not str(activity) in str(member.activities):
                            total_list.pop(total_list.index(member))

        async def filter_status(conv_dict, flags, total_list):
            try:
                status = flags["status"]
                conv_dict["status"] = status
            except KeyError:
                conv_dict["status"] = " "
            finally:
                status = conv_dict["status"]
                valid_status = ["online", "dnd", "do not disturb", "idle"]
                if status.lower() not in valid_status:
                    await ctx.send("That is not a valid status.")
                    return
                if conv_dict["status"] != " ":
                    for member in total_list:
                        if not str(member.status) == status:
                            total_list.pop(total_list.index(member))

        if flags["role"]:
            await filter_role(conv_dict, flags, total_list)
        if flags["activity"]:
            await filter_activity(conv_dict, flags, total_list)
        if flags["name"]:
            await filter_name(conv_dict, flags, total_list)
        if flags["discrim"]:
            await filter_name(conv_dict, flags, total_list)
        if flags["status"]:
            await filter_status(conv_dict, flags, total_list)

        final_str = " | ".join(member.mention for member in total_list)
        embed = discord.Embed(title="Members with", description=final_str, color=self.bot.color)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Utility(bot))
