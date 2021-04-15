import discord
from discord.ext import commands
import pickle
import datetime
from discord_slash import SlashCommand, SlashContext
import os
import traceback


intents = discord.Intents.all()

bot = commands.Bot(command_prefix="e!", intents=intents)
slash = SlashCommand(bot, override_type=True)
bot.launch_time = datetime.datetime.utcnow()
bot.color = discord.Color.from_rgb(156, 7, 241)



@bot.event
async def on_ready():
        bot.load_extension('jihaku')
        exceptions = ""
        for file in os.listdir("./cogs"):
                if file.endswith('.py'):
                        try:
                                bot.load_extension(f"cogs.{file[:-3]}")
                        except Exception as e:
                                exceptions += f"- {file} failed to load [{e}]\n"
                        else:
                                exceptions += f"+ {file} loaded successfully\n"
   
        embed = discord.Embed(title = "Bot ready!", description = f"Cogs status: \n ```diff\n{exceptions}```", color = bot.color)
        embed.timestamp = bot.launch_time
        embed.set_footer(text = "Bot online since:")
        c = bot.get_channel(827737123704143890)
        await c.send(embed = embed)
                    
         
                               

token = pickle.load(open("credentials.pkl", 'rb'))['discord']
bot.run(token)
