import discord
from discord.ext import commands
import datetime
from discord_slash import SlashCommand
import os
from classes.LoadCog import load_extension
from discord.ext import tasks
import random

intents = discord.Intents.all()


async def get_prefix(eclipse, message):
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
    async with eclipse.pool.acquire() as conn:
        async with conn.transaction():
            prefixes = await conn.fetchval("SELECT prefix FROM prefixes WHERE guild_id = $1", message.guild.id)
            base.append(prefixes)
    return base


mentions = discord.AllowedMentions(
    everyone=False,
    users=True,
    replied_user=False,
    roles=False)


class Eclipse(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=get_prefix,
                         allowed_mentions=mentions,
                         intents=intents)

        loop = asyncio.get_event_loop()
        f = pickle.load(open('credentials.pkl', 'rb'))
        self.pool = loop.run_until_complete(
            asyncpg.create_pool(
                dsn=f["postgres_uri"],
                host=f["postgres_host"],
                user=f["postgres_user"],
                port=f["postgres_port"],
                password=f["postgres_password"],
                database=f["postgres_database"]))

        self.reddit = apraw.Reddit(
            client_id=f['reddit_id'],
            client_secret=f['reddit_secret'],
            user_agent="Eclipse")
        self.memes = []
        self.token = f["discord"]
        self.sra_api = f['some_random_api']
        self.launch_time = datetime.datetime.utcnow()
        self.color = discord.Color.from_rgb(156, 7, 241)
        with open("config/config.json", "r") as read_file:
            data = json.load(read_file)
            self.config = data

    async def on_ready(self):
        self.load_extension('jishaku')
        exceptions = ""
        for file in os.listdir("./cogs"):
            if file.endswith('.py'):
                try:
                    load_extension(self, f'cogs.{file[:-3]}', self.config)
                    print(f"loaded cogs.{file[:-3]}")
                except Exception as e:
                    exceptions += f"- {file} failed to load [{e}]\n"
                else:
                    exceptions += f"+ {file} loaded successfully\n"

        for file in os.listdir("./cogs/slash_cmds"):
            if file.endswith('.py'):
                try:
                    load_extension(self, f'cogs.slash_cmds.{file[:-3]}', self.config)
                    print(f"loaded cogs.slash_cmds.{file[:-3]}")
                except Exception as e:
                    exceptions += f"- {file} failed to load [{e}]\n"
                else:
                    exceptions += f"+ {file} loaded successfully\n"

        embed = discord.Embed(
            title="Bot ready!",
            description=f"Cogs status: \n ```diff\n{exceptions}```",
            color=bot.color)
        embed.timestamp = self.launch_time
        embed.set_footer(text="Bot online since:")
        c = bot.get_channel(840528237846331432)
        await c.send(embed=embed)

    async def process_commands(self, message):
        ctx = self.get_context(message)
        # satyamedh imma subclass context soon so i gotta override this meth dont mind me
        await self.invoke(ctx)


bot = Eclipse()

slash = SlashCommand(bot, override_type=True)


@bot.command()
@commands.has_permissions(administrator=True)
@commands.guild_only()
async def prefix(ctx, prefix):
    async with bot.pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute("UPDATE prefixes SET prefix = $1 WHERE guild_id = $2", prefix, ctx.guild.id)
    await ctx.send(f"My prefix in this server has successfully been changed to {prefix}\n\n **TIP:** To include "
                   f"spaces in the prefix do use quotes like {prefix}prefix \"hey \"")


if __name__ == "__main__":
    bot.run(bot.token)
