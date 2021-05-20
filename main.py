from constants import basic
import discord
from discord.ext import commands, tasks
from discord_slash import SlashCommand
from classes import CustomBotClass, proccessname_setter
from scripts.python_scripts import stats_webhook


intents = discord.Intents.all()


async def get_prefix(eclipse, message):
    base = []
    if message.author.id in basic.owners:
        base.append("")
    if not message.guild:
        base.append("e! ")
        base.append("e!")
        return base
    async with eclipse.pool.acquire() as conn:
        async with conn.transaction():
            prefixes = await conn.fetch("SELECT prefix FROM prefixes WHERE guild_id = $1", message.guild.id)
            for prefix in prefixes:
                base.append(prefix['prefix'])
    return commands.when_mentioned_or(*base)(bot, message)


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

@tasks.loop(minutes=5)
async def update_stats_loop():

    await stats_webhook.update_stats(bot)


slash = SlashCommand(bot, override_type=True)

if __name__ == "__main__":
    proccessname_setter.try_set_process_name("eclipse_booting")
    update_stats_loop.start()
    bot.run(bot.token)
