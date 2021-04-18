import discord
from discord.ext import commands
import pickle
import datetime
from discord_slash import SlashCommand, SlashContext
import os
import traceback
import pickle
import asyncpg
import asyncio

intents = discord.Intents.all()


async def get_prefix(bot, message):
    base = ["<@827566012467380274>", "<@!827566012467380274>", "<@827566012467380274> ", "<@!827566012467380274> "]
    if message.guild is None:
        base.append("e! ")
        base.append("e!")
    else:
        async with bot.pool.acquire() as conn:
            async with conn.transaction():
                prefix = await conn.fetchval("SELECT prefix FROM prefixes WHERE guild_id = $1", message.guild.id)
                base.append(prefix)
    return base

mentions = discord.AllowedMentions(everyone=False, users=True, replied_user=False, roles=False)

bot = commands.Bot(command_prefix=get_prefix, intents=intents, allowed_mentions = mentions)

slash = SlashCommand(bot, override_type=True)

bot.launch_time = datetime.datetime.utcnow()

bot.color = discord.Color.from_rgb(156, 7, 241)


@bot.event
async def on_ready():
    bot.load_extension('jishaku')
    exceptions = ""
    for file in os.listdir("./cogs"):
        if file.endswith('.py'):
            try:
                bot.load_extension(f"cogs.{file[:-3]}")
                print(f"loaded cogs.{file[:-3]}")
            except Exception as e:
                exceptions += f"- {file} failed to load [{e}]\n"
            else:
                exceptions += f"+ {file} loaded successfully\n"

    for file in os.listdir("./cogs/slash_cmds"):
        if file.endswith('.py'):
            try:
                bot.load_extension(f"cogs.slash_cmds.{file[:-3]}")
                print(f"loaded cogs.slash_cmds.{file[:-3]}")
            except Exception as e:
                exceptions += f"- {file} failed to load [{e}]\n"
            else:
                exceptions += f"+ {file} loaded successfully\n"

    embed = discord.Embed(title="Bot ready!", description=f"Cogs status: \n ```diff\n{exceptions}```", color=bot.color)
    embed.timestamp = bot.launch_time
    embed.set_footer(text="Bot online since:")
    c = bot.get_channel(827737123704143890)
    await c.send(embed=embed)


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
            await conn.execute("INSERT INTO greet (guild_id, config, channel_id, msg, delafter) VALUES ($1, $2, $3, $4, $5)", guild.id, 0, 0, "placeholder", 0)


@bot.event
async def on_guild_leave(guild):
    async with bot.pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute("DELETE FROM prefixes WHERE guild_id = $1", guild.id)
            await conn.execute("DELETE FROM greet WHERE guild_id = $1", guild.id)

loop = asyncio.get_event_loop()
f = pickle.load(open('credentials.pkl', 'rb'))
bot.pool = loop.run_until_complete(
    asyncpg.create_pool(dsn=f["postgres_uri"], host=f["postgres_host"], user=f["postgres_user"],
                        port=f["postgres_port"], password=f["postgres_password"], database=f["postgres_database"]))

bot.run(f["discord"])
