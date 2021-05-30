import asyncio
import datetime
import json
import multiprocessing
import os
import pickle
from threading import Thread

import asyncpraw as apraw
import asyncpg
import discord
from flask import Flask
from discord.ext import commands
from classes import proccessname_setter, context
from classes.LoadCog import load_extension


class CustomBot(commands.Bot):
    def __init__(self, command_prefix, **options):
        super().__init__(command_prefix, **options)

        pgloop = asyncio.get_event_loop()
        f = pickle.load(open('credentials.pkl', 'rb'))
        self.pool = pgloop.run_until_complete(
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
        self.gameboy = False
        self.color = discord.Color.from_rgb(156, 7, 241)
        with open("config/config.json", "r") as read_file:
            data = json.load(read_file)
            self.config = data
        self.flask_instance: Flask = None
        self.flask_thread: multiprocessing.Process = None
        self.prefixes = {}

    async def on_ready(self):
        prefixes = {}
        all_prefix_data = await _bot.pool.fetch("SELECT * FROM prefixes")
        all_guilds = await _bot.pool.fetch("SELECT guild_id FROM prefixes")
        for guild in all_guilds:
            g_prefixes = []
            for row in all_prefix_data:
                if row["guild_id"] == guild["guild_id"]:
                    g_prefixes.append(row["prefix"])
            prefixes[guild["guild_id"]] = g_prefixes

        self.prefixes = prefixes

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

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=context.Context)
        await self.invoke(ctx)

    def send_message_to_user(self, user: discord.User, message: str):
        loop = self.loop
        asyncio.run_coroutine_threadsafe(user.send(message), loop)

    def set_new_log_channel(self, guild, channel):
        loop = self.loop
        asyncio.run_coroutine_threadsafe(self._set_new_logging_channel(guild, channel), loop)

    async def _set_new_logging_channel(self, guild, channel):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("UPDATE logging SET channel_id=$2 WHERE server_id=$1", guild.id, channel.id)
