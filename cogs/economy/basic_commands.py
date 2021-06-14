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

    async def update_account(self, member: discord.Member, column, new_value):
        if column == "purse":
            await self.bot.pool.execute("UPDATE economy SET purse=$1 WHERE uid=$2", new_value, member.id)
        elif column == "bank":
            await self.bot.pool.execute("UPDATE economy SET bank=$1 WHERE uid=$2", new_value, member.id)



    async def get_status(self, member: discord.Member):
        return await self.bot.pool.fetch("SELECT * FROM economy WHERE uid=$1", member.id)

    @commands.command("beg", brief="Begs for money!")
    @commands.cooldown(1, 45, commands.BucketType.user)
    @indev_check.command_in_development()
    async def _beg(self, ctx):
        balance = await self.get_status(ctx.author)
        beg_successful = random.choice([True, False])
        coins = (random.randint(0, 1000) if beg_successful else 0)
        new_bal = balance[0]["purse"] + coins
        await self.update_account(ctx.author, "purse", new_bal)
        e = discord.Embed(title=("Oh poor little beggar! take some coins!" if beg_successful else "Ew! a beggar!"),
                          description=f"You got {str(coins)} coins!",
                          colour=(discord.Colour.green() if beg_successful else discord.Colour.red()))

        await ctx.reply(embed=e)



def setup(bot):
    bot.add_cog(EconomyBasic(bot))
