import discord
import wavelink
from discord.ext import commands


class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        if not hasattr(bot, 'wavelink'):
            self.bot.wavelink = wavelink.Client(bot=self.bot)

        self.bot.loop.create_task(self.start_nodes())

    async def start_nodes(self):
        await self.bot.wait_until_ready()
        await self.bot.wavelink.initiate_node(host='127.0.0.1',
                                              port=2333,
                                              rest_uri='http://127.0.0.1:2333',
                                              password=self.bot.lavalink_passwd,
                                              identifier='TEST',
                                              region='us_central')

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

        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.is_connected:
            await ctx.invoke(self.connect_)

        await ctx.send(f'Added {str(tracks[0])} to the queue.')
        await player.play(tracks[0])

    @commands.command(aliases=['end'], name="stop", brief="Stops playing songs")
    async def stop(self, ctx):
        player: wavelink.Player = self.bot.wavelink.get_player(ctx.guild.id)
        await ctx.reply("Stopped")
        await player.stop()

    @commands.command(aliases=['w8', 'wait'], name="pause", brief="Pauses music")
    async def pause(self, ctx):
        player: wavelink.Player = self.bot.wavelink.get_player(ctx.guild.id)
        await ctx.reply("Paused")
        await player.set_pause(True)

    @commands.command(aliases=['r'], name="resume", brief="Resumes music")
    async def resume(self, ctx):
        player: wavelink.Player = self.bot.wavelink.get_player(ctx.guild.id)
        await ctx.reply("Resumed")
        await player.set_pause(False)

    @commands.command(aliases=['l'], name="leave", brief="Leaves the VC")
    async def leave(self, ctx):
        player: wavelink.Player = self.bot.wavelink.get_player(ctx.guild.id)
        await ctx.reply("Bye!")
        await player.disconnect()


def setup(bot):
    bot.add_cog(Music(bot))
