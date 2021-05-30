import discord
from discord.ext import commands


async def get_prefix(eclipse, message):
    base = []
    if message.author.id in basic.owners:
        base.append("")
    if not message.guild:
        base.append("e! ")
        base.append("e!")
        return base
    base.extend(eclipse.prefixes[message.guild.id])
    return commands.when_mentioned_or(*base)(bot, message)


class Prefixes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
                    new_prefix = message2.content[1:-1]
                    async with self.bot.pool.acquire() as conn:
                        async with conn.transaction():
                            await conn.execute("INSERT INTO prefixes(guild_id,prefix) VALUES($1,$2)", ctx.guild.id,
                                               new_prefix)

                    og_prefixes = self.bot.prefixes[ctx.guild.id]
                    og_prefixes.append(new_prefix)
                    self.bot.prefixes[ctx.guild.id] = og_prefixes

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
                        new_prefix = message2.content[1:-1]
                        async with self.bot.pool.acquire() as conn:
                            async with conn.transaction():
                                await conn.execute("UPDATE prefixes SET prefix=$1 WHERE guild_id=$2 AND prefix=$3",
                                                   message2.content[1:-1],
                                                   ctx.guild.id, prefix)

                        og_prefixes = self.bot.prefixes[ctx.guild.id]
                        og_prefixes.pop(og_prefixes.index(prefix))
                        og_prefixes.append(new_prefix)
                        self.bot.prefixes[ctx.guild.id] = og_prefixes
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
                                    og_prefixes = self.bot.prefixes[ctx.guild.id]
                                    og_prefixes.pop(og_prefixes.index(prefix))
                                    await ctx.reply("That prefix has been deleted!")

