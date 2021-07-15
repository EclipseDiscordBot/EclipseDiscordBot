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


class Utility(commands.Cog, description="Small but useful commands"):
    def __init__(self, bot: CustomBotClass.CustomBot):
        self.bot = bot

    @commands.command(aliases=['av'],
                      brief="Gives the avatar of the user mentioned")
    async def avatar(self, ctx, user: discord.User = None):
        """
    Gives the avatar of the user mentioned. Defaults to the author if no one is mentioned.
        :param ctx:
        :param user: the user whose avatar will be shown
        :return: the avatar of the member
        """
        user = user or ctx.author
        embed = discord.Embed(title=" ", description=" ", color=0x2F3136)
        embed.set_image(url=user.avatar.url)
        await ctx.reply(embed=embed)

    @commands.command(aliases=["ct", "timedif", "timediff"],
                      brief="Gives the time difference between two Discord object IDs")
    async def snowflake(self, ctx, id1: int, id2: int):
        """
    Gives the time difference between two Discord object IDs
        :param ctx:
        :param id1: Discord ID 1
        :param id2: Discord ID 2
        :return: The time difference between the two objects
        """
        one_time = discord.utils.snowflake_time(id1)
        two_time = discord.utils.snowflake_time(id2)
        diff = two_time - one_time
        seconds = diff.total_seconds()
        seconds_str = str(seconds)
        final = abs(int(seconds_str))
        embed = discord.Embed(title=final, color=self.bot.color)
        embed.add_field(
            name=str(id1),
            value=f"**Created time:** {humanize.naturaltime(one_time)}")
        embed.add_field(
            name=str(id2),
            value=f"**Created time:** {humanize.naturaltime(two_time)}")

    @commands.command(name="suggest",
                      brief="Suggest a command/feature to the developers")
    @commands.cooldown(1, 900, discord.ext.commands.BucketType.user)
    async def suggest(self, ctx: commands.Context, *, suggestion):
        """
    Suggests a command/feature to be voted on and (maybe) be added.
        :param ctx:
        :param suggestion: the suggestion
        :return:
        """
        suggestion_channel = self.bot.get_channel(840528236597477377)
        embed = discord.Embed(title="New Suggestion",
                              description=f"```yaml\n{suggestion}```",
                              color=self.bot.color)
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"From {ctx.guild.name}")
        embed.timestamp = ctx.message.created_at
        suggestion_msg = await suggestion_channel.send(embed=embed)
        await suggestion_msg.add_reaction(emojis.white_check_mark)
        await suggestion_msg.add_reaction(emojis.no_entry_sign)
        await ctx.reply(
            f"Done! you can check the your suggestion's reviews in {support_server} {suggestion_channel.mention}")

    @commands.Cog.listener("on_message")
    async def on_msg(self, msg: discord.message):
        """
        The Auto Responder for Math Problems
        :param msg:
        :return:
        """
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

    @commands.command(name="ar",
                      aliases=['autoresponse'],
                      brief="Set various auto responders on or off")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def ar(self, ctx, option: str, toggle: bool):
        """
        Toggles auto responders on/off
        Currently, all the options are:
            - math

        :param ctx:
        :param option:
        :param toggle:
        :return:
        """
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                if option == "math":
                    await conn.execute("UPDATE config SET math=$1 WHERE server_id=$2", toggle, ctx.guild.id)
                else:
                    await ctx.reply("unknown cmd!")
                    return
        await ctx.reply("done!")

    @commands.command(name="poll",
                      brief="Create a poll with different options")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def poll(self, ctx, *, question):
        """
        An interactive poll command
        :param ctx:
        :param question:
        :return:
        """
        messages = [ctx.message]
        answers = []

        def check(m):
            return m.author.id == ctx.author.id and m.channel == ctx.channel and len(
                m.content) <= 100

        for i in range(50):
            messages.append(await ctx.send(f"Say the poll options or say `cancel` to publish the poll."))

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
        embed = discord.Embed(
            title=question,
            color=self.bot.color,
            description=answer)
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
        actual_poll = await ctx.send(embed=embed)
        for emoji, _ in answers:
            await actual_poll.add_reaction(emoji)

    @commands.command(name="quickpoll",
                      brief="Quickly create a poll with a single command")
    async def quickpoll(self, ctx, *questions_and_choices: str):
        """
        Quickly create a poll with a single command
        :param ctx:
        :param questions_and_choices:
        :return:
        """
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
        embed = discord.Embed(
            title=question,
            color=self.bot.color,
            description=body)
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
        actual_poll = await ctx.send(embed=embed)
        for emoji, _ in choices:
            await actual_poll.add_reaction(emoji)

    @commands.command(name="prefix", brief="Change/view the guild's prefixes")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def prefix(self, ctx: commands.Context):
        """
        An interactive command to change/view prefix
        :param ctx:
        :return:
        """
        e = discord.Embed(title=f'My prefixes in {str(ctx.guild.name)}')
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
                await ctx.reply("Alright, send me the prefix. "
                                "Surround the prefix with backticks so I can detect spaces backticks (`). ")
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
                    await ctx.reply("Alright, send me the prefix. "
                                    "Surround the prefix with backticks so I can detect spaces backticks (`). ")
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
                                    await ctx.reply("That prefix has been deleted!")

    @commands.command(name="userinfo", aliases=["ui"])
    async def userinfo(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        embed = discord.Embed(
            title=f"Information on {member}",
            description=member.mention,
            color=self.bot.color)
        perms_list = []
        for permission, value in member.guild_permissions:
            if value:
                perms_list.append(permission.replace("_", " ").title())
        for perm in perms_list:
            ignored_perms = [
                "Add Reactions",
                "Priority Speaker",
                "Stream",
                "Embed Links",
                "Read Message History",
                "External Emojis",
                "Connect",
                "Speak",
                "Mute Members",
                "Deafen Members",
                "Move Members",
                "Use Voice Activation",
                "Change Nickname",
                "Manage Webhooks",
                "Request To Speak"]
            if perm in ignored_perms:
                perms_list.pop(perms_list.index(perm))
        permissions_str = ", ".join(perm for perm in perms_list)
        joined = humanize.precisedelta(
            datetime.datetime.utcnow() -
            member.joined_at.replace(
                tzinfo=None))
        created = humanize.precisedelta(
            datetime.datetime.utcnow() -
            member.created_at.replace(
                tzinfo=None))
        embed.add_field(name=f"Joined {ctx.guild.name} on", value=joined)
        embed.add_field(name="Created account on", value=created)
        embed.add_field(name="Permissions", value=permissions_str)
        embed.add_field(
            name="Status",
            value=str(
                member.status).replace(
                "dnd",
                "DND <:status_dnd:844215897206947930>").replace(
                "do_not_disturb",
                "<:status_dnd:844215897206947930> DND").replace(
                    "online",
                    "Online <:status_online:844215865951911968>").replace(
                        "idle",
                        "Idle <:status_idle:844216072265531452>").replace(
                            "offline",
                "Offline <:status_offline:844216076543721523>"))
        embed.add_field(
            name=f"Roles [{len(member.roles)}]",
            value=member.top_role.mention)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Utility(bot))
