import discord
from discord.ext import commands
import datetime
import humanize

class AltFinder(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
     
    @commands.command()
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    async def alts(self, ctx, dur = "7d", size:int=10):
        if not dur.lower().endswith("d"):
            return await ctx.send("The duration must be days like `7d`")
        
        delta = datetime.timedelta(days=dur[:-1])
        alts = []
        def check(mem:discord.User):
            return mem.created_at
        
        alts_str = ""
        counter = 0
        for member in ctx.guild.members:
            if (datetime.datetime.now() - member.created_at) < delta:
                if counter > size:
                    break
                alts.append(member)
                counter += 1
        alts.sort(reverse=True, key=check)
        for alt in alts:
            alts_str += f"*`{(alts.index(alt)) + 1}.`* - {alt.mention} - {humanize.naturaldate(alt.created_at.date())}\n"
        
        embed = discord.Embed(title = f"New accounts in {ctx.guild.name}", description=alts_str, color=self.bot.color)
        embed.set_footer(text=f"Showing {size} alts less than {humanize.precisedelta(delta)} old")
        await ctx.send(embed=embed)
        
        
        
        
        
        
        
def setup(bot):
    bot.add_cog(AltFinder(bot))
                
       
  
	
	
  
    
    
    
