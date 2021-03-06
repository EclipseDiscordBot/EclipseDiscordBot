import asyncio
import random
from classes import CustomBotClass
import aiohttp
from discord.ext import commands
import discord

from constants import emojis, basic


class Fun(commands.Cog):

    def __init__(self, bot: CustomBotClass.CustomBot):
        self.bot = bot

    @commands.command(brief="Chooses a random object from specified options",
                      aliases=["pick", "choose"])
    async def choice(self, ctx, *, options: str):
        options1 = options.split(' ')
        choice = random.choice(options1)
        await ctx.reply(f"I choose..... {choice}")

    @commands.command(brief="Repeats you", aliases=['echo'])
    async def say(self, ctx, *, words: str):
        txt = await commands.clean_content().convert(ctx, words)
        await ctx.reply(txt)

    @commands.command(brief="gives a random meme from r/memes")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def meme(self, ctx):
        random_post = self.bot.memes[random.randint(0, len(self.bot.memes))]
        await ctx.reply(embed=random_post)

    @commands.command(name="dbt",
                      aliases=['discord_bot_token'],
                      brief="Gives a fake random discord bot token")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def dbt(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://some-random-api.ml/bottoken") as r:
                res = await r.json()
                await ctx.reply(res['token'])
                await asyncio.sleep(2)
                await ctx.reply("lol thats a fake bot token :P")

    @commands.command(name="rps", brief="Play rock paper scissors with the bot or with someone else")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def rps(self, ctx, member: discord.Member = None):
        if member is None:
            emoji_name_dict = {
                "Rock": "🪨",
                "Paper": "📰",
                "Scissors": "✂"
            }
            bot_choice = random.choice(list(emoji_name_dict.keys()))
            embed = discord.Embed(title="Rock Paper Scissors", description="**React below to choose!**"
                                                                           "Rock: 🪨"
                                                                           "Paper: 📰"
                                                                           "Scissors: ✂", color=self.bot.color)
            msg = await ctx.send(embed=embed)
            for emo in list(emoji_name_dict.values()):
                await msg.add_reaction(emo)

            def check(reaction, user):
                if reaction.message.id == msg.id:
                    if reaction.emoji in list(emoji_name_dict.values()):
                        if user.id == ctx.author.id:
                            return True
                        else:
                            return False
                    else:
                        return False
                else:
                    return False

            raw_reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=60)
            if str(raw_reaction) == "\U0001faa8":
                user_choice = "Rock"
            elif str(raw_reaction) == "\U0001f4f0":
                user_choice = "Paper"
            elif str(raw_reaction) == "\U00002702":
                user_choice = "Scissors"
            if user_choice == bot_choice:
                reply = f"I chose {bot_choice} and you chose {user_choice}! It's a tie!"
            if user_choice == "Rock":
                if bot_choice == "Paper":
                    reply = "You chose Rock and I chose Paper, I won! :D"
                if bot_choice == "Scissors":
                    reply = "You chose Rock and I chose Scissors, You won!, but I won't let you next time!"
            if user_choice == "Paper":
                if bot_choice == "Rock":
                    reply = "You chose Paper and I chose Rock, You won!, but I won't let you next time!"
                if bot_choice == "Scissors":
                    reply = "You chose Paper and I chose Scissors, I won! :D"
            if user_choice == "Scissors":
                if bot_choice == "Rock":
                    reply = "You chose Scissors and I chose Rock, I won! :D"
                if bot_choice == "Paper":
                    reply = "You chose Scissors and I chose Paper, You won!, but I won't let you next time!"
            embed = msg.embeds[0].copy()
            embed.description += f"\n{reply}"
            await msg.edit(embed=embed)




    @commands.command("hack", aliases=['hk', 'hax'], description="hax the specified person")
    @commands.cooldown(1, 45, commands.BucketType.user)
    async def _hack(self, ctx: commands.Context, user: discord.User):
        success = random.choice([True, False, False, False, False, False, False, False])
        linux_chance = random.choice(
            [True, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
             False, False, False, False, False, False, False, False, False, False, False, False, False, False, False])
        ip = f'{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}'
        if user.id in basic.owners:
            await ctx.reply("Hey! you're not hacking my devs :unamused:, the hack has been reversed onto **YOU**")
            user = ctx.author
            await asyncio.sleep(1)
        message: discord.Message = await ctx.reply(f"Initiating the hack on `{user.display_name}` {emojis.loading}")
        await asyncio.sleep(1)
        await message.edit(content=f"Trying to find `{user.display_name}`'s IP {emojis.loading}")
        await asyncio.sleep(2)
        await message.edit(content=f"Got it! {ip}! {emojis.loading}")
        await asyncio.sleep(0.5)
        await message.edit(content=f"Trying to find open ports! {emojis.loading}")
        await asyncio.sleep(2)
        await message.edit(content=f"Found open ports! `80`, `443`, `25565` {emojis.loading}")
        await asyncio.sleep(0.5)
        await message.edit(content=f"Trying to create payload with msfvenom {emojis.loading}")
        await asyncio.sleep(2)
        await message.edit(content=f"Trying to inject payload {emojis.loading}")
        await asyncio.sleep(0.5)
        if linux_chance:
            await message.edit(
                content=f"Wait WTF! HE USES LINUX! I AM NOT HACKING A FELLOW LINUX USER!!!!!!! `{user.display_name}` Nice! you use linux even if you actually don't!")
            return
        await message.edit(content=f"PAYLOAD INJECTION SUCCESSFUL! DROPPING INTO SHELL {emojis.loading}")
        await asyncio.sleep(2)
        shell_attempts = random.randint(3, 21)
        for i in range(shell_attempts):
            await message.edit(content=f"SHELL ACCESS DENIED, TRYING AGAIN, attempt {i} {emojis.loading}")
            await asyncio.sleep(2)
        if not success:
            await message.edit(
                content=f"OH NO, PAYLOAD WAS DELETED BY ANTIVIRUS! `{user.display_name}` got lucky :unamused:")
            return
        await message.edit(content=f"SHELL ACCESS GRANTED! {emojis.loading}")
        await asyncio.sleep(0.5)
        await message.edit(content=f"Trying to get into edge's cookies(wtf they use edge) {emojis.loading}")
        await asyncio.sleep(1)
        await message.edit(content=f"got session token, trying it out {emojis.loading}")
        await asyncio.sleep(1)
        random_number = random.randint(0, 10000)
        random_number2 = random.randint(0, 10000)
        await message.edit(
            content=f"EMAIL HACK SUCCESSFUL! \nEmail: `{user.display_name}{random_number}@hotmail.com` \nPassword: `Ilikecyberpunk2077cuz{random_number2}`")


def setup(bot):
    bot.add_cog(Fun(bot))
