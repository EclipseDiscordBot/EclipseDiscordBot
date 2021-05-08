import asyncio
import datetime
import json
import pickle
import asyncpraw as apraw
import asyncpg
import discord
from discord.ext import commands


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

        self.token = f["discord"]

        self.sra_api = f['some_random_api']

        self.launch_time = datetime.datetime.utcnow()

        self.color = discord.Color.from_rgb(156, 7, 241)

        with open("config/config.json", "r") as read_file:
            data = json.load(read_file)
            self.config = data
