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
        q = await aki.start_game(child_mode=(False if ctx.channel.is_nsfw() else True))
        game_over = False
        guesses = 1
        message: discord.Message = None

        async def game_over_callback(nothing):
            nonlocal game_over
            nonlocal guesses
            nonlocal message
            if nothing:
                game_over = True
            else:
                await aki.win()
                guesses = guesses + 1
                if len(aki.guesses) <= guesses:
                    await ctx.reply(";( you win, I don't know who it is!")
                    game_over = True
                    return
                e3 = discord.Embed(title=aki.guesses[guesses]['name'], description=aki.guesses[guesses]['description'])
                e3.set_image(url=aki.guesses[guesses]['absolute_picture_path'])
                await message.edit(embed=e3, view=akinator_buttons.AkinatorView2(ctx.author, game_over_callback))
                return

        async def callback(buttontype):
            if game_over:
                return
            if not buttontype:
                await aki.back()
                q2 = aki.question
                e2 = discord.Embed(title=q2, description="Click a button to answer")
                await message.edit(embed=e2,
                                   view=akinator_buttons.AkinatorView(ctx.author, callback))
                return
            if aki.progression <= 80:
                q2 = await aki.answer(buttontype)
                e2 = discord.Embed(title=q2, description="Click a button to answer")
                e2.set_footer(text=f"Progression: {aki.progression}")
                await message.edit(embed=e2,
                                   view=akinator_buttons.AkinatorView(ctx.author, callback))
                return

            await aki.win()
            e3 = discord.Embed(title=aki.first_guess['name'], description=aki.first_guess['description'])
            e3.set_image(url=aki.first_guess['absolute_picture_path'])
            await message.edit(embed=e3, view=akinator_buttons.AkinatorView2(ctx.author, game_over_callback))
            return

        e = discord.Embed(title=q, description="Click a button to answer")
        message = await ctx.reply(embed=e, view=akinator_buttons.AkinatorView(ctx.author, callback))


def setup(bot):
    bot.add_cog(AkinatorCog(bot))
