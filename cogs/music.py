import asyncio
from typing import Dict, List, Union

import discord
import wavelink
from discord.ext import commands, tasks


class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        if not hasattr(bot, 'wavelink'):
            self.bot.wavelink = wavelink.Client(bot=self.bot)

        self.bot.loop.create_task(self.start_nodes())
        self.queue: Dict[wavelink.Player, List[wavelink.Track]] = {}
        # self.loop: Dict[wavelink.Player, Dict[str, Union[int, bool]]] = {}

    async def start_nodes(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(10)
        await self.bot.wavelink.initiate_node(host='127.0.0.1',
                                              port=2333,
                                              rest_uri='http://127.0.0.1:2333',
                                              password=self.bot.lavalink_passwd,
                                              identifier='TEST',
                                              region='us_central')
        self.next_song.start()

    @commands.command(name='connect', brief="Connects to your VC")
    async def connect_(self, ctx, *, channel: discord.VoiceChannel = None):
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                raise discord.DiscordException('No channel to join. Please either specify a valid channel or join one.')

        player = self.bot.wavelink.get_player(ctx.guild.id)
        await ctx.send(f'Connecting to **`{channel.name}`**')
        await player.connect(channel.id)

    @commands.command(aliases=['queue', 'pl'], name="play", brief="searches and plays a song")
    async def play(self, ctx, *, query: str):
        tracks = await self.bot.wavelink.get_tracks(f'ytsearch:{query}')

        if not tracks:
            return await ctx.send('Could not find any songs with that query.')

        player: wavelink.Player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.is_connected:
            await ctx.invoke(self.connect_)

        if player not in list(self.queue.values()):
            self.queue[player] = []
        self.queue[player].append(tracks[0])
        await ctx.send(f'Added `{str(tracks[0])}` to the queue.')

    @commands.command(aliases=['end'], name="stop", brief="Stops playing songs")
    async def stop(self, ctx):
        player: wavelink.Player = self.bot.wavelink.get_player(ctx.guild.id)
        await ctx.reply("Stopped")
        await player.stop()
        self.queue[player] = []

    @commands.command(aliases=['w8', 'wait', 'p'], name="pause", brief="Pauses music")
    async def pause(self, ctx):
        player: wavelink.Player = self.bot.wavelink.get_player(ctx.guild.id)
        await ctx.reply("Paused")
        await player.set_pause(True)

    @commands.command(aliases=['r'], name="resume", brief="Resumes music")
    async def resume(self, ctx):
        player: wavelink.Player = self.bot.wavelink.get_player(ctx.guild.id)
        await ctx.reply("Resumed")
        await player.set_pause(False)

    @commands.command(aliases=['l', 'disconnect'], name="leave", brief="Leaves the VC")
    async def leave(self, ctx):
        player: wavelink.Player = self.bot.wavelink.get_player(ctx.guild.id)
        await ctx.reply("Bye!")
        await player.disconnect()

    @commands.command(aliases=['s', 'ski'], name="skip", brief="Skips the current song")
    async def skip(self, ctx):
        player: wavelink.Player = self.bot.wavelink.get_player(ctx.guild.id)
        queue = self.queue[player]
        await ctx.reply(f"Skipping")
        await player.stop()

        if not len(queue) == 0:
            await player.play(queue[0])
            queue.pop(0)

    @tasks.loop(seconds=1)
    async def next_song(self):
        for player, queue in self.queue.items():
            if not player.is_playing:
                if not len(queue) == 0:
                    await player.play(queue[0])
                    queue.pop(0)

    @commands.command(name="volume", aliases=['vol'], brief="Changes the volume")
    async def _volume(self, ctx: commands.Context, volume: int=None):
        player: wavelink.Player = self.bot.wavelink.get_player(ctx.guild.id)
        if volume is None:
            await ctx.reply(f'Current volume is {player.volume}')
            return

        if volume < 0 or volume > 1000:
            await ctx.reply("Invalid volume, keep it between 0 and 1000")
            return

        await player.set_volume(volume)
        await ctx.reply(f"Done! The volume is now {player.volume}")

def setup(bot):
    bot.add_cog(Music(bot))
