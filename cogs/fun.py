import asyncio
import random
from classes import CustomBotClass
import aiohttp
from prsaw import RandomStuff
from discord.ext import commands
import discord

rs = RandomStuff()

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
            embed = discord.Embed(title="Rock Paper Scissors", description="", color=self.bot.color)
            msg = await ctx.send(embed=embed)
            for emo in list(emoji_name_dict.values()):
                await msg.add_reaction(emo)

            def check(reaction, user):
                if reaction.message.id == msg.id:
                    if reaction.emoji in list(emoji_name_dict.values()):
                        return True
                    else:
                        return False
                else:
                    return False

            user_emoji = await self.bot.wait_for('reaction_add', check=check)
            user_choice = emoji_name_dict[user_emoji]
            if user_choice == bot_choice:
                await ctx.send(f"I chose {bot_choice} and you chose {user_choice}! It's a tie!")
            if user_choice == "Rock":
                if bot_choice == "Paper":
                    await ctx.send("You chose Rock and I chose Paper, I won! :D")
                if bot_choice == "Scissors":
                    await ctx.send("You chose Rock and I chose Scissors, You won!, but I won't let you next time!")
            if user_choice == "Paper":
                if bot_choice == "Rock":
                    await ctx.send("You chose Paper and I chose Rock, You won!, but I won't let you next time!")
                if bot_choice == "Scissors":
                    await ctx.send("You chose Paper and I chose Scissors, I won! :D")
            if user_choice == "Scissors":
                if bot_choice == "Rock":
                    await ctx.send("You chose Scissors and I chose Rock, I won! :D")
                if bot_choice == "Paper":
                    await ctx.send("You chose Scissors and I chose Paper, You won!, but I won't let you next time!")


    # TODO make a configuration of chatbot. Example: [p]chatbot <#channel> to talk with the chatbot forever in that channel @Mr Potato#3773 will do it
    @commands.command(name="chatbot",
                      aliases=['chat', 'chatb', 'cb'],
                      brief="Start a talking session with the bot!")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def _chatbot(self, ctx):
        session = True
        await ctx.send("The talking session between you and me started! Why not say something like `hi`\nIf you want to end this talking session, type `Cancel`")

        while session is True:
            try:
                message = await self.bot.wait_for('message', timeout = 30, check = lambda m : (ctx.author == m.author and ctx.channel == m.channel))
            except asyncio.TimeoutError:
                session = False
                await ctx.send("Timed out! Talking session with me has automatically ended!")
            else:
                if message.content.lower() == "cancel":
                    session = False
                    await ctx.send("Talking session with me has ended!")
                else:
                    async with ctx.channel.typing():

                        response = await self._get_response(ctx.author.id, message.content)
                        await message.reply(response, mention_author=False)


    async def _get_response(self, uid, msg):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://api.brainshop.ai/get?bid={self.bot.brain_id}&key={self.bot.brain_api}&uid={uid}&msg={msg}") as resp:
                if resp.status != 200:
                    return "Something went wrong while accessing the BrainShop API."
                js = await resp.json()
                return js["cnt"]

def setup(bot):
    bot.add_cog(Fun(bot))
