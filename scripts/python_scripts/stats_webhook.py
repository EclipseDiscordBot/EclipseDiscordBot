import discord
import pickle
import psutil
import os
import humanize


def update_stats(bot:discord.ext.commands.Bot):
    latency = f"{bot.latency * 1000}ms"

    msg_id = 844559876684513280
    url = (pickle.load(open("credentials.pkl", 'rb')))["usageinfo"]

    webhook = discord.Webhook.from_url(url, adapter=discord.RequestsWebhookAdapter())

    cpu_usage = f"{psutil.cpu_percent(5)}%"
    ram_usage = f"{psutil.virtual_memory()[2]}%"
    pid = os.getpid()
    load1, load2, load3 = psutil.getloadavg()
    load_str = f"{load1}, {load2}, {load3}"
    embed = discord.Embed(title = "Bot Stats", description = f"Online for **{humanize.precisedelta(datetime.datetime.now() - bot.launch_time)}**", color=bot.color)
    embed.add_field(name="Ping", value=latency)
    embed.add_field(name="CPU", value=cpu_usage)
    embed.add_field(name="RAM", value=ram_usage)
    embed.add_field(name="Load Average", value=load_str)
    embed.add_field(name="PID", value=str(pid))
    embed.timestamp = datetime.datetime.now()
    embed.set_footer(text="Last updated")
    await webhook.edit_message(msg_id, content=None, embed=embed)



