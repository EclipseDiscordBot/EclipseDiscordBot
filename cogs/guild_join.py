from discord.ext import commands
from classes import CustomBotClass


class GuildJoin(commands.Cog):
    def __init__(self, bot: CustomBotClass.CustomBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("INSERT INTO prefixes (guild_id, prefix) VALUES ($1, $2)", guild.id, "e!")
                await conn.execute(
                    "INSERT INTO greet (guild_id, config, channel_id, msg, delafter) VALUES ($1, $2, $3, $4, $5)",
                    guild.id,
                    0, 0, "placeholder", 0)
                await conn.execute("INSERT INTO logging(server_id,channel_id,enabled) VALUES($1,$2,$3)",
                                   guild.id, 0, False)
                await conn.execute("INSERT INTO automeme(server_id,channel_id,enabled) VALUES($1,$2,$3)",
                                   guild.id, 0, False)
                await conn.execute("INSERT INTO config(math,server_id,invite_tracker_enable,invite_tracker_channel) VALUES($1,$2,$3,$4)",
                                   False, guild.id, False, 0)

    @commands.Cog.listener()
    async def on_guild_leave(self, guild):
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("DELETE FROM prefixes WHERE guild_id = $1", guild.id)
                await conn.execute("DELETE FROM greet WHERE guild_id = $1", guild.id)
                await conn.execute("DELETE FROM logging WHERE server_id=$1", guild.id)
                await conn.execute("DELETE FROM automeme WHERE server_id=$1", guild.id)
                await conn.execute("DELETE FROM config WHERE server_id=$1", guild.id)


def setup(bot):
    bot.add_cog(GuildJoin(bot))
