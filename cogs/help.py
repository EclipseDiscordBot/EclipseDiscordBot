import discord
from discord.ext import commands


class EclipseHelpCommand(commands.HelpCommand):
    def get_command_signature(self, command):
        return f"{self.clean_prefix}{command.qualified_name} {command.signature}"

    async def send_bot_help(self, mapping):
        ctx = self.context
        embed = discord.Embed(title="Help", color=ctx.bot.color)
        prefix = self.clean_prefix
        for cog, commands in mapping.items():
            cog_name = getattr(cog, "qualified_name", "No Category")
            cmd_str = ""
            for cmd in commands:
                cmd_str += f"`{cmd.qualified_name}, `"
            embed.add_field(name=cog_name, value=cmd_str)
        embed.description = f"Type `{prefix}help <command>` for more information on a command\n" \
                            f"You can also type `{prefix}help <category>` for more info on a category" \
                            f"**Note that this help command shows only the commands that you can use**"
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        embed.set_footer(text="Eclipse", icon_url=ctx.bot.user.avatar_url)
        await ctx.reply(embed=embed)


class help(commands.Cog):
    def __init__(self, bot):
        self._original_help_command = bot.help_command
        bot.help_command = EclipseHelpCommand()
        bot.help_command.cog = self
        self.bot = bot

    def cog_unload(self):
        self.bot.help_command = self._original_help_command


def setup(bot):
    bot.add_cog(help(bot))
