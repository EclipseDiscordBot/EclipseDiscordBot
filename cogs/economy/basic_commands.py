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

    async def get_balance(self, member):
        return (await self.bot.pool.fetch("SELECT * FROM economy WHERE uid=$1", member.id))[0]

    async def modify(self, member, column, sign, amt):
        if sign == "-":
            new_value = (await self.get_balance(member))[column] - amt
        elif sign == "+":
            new_value = (await self.get_balance(member))[column] + amt
        else:
            return
        if column == "purse":
            await self.bot.pool.execute("UPDATE economy SET purse =$1 WHERE uid=$2", new_value, member.id)
        elif column == "bank":
            await self.bot.pool.execute("UPDATE economy SET bank =$1 WHERE uid=$2", new_value, member.id)
        return new_value



    @commands.command("beg", brief="Begs for money!")
    @commands.cooldown(1, 45, commands.BucketType.user)
    @indev_check.command_in_development()
    async def _beg(self, ctx):
        beg_successful = random.choice([True, False])
        coins = (random.randint(0, 1000) if beg_successful else 0)
        new_bal = await self.modify(ctx.author, 'purse', "+" if beg_successful else "-", coins)
        e = discord.Embed(title=("Oh poor little beggar! take some coins!" if beg_successful else "Ew! a beggar!"), description=f"You got {str(coins)} coins!\nNow you have {new_bal} coins", colour=(discord.Colour.green() if beg_successful else discord.Colour.red()))
        await ctx.reply(embed=e)

    @commands.command(name='slots', brief="Gambling is bad!")
    @commands.cooldown(1, 15, commands.BucketType.user)
    @indev_check.command_in_development()
    async def slots_command(self, ctx, amt: int):
        bal = (await self.get_balance(ctx.author))['purse']
        if amt > bal:
            await ctx.send("You don't have that much!")
            return
        emoji = ["👀", "🔥", "😳", "🤡", "👽", "🖕", "🌟", "🍑", "🍆"]
        result = []
        first = random.choice(emoji)
        second = random.choice(emoji)
        third = random.choice(emoji)
        result.append(first)
        result.append(second)
        result.append(third)

        embed = discord.Embed(title=f"{ctx.author.display_name}'s slots machine")
        win_amt = 0
        win = False

        dict = {}

        for res in result:
            if res in dict.keys():
                dict[res] += 1
            else:
                dict[res] = 1

        for i in dict.keys():
            if dict[i] >= 2:
                win = True
                break

        if win == True:
            embed.color = discord.Color.green()
        else:
            embed.color = discord.Color.red()
            embed.set_footer(text="sucks to suck")

        if win == True:
            if first == second == third:
                sign = "+"
                win_amt = 100 * amt
            else:
                sign = "+"
                win_amt = 2 * amt
        else:
            sign = "-"
            win_amt = amt

        if win == True:
            coin_str = f"You won **{win_amt}** coins."
        else:
            coin_str = f"You lost **{win_amt}** coins."

        new_balance = await self.modify(ctx.author, 'purse', sign, win_amt)
        embed.description = f"{coin_str}\n\nYou now have **{new_balance}** coins."
        outcome_str = f"{first} {second} {third}"
        embed.add_field(name="Outcome", value=f"**<** {outcome_str} **>**")
        await ctx.send(embed=embed)

    @commands.command(name="balance", aliases=["bal"], brief="Gets the balance of a member")
    @indev_check.command_in_development()
    async def balance_command(self, ctx, member:discord.Member=None):
        member = member or ctx.author
        balance = await self.get_balance(member)
        embed = discord.Embed(title = f"{member}'s balance", description=f"Purse: **{balance['purse']}** coins\nBank: **{balance['bank']}** coins", color=self.bot.color)
        embed.set_author(name=member, icon_url=member.avatar.url)
        await ctx.reply(embed = embed)




def setup(bot):
    bot.add_cog(EconomyBasic(bot))
