import discord
from discord.ext import commands
import datetime
import humanize
from classes import checks
from classes import CustomBotClass


class AltFinder(commands.Cog):

    def __init__(self, bot: CustomBotClass.CustomBot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    async def alts(self, ctx, dur=None, size: int = 10):
        if dur:
            if not dur.lower().endswith("d"):
                return await ctx.send("The duration must be days like `7d`")
        alts = []

        paginator = commands.Paginator()
        counter = 0
        for member in ctx.guild.members:
            if dur:
                delta = datetime.timedelta(days=int(dur[:-1]))
                if (datetime.datetime.now() - member.created_at) < delta:
                    if counter > size:
                        break
                alts.append(member)
                counter += 1
            else:
                if counter > size:
                    break
                alts.append(member)
                counter += 1
        alts.sort(reverse=True, key=checks.created_at)
        for alt in alts:
            paginator.add_line(f"{alt} Created at {humanize.naturaldate(alt.created_at.date())} ({humanize.precisedelta(datetime.datetime.now() - alt.created_at)})\n")
        for page in paginator.pages:
            await ctx.send(page)



def setup(bot):
    bot.add_cog(AltFinder(bot))
