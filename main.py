import discord
from discord.ext import commands
from discord_slash import SlashCommand
from classes import CustomBotClass
import os
from classes.LoadCog import load_extension

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


@bot.event
async def on_ready():
    bot.load_extension('jishaku')
    exceptions = ""
    for file in os.listdir("./cogs"):
        if file.endswith('.py'):
            try:
                load_extension(bot, f'cogs.{file[:-3]}', bot.config)
                print(f"loaded cogs.{file[:-3]}")
            except Exception as e:
                exceptions += f"- {file} failed to load [{e}]\n"
            else:
                exceptions += f"+ {file} loaded successfully\n"

    for file in os.listdir("./cogs/slash_cmds"):
        if file.endswith('.py'):
            try:
                load_extension(bot, f'cogs.slash_cmds.{file[:-3]}', bot.config)
                print(f"loaded cogs.slash_cmds.{file[:-3]}")
            except Exception as e:
                exceptions += f"- {file} failed to load [{e}]\n"
            else:
                exceptions += f"+ {file} loaded successfully\n"

    embed = discord.Embed(
        title="Bot ready!",
        description=f"Cogs status: \n ```diff\n{exceptions}```",
        color=bot.color)
    embed.timestamp = bot.launch_time
    embed.set_footer(text="Bot online since:")
    c = bot.get_channel(840528237846331432)
    await c.send(embed=embed)


async def on_message(message):
    if bot.user.mentioned_in(message):
        if not message.guild:
            await message.reply("Hello! My prefix here is *`e!`*!")
        else:
            async with bot.pool.acquire() as conn:
                async with conn.transaction():
                    prefix = await conn.fetchval("SELECT prefix FROM prefixes WHERE guild_id = $1", message.guild.id)
            await message.reply(f"Hello! My prefix here is *`{prefix}`*!")

    await bot.process_commands(message)


@bot.command()
@commands.has_permissions(administrator=True)
@commands.guild_only()
async def prefix(ctx, prefix):
    async with bot.pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute("UPDATE prefixes SET prefix = $1 WHERE guild_id = $2", prefix, ctx.guild.id)
    await ctx.send(f"My prefix in this server has successfully been changed to {prefix}\n\n **TIP:** To include "
                   f"spaces in the prefix do use quotes like {prefix}prefix \"hey \"")



if __name__ == "__main__":
    bot.run(bot.token)
