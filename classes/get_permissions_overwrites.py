from typing import Mapping, Union

import discord
from discord import PermissionOverwrite, Member, Role


def get_overwrites(arg: discord.Role, arg2: discord.PermissionOverwrite):
    return {
        "role_name": arg.name,
        "is_default": arg.is_default(),
        "is_bot": arg.is_bot_managed(),
        "is_boost": arg.is_premium_subscriber(),

    }
