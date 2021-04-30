import asyncpraw as apraw
import discord
from discord.ext import commands
import datetime
import json
from discord_slash import SlashCommand
import os
from classes.LoadCog import load_extention
import pickle
import asyncpg
import asyncio
from discord.ext import tasks
import random

intents = discord.Intents.all()


async def get_prefix(bot, message):
    base = [
        "<@827566012467380274>",
        "<@!827566012467380274>",
        "<@827566012467380274> ",
        "<@!827566012467380274> "]
    if message.author.id == 694839986763202580 or message.author.id == 605364556465963018:
        base.append("")
    if not message.guild:
        base.append("e! ")
        base.append("e!")
        return base
    async with bot.pool.acquire() as conn:
        async with conn.transaction():
            prefix = await conn.fetchval("SELECT prefix FROM prefixes WHERE guild_id = $1", message.guild.id)
            base.append(prefix)
    return base


mentions = discord.AllowedMentions(
    everyone=False,
    users=True,
    replied_user=False,
    roles=False)

bot = commands.Bot(
    command_prefix=get_prefix,
    intents=intents,
    allowed_mentions=mentions,
    case_insensitive=True)

slash = SlashCommand(bot, override_type=True)

bot.launch_time = datetime.datetime.utcnow()

bot.color = discord.Color.from_rgb(156, 7, 241)


@bot.event
async def on_ready():
    bot.load_extension('jishaku')
    exceptions = ""
    with open("config/config.json", "r") as read_file:
        data = json.load(read_file)
        bot.config = data
    for file in os.listdir("./cogs"):
        if file.endswith('.py'):
            try:
                load_extention(bot, f'cogs.{file[:-3]}', data)
                print(f"loaded cogs.{file[:-3]}")
            except Exception as e:
                exceptions += f"- {file} failed to load [{e}]\n"
            else:
                exceptions += f"+ {file} loaded successfully\n"

    for file in os.listdir("./cogs/slash_cmds"):
        if file.endswith('.py'):
            try:
                load_extention(bot, f'cogs.slash_cmds.{file[:-3]}', data)
                print(f"loaded cogs.slash_cmds.{file[:-3]}")
            except Exception as e:
                exceptions += f"- {file} failed to load [{e}]\n"
            else:
                exceptions += f"+ {file} loaded successfully\n"

    embed = discord.Embed(
        title="Bot ready!",
        description=f"Cogs status: \n ```diff\n{exceptions}```",
        color=bot.color)
    embed.timestamp = bot.launch_time
    embed.set_footer(text="Bot online since:")
    c = bot.get_channel(827737123704143890)
    await c.send(embed=embed)


async def on_message(message):
    if bot.user.mentioned_in(message):
        if not message.guild:
            await message.reply("Hello! My prefix here is *`e!`*!")
        else:
            async with bot.pool.acquire() as conn:
                async with conn.transaction():
                    prefix = await conn.fetchval("SELECT prefix FROM prefixes WHERE guild_id = $1", message.guild.id)
            await message.reply(f"Hello! My prefix here is *`{prefix}`*!")

    await bot.process_commands(message)



@bot.command()
@commands.has_permissions(administrator=True)
@commands.guild_only()
async def prefix(ctx, prefix):
    async with bot.pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute("UPDATE prefixes SET prefix = $1 WHERE guild_id = $2", prefix, ctx.guild.id)
    await ctx.send(f"My prefix in this server has successfully been changed to {prefix}\n\n **TIP:** To include "
                   f"spaces in the prefix do use quotes like {prefix}prefix \"hey \"")


@bot.event
async def on_guild_join(guild):
    async with bot.pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute("INSERT INTO prefixes (guild_id, prefix) VALUES ($1, $2)", guild.id, "e!")
            await conn.execute(
                "INSERT INTO greet (guild_id, config, channel_id, msg, delafter) VALUES ($1, $2, $3, $4, $5)", guild.id,
                0, 0, "placeholder", 0)
            await conn.execute("INSERT INTO logging(server_id,channel_id,enabled) VALUES($1,$2,$3)",
                               guild.id, 0, False)
            await conn.execute("INSERT INTO automeme(server_id,channel_id,enabled) VALUES($1,$2,$3)",
                               guild.id, 0, False)


@bot.event
async def on_guild_leave(guild):
    async with bot.pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute("DELETE FROM prefixes WHERE guild_id = $1", guild.id)
            await conn.execute("DELETE FROM greet WHERE guild_id = $1", guild.id)
            await conn.execute("DELETE FROM logging WHERE server_id=$1", guild.id)
            await conn.execute("DELETE FROM automeme WHERE server_id=$1", guild.id)


async def gend(gw):
    guild = bot.get_guild(gw["guild_id"])
    ch = guild.get_channel(gw["channel_id"])
    msg = await ch.fetch_message(gw["msg_id"])
    host = guild.get_member(gw["host"])
    prize = gw["prize"]
    print(f"ending giveaway id {msg.id}")
    winners = gw["winners"]
    new_embed = msg.embeds[0].copy()
    end_timestamp = gw["end_time"]
    await discord.utils.sleep_until(datetime.datetime.fromtimestamp(end_timestamp))
    reactions = msg.reactions[0]
    raffle = await reactions.users().flatten()
    raffle.pop(raffle.index(bot.user))
    if winners > 1:
        try:
            winner = random.choice(raffle)
            winner_str = winner.mention
        except Exception:
            await ch.send(f"There were no entrants to the giveaway lol\n {msg.jump_url}")
            return
    else:
        new_list = []
        for entrant in raffle:
            new_list.append(entrant.mention)
        final_set = set(new_list)
        winner_list = random.sample(final_set, winners)
        winner_str = ""
        for win in winner_list:
            winner_str += f"{win.mention}, "

    new_embed.description = f"Winner(s): {winner_str}\n Hosted by: {host.mention}"
    new_embed.timestamp = datetime.datetime.now()
    if winners > 1:
        new_embed.set_footer(text=f"{winners} winners • Ended at")
    else:
        new_embed.set_footer(text="Ended at")
    cleaned_prize = ""
    for word in prize:
        for i in word:
            cleaned_prize += f"{i}\u200b"
    await ch.send(f"🎉 Congratulations {winner_str}! You won **{cleaned_prize}**! \n {msg.jump_url}")
    await bot.pool.execute("DELETE FROM giveaways WHERE msg_id = $1", gw["msg_id"])


@tasks.loop(seconds=5)
async def end_gws():
    await bot.wait_until_ready()
    async with bot.pool.acquire() as conn:
        async with conn.transaction():
            res = await conn.fetch("SELECT * FROM giveaways")
    for row in res:
        end_time = datetime.datetime.fromtimestamp(row["end_time"])
        if datetime.datetime.now() - end_time < datetime.timedelta(seconds=5):
            await gend(row)



loop = asyncio.get_event_loop()
f = pickle.load(open('credentials.pkl', 'rb'))
bot.pool = loop.run_until_complete(
    asyncpg.create_pool(
        dsn=f["postgres_uri"],
        host=f["postgres_host"],
        user=f["postgres_user"],
        port=f["postgres_port"],
        password=f["postgres_password"],
        database=f["postgres_database"]))

bot.reddit = apraw.Reddit(client_id=f['reddit_id'], client_secret=f['reddit_secret'], user_agent="Eclipse")
bot.memes = []

bot.run(f["discord"])
