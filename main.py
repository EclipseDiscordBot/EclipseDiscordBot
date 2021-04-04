import discord
from discord.ext import commands
import jishaku
import pickle
import datetime

client = commands.Bot(command_prefix="e!")
client.launch_time = datetime.datetime.utcnow()

cogs = ['cogs.basic',
        'jishaku']


@client.event
async def on_ready():
    c = 0
    for guild in client.guilds:
        c += guild.member_count
    for i in cogs:
        client.load_extension(i)
        print(f"loaded {i}")
    print(
        f"Bot ready; started on {client.launch_time} and logged in as {client.user} Can see {c} members and {len(client.guilds)} guilds Ping is {round(client.latency * 1000)} ms")


token = pickle.load(open("credentials.pkl", 'rb'))['discord']
client.run(token)
