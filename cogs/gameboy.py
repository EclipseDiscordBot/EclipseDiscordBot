from discord.ext import commands
import discord
import pyboy
from save_thread_result import ThreadWithResult
from classes import CustomBotClass, indev_check, ignore, gameboy


class GameBoy(commands.Cog):
    def __init__(self, bot: CustomBotClass.CustomBot):
        self.bot = bot

    @commands.command("gb", aliases=["Gameboy"])
    @indev_check.command_in_development()
    @commands.cooldown(1, 3600, commands.BucketType.user)
    @commands.guild_only()
    async def _gb(self, ctx: commands.Context):
        if self.bot.gameboy:
            await ctx.reply("Sorry, somebody is already using this.. try again later :D")
            return
        bot = self.bot
        bot.gameboy = True
        message: discord.Message = ctx.message
        if not message.attachments:
            e = discord.Embed(
                title="Oops! you have not attached any ROM files to your message!",
                description=" we can't tell you where to get it... Nintendo is here! RUN FOR YOUR LIVES",
                colour=discord.Color.red())
            await ctx.reply(embed=e)
            return
        rom: discord.Attachment = message.attachments[0]
        if not (rom.filename.split(".")[-1] == "gb"):
            e = discord.Embed(
                title="Oops! the file you attached is NOT a gameboy ROM file. it should have a `.gb` extension!",
                description=" we can't tell you where to get it... Nintendo is here! RUN FOR YOUR LIVES",
                colour=discord.Color.red())
            await ctx.reply(embed=e)
            return
        await rom.save(f"data/gameboy/{ctx.author.id}.{rom.filename}")
        instance = gameboy.GameBoy(
            f"data/gameboy/{ctx.author.id}.{rom.filename}",
            ctx.channel,
            ctx.author,
            bot.loop)
        await instance.start_emulator(ctx)
        self.bot = False


def setup(bot):
    bot.add_cog(GameBoy(bot))
