import discord
import aiohttp
from discord.ext import commands


class Chatbot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def chatbot_handler(self, message: discord.Message):
        if not message.guild:
            return
        if message.author.bot:
            return
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                data = await conn.fetchrow('SELECT channel_id FROM chatbot WHERE guild_id = $1', message.guild.id)
                if not data:
                    return
                if message.guild.id != int(data['guild_id']):
                    return
                if message.channel.id != int(data['channel_id'])
                return
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"http://api.brainshop.ai/get?bid={self.bot.brain_id}&key={self.bot.brain_api}&uid={uid}&msg={msg}") as resp:
                        if resp.status != 200:
                            return await message.reply("Sorry something went wrong while accessing the BrainShop API! It has been reported immediately!",
                                                       mention_author=False)
                        await message.reply(js["cnt"], mention_author=False)


def setup(bot):
    bot.add_cog(Chatbot(bot))
