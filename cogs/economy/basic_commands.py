import discord
from discord.ext import commands
from classes import CustomBotClass, indev_check
import random
class EconomyBasic(commands.Cog):
    def __init__(self, bot: CustomBotClass.CustomBot):
        """

        The Economy cog

        database table:

         uid | purse | bank | inventory | work | sus
        -----+-------+------+-----------+------+-----


        :param bot:
        """
        self.bot = bot

    @commands.command("beg", brief="Begs for money!")
    @commands.cooldown(1, 45, commands.BucketType.user)
    @indev_check.command_in_development()
    async def _beg(self, ctx):
        current_status = await self.bot.pool.fetch("SELECT * FROM economy WHERE uid=$1", ctx.author.id)
        beg_successful = random.choice([True, False])
        coins = (random.randint(0, 1000) if beg_successful else 0)
        e = discord.Embed(title=("Oh poor little beggar! take some coins!" if beg_successful else "Ew! a beggar!"), description=f"You got {str(coins)} coins!", colour=(discord.Colour.green() if beg_successful else discord.Colour.red()))
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("UPDATE economy SET purse=$1 WHERE uid=$2", current_status[0]['purse']+coins, ctx.author.id)

        await ctx.reply(embed=e)



def setup(bot):
    bot.add_cog(EconomyBasic(bot))
