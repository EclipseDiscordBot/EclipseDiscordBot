from typing import List

from constants import basic
import discord
from discord.ext import commands, tasks
from discord_slash import SlashCommand
from classes import CustomBotClass, proccessname_setter
from flask import Flask
from threading import Thread
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

@tasks.loop(minutes=5)
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
        response_json['reason'] = 'invalid_user_id'
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
            if role.permissions.manage_guild or role.permissions.administrator:
                guild = {
                    "name": str(server),
                    "id": server.id,
                    "logo": str(server.icon_url) if server.icon_url else hash(server.icon_url)
                }
                final_list.append(guild)
                break
    if not final_list:
        response_json = response_templates['failure'].copy()
        response_json['reason'] = 'no_mutual_guilds_with_manage_server_permission'
        return response_json
    response_json['result'] = final_list
    return response_json


def begin_flask():
    app.run(port=8076)


if __name__ == "__main__":
    proccessname_setter.try_set_process_name("eclipse_booting")
    thr = Thread(target=begin_flask)
    thr.daemon = True
    thr.start()
    update_stats_loop.start()
    bot.run(bot.token)
