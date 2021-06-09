import discord
from discord.ext import commands
from akinator.async_aki import Akinator
import akinator
import asyncio
from classes import CustomBotClass, akinator_buttons, indev_check


class AkinatorCog(commands.Cog):
    def __init__(self, bot: CustomBotClass.CustomBot):
        self.bot = bot

    @commands.command("akinator", aliases=['aki'], brief="Starts a game of akinator")
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def _aki(self, ctx: commands.Context):
        aki = Akinator()
        q = await aki.start_game()
        game_over = False

        async def game_over_callback():
            nonlocal game_over
            game_over = True

        async def callback(buttontype):
            if game_over:
                return
            if aki.progression <= 80:
                q2 = await aki.answer(buttontype)
                e2 = discord.Embed(title=q2, description="Click a button to answer")
                await ctx.reply(embed=e2,
                                view=akinator_buttons.AkinatorView(ctx.author, callback))
            await aki.win()
            e3 = discord.Embed(title=aki.first_guess['name'], description=aki.first_guess['description'])
            e3.set_image(url=aki.first_guess['absolute_picture_path'])
            await ctx.reply(embed=e3, view=akinator_buttons.AkinatorView2(ctx.author, game_over_callback))
            return

        e = discord.Embed(title=q, description="Click a button to answer")
        await ctx.reply(embed=e, view=akinator_buttons.AkinatorView(ctx.author, callback))


def setup(bot):
    bot.add_cog(AkinatorCog(bot))
