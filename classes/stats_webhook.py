import aiohttp
import discord
import pickle
import psutil
import humanize
import datetime
from discord.ext import commands


async def update_stats(bot: commands.Bot):
    latency = f"{bot.latency * 1000}ms"

    msg_id = 844559876684513280
    url = (pickle.load(open("credentials.pkl", 'rb')))["usageinfo"]
    session = aiohttp.ClientSession()
    webhook = discord.Webhook.from_url(url=url, session=session)
    cpu_usage = f"{psutil.cpu_percent(5)}%"
    ram_usage = f"{psutil.virtual_memory()[2]}%"
    load1, load2, load3 = psutil.getloadavg()
    load_str = f"{load1}, {load2}, {load3}"
    embed = discord.Embed(title="Bot Stats",
                          description=f"Online for **{humanize.precisedelta(datetime.datetime.utcnow() - bot.launch_time)}**",
                          color=bot.color)
    embed.add_field(name="Ping", value=latency)
    embed.add_field(name="Servers", value=len(bot.guilds))
    users = 0
    for guild in bot.guilds:
        for memb in guild.members:
            users += 1
    embed.add_field(name="Users", value=str(users))
    embed.add_field(name="CPU", value=cpu_usage)
    embed.add_field(name="RAM", value=ram_usage)
    embed.add_field(name="Load Average", value=load_str)
    embed.timestamp = datetime.datetime.utcnow()
    embed.set_footer(text="Last updated")
    await webhook.edit_message(msg_id, content=None, embed=embed)
    await session.close()
