import discord
import pickle
import psutil
import os
import humanize
import datetime


async def update_stats(bot:discord.ext.commands.Bot):
    latency = f"{bot.latency * 1000}ms"

    msg_id = 844559876684513280
    url = (pickle.load(open("credentials.pkl", 'rb')))["usageinfo"]

    webhook = discord.Webhook.from_url(url, adapter=discord.RequestsWebhookAdapter())

    cpu_usage = f"{psutil.cpu_percent(5)}%"
    ram_usage = f"{psutil.virtual_memory()[2]}%"
    load1, load2, load3 = psutil.getloadavg()
    load_str = f"{load1}, {load2}, {load3}"
    embed = discord.Embed(title = "Bot Stats", description = f"Online for **{humanize.precisedelta(datetime.datetime.now() - bot.launch_time)}**", color=bot.color)
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
    embed.timestamp = datetime.datetime.now()
    embed.set_footer(text="Last updated")
    webhook.edit_message(msg_id, content=None, embed=embed)
