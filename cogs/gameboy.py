from discord.ext import commands
import discord
import pyboy
from save_thread_result import ThreadWithResult
from classes import CustomBotClass, indev_check, ignore, deprecated


class GameBoy(commands.Cog):
    def __init__(self, bot: CustomBotClass.CustomBot):
        self.bot = bot

    @commands.command("gb", aliases=["Gameboy"])
    @indev_check.command_in_development()
    @commands.cooldown(1, 3600, commands.BucketType.user)
    @commands.guild_only()
    @deprecated
    async def _gb(self, ctx: commands.Context):
        bot = self.bot
        ignore.ignore(bot)
        message: discord.Message = ctx.message
        if not message.attachments:
            e = discord.Embed(title="Oops! you have not attached any ROM files to your message!",
                              description=" we can't tell you where to get it... Nintendo is here! RUN FOR YOUR LIVES",
                              colour=discord.Color.red())
            await ctx.reply(embed=e)
            return
        rom: discord.Attachment = message.attachments[0]
        if not (rom.filename.split(".")[-1] == "gb"):
            e = discord.Embed(title="Oops! the file you attached is NOT a gameboy ROM file. it should have a `.gb` extension!", description=" we can't tell you where to get it... Nintendo is here! RUN FOR YOUR LIVES", colour=discord.Color.red())
            await ctx.reply(embed=e)
            return
        await rom.save(f"data/gameboy/{ctx.author.id}.{rom.filename}")
        gb_thread = ThreadWithResult(target=pyboy.PyBoy, args=(f"/home/satyamedh/PycharmProjects/EclipseDiscordBot/data/gameboy/{ctx.author.id}.{rom.filename}",))
        gb_thread.daemon = True
        gb_thread.start()
        if getattr(gb_thread, 'result', None):
            print(gb_thread.result)




def setup(bot):
    bot.add_cog(GameBoy(bot))
