import asyncio
import datetime
import json
import os
import pickle
import asyncpraw as apraw
import asyncpg
import discord
from discord.ext import commands

from classes import proccessname_setter
from classes.LoadCog import load_extension


class CustomBot(commands.Bot):
    def __init__(self, command_prefix, **options):
        super().__init__(command_prefix, **options)

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
        self.brain_id = f['brain_id']
        self.brain_api = f['brain_api']
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
                    load_extension(
                        self, f'cogs.slash_cmds.{file[:-3]}', self.config)
                    print(f"loaded cogs.slash_cmds.{file[:-3]}")
                except Exception as e:
                    exceptions += f"- {file} failed to load [{e}]\n"
                else:
                    exceptions += f"+ {file} loaded successfully\n"

        embed = discord.Embed(
            title="Bot ready!",
            description=f"Cogs status: \n ```diff\n{exceptions}```",
            color=self.color)
        embed.timestamp = self.launch_time
        embed.set_footer(text="Bot online since:")
        c = self.get_channel(840528237846331432)
        proccessname_setter.try_set_process_name("eclipse_online")
        await c.send(embed=embed)

    async def on_message(self, message):
        if self.user.mentioned_in(message):
            if not message.guild:
                await message.reply("Hello! My prefix here is *`e!`*!")
            else:
                async with self.pool.acquire() as conn:
                    async with conn.transaction():
                        prefixes = await conn.fetchval("SELECT prefix FROM prefixes WHERE guild_id = $1",
                                                       message.guild.id)
                await message.reply(f"Hello! My prefix here is *`{prefixes}`*!")

        await self.process_commands(message)
