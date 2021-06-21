import asyncio

import discord
from discord.ext import commands
from classes import CustomBotClass, indev_check, economy, check_create_db_entries
from constants import emojis
from constants.economy.ids import id_name, id_to_strid, strid_to_id
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
        try:
            return (await self.bot.pool.fetch("SELECT * FROM economy WHERE uid=$1", member.id))[0]
        except IndexError:
            await check_create_db_entries.check_create_db(self.bot, member)

    async def modify(self, member, column, sign, amt):
        if sign == "-":
            new_value = (await self.get_balance(member))[column] - amt
        elif sign == "+":
            new_value = (await self.get_balance(member))[column] + amt
        elif sign == "rr":
            await self.bot.pool.execute("UPDATE economy SET active_items=array_remove(active_items, $1) WHERE uid=$2", amt, member.id)
            return
        elif sign == "ar":
            await self.bot.pool.execute("UPDATE economy SET active_items=array_append(active_items, $1) WHERE uid=$2", amt, member.id)
            return
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
        e = discord.Embed(title=("Oh poor little beggar! take some coins!" if beg_successful else "Ew! a beggar!"),
                          description=f"You got {str(coins)} coins!",
                          colour=(discord.Colour.green() if beg_successful else discord.Colour.red()))
        await ctx.reply(embed=e)

    @commands.command()
    @indev_check.command_in_development()
    async def item(self, ctx: commands.Context, item: str):
        try:
            item = strid_to_id.strid_id[item]
        except KeyError:
            await ctx.reply("No such item")
            return
        await self.modify(ctx.author, None, "ar", item)
        await ctx.reply("done")

    @commands.command(name='slots', brief="Gambling is bad!")
    @commands.cooldown(1, 15, commands.BucketType.user)
    @indev_check.command_in_development()
    async def slots_command(self, ctx, amt: str):
        bal = (await self.get_balance(ctx.author))['purse']
        amt = economy.convert_to_money(amt, bal, 100, ctx.author)
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

        new_balance = await self.modify(ctx.author, 'purse', sign, int(win_amt))
        embed.description = f"{coin_str}\n\nYou now have **{new_balance}** coins."
        outcome_str = f"{first} {second} {third}"
        embed.add_field(name="Outcome", value=f"**<** {outcome_str} **>**")
        await ctx.send(embed=embed)

    @commands.command(name="balance", aliases=["bal"], brief="Gets the balance of a member")
    @indev_check.command_in_development()
    async def balance_command(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        balance = await self.get_balance(member)
        embed = discord.Embed(title=f"{member}'s balance",
                              description=f"Purse: **{balance['purse']}** coins\nBank: **{balance['bank']}** coins",
                              color=self.bot.color)
        embed.set_author(name=member, icon_url=member.avatar.url)
        await ctx.reply(embed=embed)

    @commands.command(name="deposit", aliases=["dep"], brief="Deposits coins into your bank account")
    @indev_check.command_in_development()
    async def _deposit(self, ctx, amt: str):
        bal = (await self.get_balance(ctx.author))['purse']
        final_bal = economy.convert_to_money(amt, bal, 0, ctx.author)
        await self.modify(ctx.author, "purse", "-", final_bal)
        await self.modify(ctx.author, "bank", "+", final_bal)
        await ctx.reply(f"Deposited {final_bal} coins, you now have {bal - final_bal} coins in your purse!")

    @commands.command(name="withdraw", aliases=["with"], brief="Withdraws money from your bank account")
    @indev_check.command_in_development()
    async def _withdraw(self, ctx, amt: str):
        bal = (await self.get_balance(ctx.author))['bank']
        final_bal = economy.convert_to_money(amt, bal, 0, ctx.author)
        await self.modify(ctx.author, "bank", "-", final_bal)
        await self.modify(ctx.author, "purse", "+", final_bal)
        await ctx.reply(f"Withdrew {final_bal} coins, you now have {bal - final_bal} coins in your bank!")

    @commands.command(name="rob", aliases=["steal"], brief="Stealing/robbing is bad!")
    @indev_check.command_in_development()
    @commands.guild_only()
    @commands.cooldown(1, 45, commands.BucketType.user)
    async def _rob(self, ctx: commands.Context, user: discord.Member):
        author = (await self.get_balance(ctx.author))
        unlucky_guy = (await self.get_balance(user))

        if author['passive']:
            await ctx.reply("Hey! You're in passive mode! Turn that off if you want to share!")
            return
        if unlucky_guy['passive']:
            await ctx.reply(f"Hey! {user.display_name} is in passive mode! leave them alone!")
            return

        if unlucky_guy['purse'] <= 500:
            await ctx.reply(
                f"Wtf are you doing? he has only {unlucky_guy['purse']} coins in his purse! leave that poor guy alone!")
            return
        if author['purse'] <= 250:
            await ctx.reply(
                f"You need at least 250 coins in your purse to steal!")
            return
        if strid_to_id.strid_id['padlock'] in unlucky_guy['active_items']:
            await self.modify(user, None, 'rr', strid_to_id.strid_id['padlock'])
            await ctx.reply(f"You notice `{user.display_name}` has  **HUGE** padlock on his wallet, you were caught and had to pay 250 coins to the police!")
            await self.modify(ctx.author, "purse", "-", 250)
            return
        success = random.choice([True, False])
        if success:
            amount = random.randint(1, unlucky_guy['purse'])
        else:
            amount = random.randint(1, author['purse'])

        quotient = amount / unlucky_guy['purse']
        percentage = quotient * 100

        await self.modify(ctx.author, 'purse', ("+" if success else "-"), amount)
        await self.modify(user, 'purse', ("-" if success else "+"), amount)

        if success:
            if percentage <= 10:
                await ctx.reply(f"{emojis.laughing} You stole just {amount} from `{user.display_name}`")
                return
            if percentage <= 25:
                await ctx.reply(f"{emojis.no_emotion} You stole {amount} from `{user.display_name}`")
                return
            if percentage <= 75:
                await ctx.reply(
                    f"{emojis.bag_o_cash} You stole a fair amount! you stole {amount} from `{user.display_name}`")
                return
            if percentage <= 100:
                await ctx.reply(
                    f"{emojis.money_in_mouth} YOU STOLE BASICALLY EVERYTHING LMFAO! You stole {amount} from `{user.display_name}`!")
                return
        else:
            await ctx.reply(
                f'{emojis.laughing} You were caught stealing! you had to pay {amount} to the police {emojis.laughing}')

    @commands.command(name="give", brief="gives the mentioned used a certain amount of money!")
    @indev_check.command_in_development()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def _give(self, ctx: commands.Context, user: discord.Member, amount: str):
        bal = (await self.get_balance(ctx.author))['purse']
        info = (await self.get_balance(ctx.author))
        user_info = (await self.get_balance(user))
        if info['passive']:
            await ctx.reply("Hey! You're in passive mode! Turn that off if you want to share!")
            return
        if user_info['passive']:
            await ctx.reply(f"Hey! {user.display_name} is in passive mode! leave them alone!")
            return
        amt = economy.convert_to_money(amount, bal, 100, ctx.author)
        quotient = amt / bal
        percentage = quotient * 100

        def check(message):
            return message.author.id == ctx.author.id

        if percentage > 50:
            await ctx.reply(f"You want to give {amt} to {user.mention}? reply with yes or no")
            try:
                msg = await self.bot.wait_for("message", check=check, timeout=60)
            except asyncio.TimeoutError:
                return
            else:
                if msg.content == "yes" or msg.content == "y" or msg.content == "ye" or msg.content == "yup":
                    message = await ctx.reply(f"kay, initiating transaction {emojis.loading}")
                    await asyncio.sleep(0.5)
                    await message.edit(content=f"Contacting to the bank {emojis.loading}")
                    await asyncio.sleep(2)
                    await message.edit(content=f"Writing check {emojis.loading}")
                    await asyncio.sleep(5)
                    await message.edit(content=f"Processing payment {emojis.loading}")
                    await asyncio.sleep(10)
                    await self.modify(ctx.author, "purse", "-", amt)
                    await self.modify(user, "purse", "+", amt)
                    await message.edit(content=f"Transfer done {emojis.white_check_mark}")
                    return
                else:
                    await ctx.reply("aight, not giving anything")
                    return
        message = await ctx.reply(content=f"kay, initiating transaction {emojis.loading}")
        await asyncio.sleep(0.5)
        await message.edit(content=f"Contacting to the bank {emojis.loading}")
        await asyncio.sleep(2)
        await message.edit(content=f"Writing check {emojis.loading}")
        await asyncio.sleep(5)
        await message.edit(content=f"Processing payment {emojis.loading}")
        await asyncio.sleep(10)
        await self.modify(ctx.author, "purse", "-", amt)
        await self.modify(user, "purse", "+", amt)
        await message.edit(content=f"Transfer done {emojis.white_check_mark}")
        return




def setup(bot):
    bot.add_cog(EconomyBasic(bot))
