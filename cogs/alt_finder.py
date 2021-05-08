import discord
from discord.ext import commands
import datetime
import humanize
from classes import CustomBotClass


class AltFinder(commands.Cog):

    def __init__(self, bot: CustomBotClass.CustomBot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    async def alts(self, ctx, dur="7d", size: int = 10):
        if not dur.lower().endswith("d"):
            return await ctx.send("The duration must be days like `7d`")

        delta = datetime.timedelta(days=int(dur[:-1]))
        alts = []

        def check(mem: discord.User):
            return mem.created_at

        paginator = commands.Paginator()
        counter = 0
        for member in ctx.guild.members:
            if (datetime.datetime.now() - member.created_at) < delta:
                if counter > size:
                    break
                alts.append(member)
                counter += 1
        alts.sort(reverse=True, key=check)
        for alt in alts:
            paginator.add_line(f"*`{(alts.index(alt)) + 1}.`* - {alt.mention} - {humanize.naturaldate(alt.created_at.date())}\n")
        for page in paginator.pages:
            embed = discord.Embed(
                title=f"New accounts in {ctx.guild.name}",
                description=page,
                color=self.bot.color)
            embed.set_footer(
                text=f"Showing {size} alts less than {humanize.precisedelta(delta)} old")
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(AltFinder(bot))
