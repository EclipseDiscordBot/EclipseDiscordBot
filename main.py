import discord
from discord.ext import commands
import pickle
import datetime

intents = discord.Intents.all()

client = commands.Bot(command_prefix="e!", intents=intents)
client.launch_time = datetime.datetime.utcnow()

cogs = ['cogs.basic',
        'cogs.mod',
        'jishaku']



@client.event
async def on_ready():
    for i in cogs:
        client.load_extension(i)
        print(f"loaded {i}")
    await send_init_msg()
    print(
        f"Bot ready; started on {client.launch_time} and logged in as {client.user} Can see {len(client.users)} members and {len(client.guilds)} guilds Ping is {round(client.latency * 1000)} ms")


async def send_init_msg():
    channel = client.get_channel(827737123704143890)
    await channel.send(f"Bot ready; started on {client.launch_time} and logged in as {client.user} Can see {len(client.users)} members and {len(client.guilds)} guilds Ping is {round(client.latency * 1000)} ms")


token = pickle.load(open("credentials.pkl", 'rb'))['discord']
client.run(token)
