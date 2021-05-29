import discord
from discord.ext import commands
from classes import CustomBotClass, buttons


class EclipseHelpCommand(commands.HelpCommand):
    def get_command_signature(self, command):
        return f"{command.qualified_name} {command.signature}"

    async def send_bot_help(self, mapping):
        ctx = self.context
        bot_prefix = ""
        embed = discord.Embed(
            title="Help",
            description=f"Type *`{bot_prefix}help <category>`* for more info on a category.",
            color=ctx.bot.color)
        for cog, command in mapping.items():
            all_cmds = [f"`{c.qualified_name}`" for c in command]
            if all_cmds:
                cog_name = getattr(cog, "qualified_name", "No Category")
                embed.add_field(
                    name=cog_name,
                    value=" ".join(all_cmds),
                    inline=False)
        await ctx.send(embed=embed, view=buttons.Links())

    async def send_cog_help(self, cog):
        ctx = self.context
        embed = discord.Embed(
            title=f"{cog.qualified_name} Commands",
            color=ctx.bot.color)
        all_commands = cog.get_commands()
        dsc = ""
        for command in all_commands:
            dsc += f"**{command.qualified_name}** - {command.brief}\n"
        embed.description = dsc
        await ctx.send(embed=embed, view=buttons.Links())

    async def send_command_help(self, command):
        ctx = self.context
        # prefix = self.clean_prefix
        embed = discord.Embed(
            title=command.qualified_name,
            color=ctx.bot.color)
        embed.description = command.brief
        embed.add_field(
            name="Usage",
            value=f"```{self.get_command_signature(command)}```")
        if command.aliases:
            a_str = ""
            for a in command.aliases:
                a_str += f"`{a}` "
            embed.add_field(name="Aliases", value=a_str)
        bool_can = await command.can_run(ctx)
        if bool_can:
            can_txt = "This command can be used by you"
        else:
            can_txt = "This command cannot be used by you"
        embed.set_footer(text=can_txt)
        await ctx.send(embed=embed, view=buttons.Links())


class _Help(commands.Cog):
    def __init__(self, bot: CustomBotClass.CustomBot):
        self._original_help_command = bot.help_command
        bot.help_command = EclipseHelpCommand()
        bot.help_command.cog = self
        self.bot = bot

    def cog_unload(self):
        self.bot.help_command = self._original_help_command


def setup(bot):
    bot.add_cog(_Help(bot))
