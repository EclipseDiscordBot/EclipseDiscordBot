import discord
from discord.ext import commands
from classes import CustomBotClass, buttons


class BaseHelpView(discord.ui.View):
    def __init__(self, all_buttons: list):
        super().__init__()
        for button in all_buttons:
            self.add_item(button)


class BaseButton(discord.ui.Button):
    def __init__(self, label):
        super().__init__(style=discord.ButtonStyle.blurple, label=label)

    async def callback(self, interaction):
        await interaction.message.edit(content=self.label)


class EclipseHelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.original_help_command = bot.help_command
        bot.help_command = None

    def cog_unload(self):
        self.bot.help_command = self.original_help_command

    async def send_bot_help(self, ctx):
        bot = ctx.bot
        embed = discord.Embed(title="Help", color=ctx.bot.color)
        embed.description = "\n".join(f"**{cog_name}**" for cog_name in bot.cogs)
        base_buttons = []
        for cog_name in bot.cogs:
            button = BaseButton(label=cog_name)
            base_buttons.append(button)
        await ctx.send(embed=embed, view=BaseHelpView(base_buttons))

    async def send_command_help(self, ctx, command):
        pass

    async def send_cog_help(self, ctx, cog):
        pass

    @commands.command(name="help", brief="Shows this message")
    async def help(self, ctx, subcommand=None):
        if subcommand is None:
            await self.send_bot_help(ctx)
            return

        if bot.get_command(subcommand) is not None:
            command = bot.get_command(subcommand)
            await send_command_help(ctx, command)
            return

        if bot.get_cog(subcommand) is not None:
            cog = bot.get_cog(subcommand)
            await send_cog_help(ctx, cog)


def setup(bot):
    bot.add_cog(EclipseHelpCommand(bot))
