import discord
from discord.ext import commands


class EclipseHelpCommand(commands.HelpCommand):
    def get_command_signature(self, command):
        return f"{self.clean_prefix}{command.qualified_name} {command.signature}"

    # todo fix dis! @zapd0s! it doesnt even show description!

    async def send_bot_help(self, mapping):
        ctx = self.context
        bot_prefix = self.clean_prefix
        embed = discord.Embed(title="Help", description = f"Type `{bot_prefix}help <command>` for more info on a command.\nYou can also type `{bot_prefix}help <category>` for more info on a category.", color = ctx.bot.color)
        for cog, commands in mapping.items():
            all_cmds = [f"{c.qualified_name}" for c in commands]
            if all_cmds:
                cog_name = getattr(cog, "qualified_name", "No Category")
                embed.add_field(name=cog_name, value=" ".join(all_cmds), inline=False)
        await ctx.send(embed = embed)

    async def send_cog_help(self, cog):
        ctx = self.context
        embed = discord.Embed(title = f"{cog.qualified_name} Commands", color = ctx.bot.color)
        all_commands = cog.get_commands()
        dsc = ""
        for command in all_commands:
            dsc += f"**{command.qualified_name}** - {command.brief}\n"

        embed.description=dsc
        await ctx.send(embed=embed)





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
