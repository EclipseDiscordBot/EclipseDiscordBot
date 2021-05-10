import discord
from discord_slash import SlashCommand
from classes import CustomBotClass

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
    roles=True)

bot = CustomBotClass.CustomBot(
    command_prefix=get_prefix,
    intents=intents,
    allowed_mentions=mentions,
    case_insensitive=True)

slash = SlashCommand(bot, override_type=True)


if __name__ == "__main__":
    bot.run(bot.token)
