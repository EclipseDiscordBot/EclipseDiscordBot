import random
from classes import CustomBotClass
import asyncpraw as apraw
import discord
from discord.ext import commands, tasks


class AutoMeme(commands.Cog, name="Auto Meme Cog"):
    def __init__(self, bot: CustomBotClass.CustomBot):
        self.bot = bot
        self.reddit: apraw.Reddit = self.bot.reddit
        self._automeme.start()

    @commands.command(name="automeme", brief="Sets up automeme in a channel")
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    @commands.cooldown(1, 3600, discord.ext.commands.BucketType.member)
    async def automeme(self, ctx, channel:discord.TextChannel, toggle):
        """
        Setup a channel for the bot to send a meme every 5 minutes in.
        :param ctx:
        :param toggle:
        :param channel:
        :return:
        """
        positive = ["yes", "true", "1"]
        negative = ["no", "false", "0"]
        if toggle in positive:
                    bool_toggle = True
        elif toggle in negative:
                    bool_toggle = False
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("UPDATE automeme SET channel_id=$1,enabled=$2 WHERE server_id=$3",
                                   (0 if not toggle else channel.id), bool_toggle, ctx.guild.id)
        await ctx.reply("done!")

    @tasks.loop(minutes=5)
    async def _automeme(self):
        memes_subreddit = await self.reddit.subreddit("memes")
        async for hot_post in memes_subreddit.hot(limit=100):
            e = discord.Embed(title=hot_post.title, color=self.bot.color)
            e.set_image(url=hot_post.url)
            e.set_footer(text=f'\U00002b06 {hot_post.score} | API by Reddit')
            self.bot.memes.append(e)

        random_post = self.bot.memes[random.randint(
            0, len(self.bot.memes) - 1)]
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                data = await conn.fetch("SELECT * FROM automeme")
                for row in data:
                    if row['enabled']:
                        try:
                            guild: discord.Guild = self.bot.get_guild(
                                id=row['server_id'])
                            channel: discord.TextChannel = guild.get_channel(
                                row['channel_id'])
                        except AttributeError:
                            continue
                        try:
                            await channel.send(embed=random_post)
                        except AttributeError:
                            await conn.execute("DELETE FROM automeme WHERE server_id=$1", row['server_id'])


def setup(bot):
    bot.add_cog(AutoMeme(bot))
