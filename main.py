from typing import List
import multiprocessing
from constants import basic
import discord
from discord.ext import commands, tasks
from discord_slash import SlashCommand
from classes import CustomBotClass, proccessname_setter
from flask import Flask
from flask import request
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


@tasks.loop(minutes=1)
async def update_stats_loop():
    await stats_webhook.update_stats(bot)


slash = SlashCommand(bot, override_type=True)

app = Flask(__name__)

response_templates = {
    "success": {
        "success": True
    },

    "failure": {
        "success": False
    }
}


@app.route('/mutual-guild')
def mutual_guilds():
    user_id = request.args.get('id', default=0, type=int)
    if user_id == 0:
        response_json = response_templates['failure'].copy()
        response_json['reason'] = 'default_or_zero_id'
        return response_json
    if not bot.is_ready():
        response_json = response_templates['failure'].copy()
        response_json['reason'] = 'bot_not_ready'
        return response_json
    user: discord.User = bot.get_user(user_id)
    if user is None:
        response_json = response_templates['failure'].copy()
        response_json['reason'] = 'invalid_user_id_or_unknown_user'
        return response_json
    mutual_guildss = user.mutual_guilds
    if not mutual_guilds:
        response_json = response_templates['failure'].copy()
        response_json['reason'] = 'no_mutual_guilds'
        return response_json
    response_json = response_templates['success'].copy()
    final_list = []
    for server in mutual_guildss:
        server: discord.Guild
        member: discord.Member = server.get_member(user_id)
        roles: List[discord.Role] = member.roles
        for role in roles:
            role: discord.Role
            if role.permissions.manage_guild or role.permissions.administrator or member == server.owner:
                print(server.id)
                guild = {
                    "name": str(server),
                    "id": str(server.id),
                    "logo": str(server.icon_url) if server.icon_url else hash(server.icon_url)
                }
                final_list.append(guild)
                print(guild)
                break
    if not final_list:
        response_json = response_templates['failure'].copy()
        response_json['reason'] = 'no_mutual_guilds_with_manage_server_permission'
        return response_json
    response_json['result'] = final_list
    return response_json


@app.route("/channels")
def channels():
    guild_id = request.args.get('id', default=0, type=int)
    if guild_id == 0:
        response_json = response_templates['failure'].copy()
        response_json['reason'] = 'no_guild_id_specified'
        return response_json
    if not bot.is_ready():
        response_json = response_templates['failure'].copy()
        response_json['reason'] = 'bot_not_ready'
        return response_json
    guild: discord.Guild = bot.get_guild(guild_id)
    if guild is None:
        response_json = response_templates['failure'].copy()
        response_json['reason'] = 'unknown_guild'
        return response_json
    channels = guild.channels
    if channels is None:
        response_json = response_templates['failure'].copy()
        response_json['reason'] = 'no_channels_in_guild'
        return response_json
    final_channels = []
    for channel in channels:
        if not isinstance(channel, discord.TextChannel): continue
        channel: discord.TextChannel
        channel_json = {
            "name": channel.name,
            "id": channel.id
        }
        final_channels.append(channel_json)

    response_json = response_templates['success'].copy()
    response_json['result'] = final_channels
    return response_json


def begin_flask():
    app.run(port=8076)


if __name__ == "__main__":
    proccessname_setter.try_set_process_name("eclipse_booting")
    thr = bot.flask_thread = multiprocessing.Process(target=begin_flask, args=())
    thr.start()
    bot.flask_instance = app
    update_stats_loop.start()
    bot.run(bot.token)
