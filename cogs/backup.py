from discord import Embed
import discord
from discord.ext import commands
from classes import CustomBotClass, indev_check, context, ignore, is_guild_owner, get_permissions_overwrites


class Backup(commands.Cog):
    def __init__(self, bot: CustomBotClass.CustomBot):
        self.bot = bot
        ignore.ignore(ignore)

        # TODO FInish backup.py

    @commands.command("backup", brief="backup your server")
    @indev_check.command_in_development()
    @commands.guild_only()
    @is_guild_owner.is_guild_owner()
    async def _backup(self, ctx: context.Context):
        desc = f"Loading! <a:loading:847105845379727420>"
        e = Embed(title="Starting backup process!", description=desc)
        message = await ctx.send(embed=e)
        guild: discord.Guild = ctx.guild
        channels = guild.channels
        for channel in channels:
            channel_dict = {
                "name": channel.name,
                "permissions": [get_permissions_overwrites.get_overwrites(role, member) for role, member in
                                channel.overwrites.items()]
            }
            print(channel_dict)


def setup(bot):
    bot.add_cog(Backup(bot))
