import discord
from discord.ext import commands
import datetime
import humanize
from classes import checks
import typing
from classes import CustomBotClass


class AltFinder(commands.Cog):

    def __init__(self, bot: CustomBotClass.CustomBot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    async def alts(self, ctx, dur: typing.Optional[str]=None, size: int = 10):
        if dur:
            if not dur.lower().endswith("d"):
                return await ctx.send("The duration must be days like `7d`")
        alts = []

        paginator = commands.Paginator(prefix="```yaml", suffix="```", max_size=1000)
        counter = 0
        if dur:
            for member in ctx.guild.members:
                delta = datetime.timedelta(days=int(dur[:-1]))
                if (datetime.datetime.now() - member.created_at) < delta:
                    if counter > size:
                        break
                alts.append(member)
                counter += 1
            alts.sort(reverse=True, key=checks.created_at)
            for alt in alts:
                paginator.add_line(f"{alt} Created at {humanize.naturaldate(alt.created_at.date())} ({humanize.precisedelta(datetime.datetime.now() - alt.created_at)})\n")
        if not dur:
            all_membrs = (ctx.guild.members.sort(reverse=True, key=checks.created_at))[:size]
            for alt in all_membrs:
                paginator.add_line(
                    f"{alt} Created at {humanize.naturaldate(alt.created_at.date())} ({humanize.precisedelta(datetime.datetime.now() - alt.created_at)})\n")
        for page in paginator.pages:
            title = f"Accounts less than {humanize.precisedelta(delta)} old" if dur else "Newest accounts"
            embed=discord.Embed(title=title, description=page, color=self.bot.color)
            await ctx.send(embed=embed)



def setup(bot):
    bot.add_cog(AltFinder(bot))
