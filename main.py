import discord
from discord.ext import commands
import pickle
import datetime

intents = discord.Intents.all()

bot = commands.Bot(command_prefix="e!", intents=intents)
bot.launch_time = datetime.datetime.utcnow()
bot.color = discord.Color.from_rgb(68, 11, 212)

cogs = ['cogs.basic',
        'cogs.mod',
        'cogs.error_handler',
        'cogs.utils',
        'jishaku']


@bot.event
async def on_ready():
    for i in cogs:
        bot.load_extension(i)
        print(f"loaded {i}")
    await send_init_msg()
    print(
        f"Bot ready; started on {bot.launch_time} and logged in as {bot.user} Can see {len(bot.users)} members and {len(bot.guilds)} guilds Ping is {round(bot.latency * 1000)} ms")


async def send_init_msg():
    channel = bot.get_channel(827737123704143890)
    await channel.send(
        f"Bot ready; started on {bot.launch_time} and logged in as {bot.user} Can see {len(bot.users)} members and {len(bot.guilds)} guilds Ping is {round(bot.latency * 1000)} ms")


token = pickle.load(open("credentials.pkl", 'rb'))['discord']
bot.run(token)
