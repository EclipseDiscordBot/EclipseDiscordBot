import random
from typing import List
import discord
from discord.ext import commands, tasks
from classes import CustomBotClass, proccessname_setter, stats_webhook
from constants import basic
from flask import Flask
from threading import Thread
from flask import request

intents = discord.Intents.all()


async def get_prefix(eclipse, message):
    base = []
    if message.author.id in basic.owners or message.author.id in eclipse.owner_ids:
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
    replied_user=True,
    roles=True)

bot = CustomBotClass.CustomBot(
    command_prefix=get_prefix,
    intents=intents,
    allowed_mentions=mentions,
    case_insensitive=True,
    strip_after_prefix=True)


@tasks.loop(minutes=1)
async def update_stats_loop():
    await stats_webhook.update_stats(bot)


app = Flask(__name__)

response_templates = {
    "success": {
        "success": True
    },

    "failure": {
        "success": False
    }
}

otps = {}


@app.route('/mutual-guild')
async def mutual_guilds():
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
                guild = {
                    "name": str(server),
                    "id": str(server.id),
                    "logo": str(server.icon.url) if server.icon else None
                }
                final_list.append(guild)
                break
    if not final_list:
        response_json = response_templates['failure'].copy()
        response_json['reason'] = 'no_mutual_guilds_with_manage_server_permission'
        return response_json
    response_json['result'] = final_list
    return response_json


@app.route("/channels")
async def channels():
    guild_id = request.args.get('id', default=0, type=str)
    try:
        guild_id = int(guild_id)
    except ValueError:
        response_json = response_templates['failure'].copy()
        response_json['reason'] = 'id_not_int_convertible'
        return response_json
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
            "id": str(channel.id)
        }
        final_channels.append(channel_json)

    response_json = response_templates['success'].copy()
    response_json['result'] = final_channels
    return response_json


@app.route("/update-log-channel")
async def logging_channel_update():
    guild_id = request.args.get('gid', default=0, type=str)
    user_id = request.args.get('uid', default=0, type=str)
    new_log_channel_id = request.args.get('nlcid', default=0, type=str)
    check_id = request.args.get('check_id', default=None, type=str)
    code = request.args.get('code', default=None, type=int)

    if user_id == 0 or guild_id == 0 or new_log_channel_id == 0 or check_id is None or code is None:
        response_json = response_templates['failure'].copy()
        response_json['reason'] = 'default_or_zero_id'
        return response_json
    try:
        user_id = int(user_id)
        guild_id = int(guild_id)
        new_log_channel_id = int(new_log_channel_id)
    except ValueError:
        response_json = response_templates['failure'].copy()
        response_json['reason'] = 'ids_not_int_convertible'
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
    guild: discord.Guild = bot.get_guild(guild_id)
    if guild is None:
        response_json = response_templates['failure'].copy()
        response_json['reason'] = 'invalid_guild_id_or_unknown_guild'
        return response_json
    channel = guild.get_channel(new_log_channel_id)
    if channel is None:
        response_json = response_templates['failure'].copy()
        response_json['reason'] = 'invalid_channel_id_or_unknown_channel'
        return response_json
    if not str(otps[check_id]) == str(code):
        response_json = response_templates['failure'].copy()
        response_json['reason'] = 'wrong_otp'
        return response_json
    bot.set_new_log_channel(guild, channel)
    return {
        "success": True
    }


@app.route("/code")
async def gen_code():
    user_id = request.args.get('uid', default=0, type=str)
    scope = request.args.get('scope', default=None, type=int)
    guild_id = request.args.get('gid', default=0, type=str)
    if scope is None:
        response_json = response_templates['failure'].copy()
        response_json['reason'] = 'no_scope_given'
        return response_json
    if scope not in basic.scopes.copy().keys():
        response_json = response_templates['failure'].copy()
        response_json['reason'] = 'unknown_scope'
    if not user_id:
        response_json = response_templates['failure'].copy()
        response_json['reason'] = 'parameters_not_specified'
        return response_json
    try:
        user_id = int(user_id)
        guild_id = int(guild_id)
    except ValueError:
        response_json = response_templates['failure'].copy()
        response_json['reason'] = 'id_not_int_convertible'
        return response_json
    user: discord.User = bot.get_user(user_id)
    if user is None:
        response_json = response_templates['failure'].copy()
        response_json['reason'] = 'invalid_user_id_or_unknown_user'
        return response_json
    guild: discord.Guild = bot.get_guild(guild_id)
    if guild is None:
        response_json = response_templates['failure'].copy()
        response_json['reason'] = 'unknown_guild'
        return response_json
    try:
        code = ''.join(random.choices("0123456789", k=6))
        check_id = ''.join(random.choices("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz", k=24))
        otps[check_id] = code
        message = f'Hello! just barely made it through some cables, routers, ISPs and satellites to your discord DMs, anyway here\'s a very important code! this code allows anybody to `{basic.scopes[scope]}` in `{guild.name}`! so don\'t share it with anybody! \n `{code}`\n Code not working? join the support server at {basic.support_server} and ask <@605364556465963018>'
        bot.send_message_to_user(user, message)

        return {
            'success': True,
            "check_id": check_id,
            "scope": str(scope)
        }
    except discord.Forbidden or discord.HTTPException as e:
        response_json = response_templates['failure'].copy()
        response_json['reason'] = "dms_not_open"
        return response_json


def begin_flask():
    app.run(port=8076, host="0.0.0.0")


if __name__ == "__main__":
    proccessname_setter.try_set_process_name("eclipse_booting")
    thr = bot.flask_thread = Thread(target=begin_flask)
    thr.daemon = True
    thr.start()
    bot.flask_instance = app
    update_stats_loop.start()
    bot.run(bot.token)
