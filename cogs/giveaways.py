import discord
from discord.ext import commands
import datetime
import humanize
import asqlite


class giveaways(commands.Cog):
	def __init__(self,bot):
		self.bot = bot
		
	
	@commands.command()
	async def gstart(self,ctx,time,winners,prize):
		if time.endswith('s'):
			seconds = time[:-1]
		  	duration = datetime.timedelta(seconds = int(seconds))
		if time.endswith('m'):
		  	minutes = time[:-1]
		  	duration = datetime.timedelta(minutes = int(minutes))
		elif time.endswith('h'):
		  	hours = time[:-1]
		  	duration = datetime.timedelta(hours = int(hours))
		elif time.endswith('d'):
			days = time[:-1]
			duration = datetime.timedelta(days = int(days))
		
		start_time = datetime.datetime.now()
		end_time = start_time + duration
		duration_humanized = humanize.naturaldelta(duration)
		embed = discord.Embed(title = prize, description = f"React with 🎉 to enter!\nTime Left: **{duration_humanized}**\nHosted By: {ctx.author.mention}", color = discord.Color.random())
		embed.timestamp = end_time
		embed.set_footer(text = "Ending Time:")
		gw_msg = await ctx.send("🎉 **GIVEAWAY** 🎉", embed = embed)
		
