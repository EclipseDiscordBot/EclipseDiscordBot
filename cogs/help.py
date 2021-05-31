import discord
from discord.ext import commands
from classes import CustomBotClass, buttons
import re


class BaseHelpView(discord.ui.View):
    def __init__(self, all_buttons: list):
        super().__init__()
        for button in all_buttons:
            self.add_item(button)


class BaseButton(discord.ui.Button):
    def __init__(self, label, embed: discord.Embed = None):
        super().__init__(style=discord.ButtonStyle.blurple, label=label)
        self.embed = embed

    async def callback(self, interaction):
        await interaction.message.edit(embed=self.embed)


class EclipseHelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.original_help_command = bot.help_command
        bot.help_command = None

    def cog_unload(self):
        self.bot.help_command = self.original_help_command

    def _caps(self, str):
        return re.sub(r"(\w)([A-Z])", r"\1 \2", str)

    async def get_cog_view(self, ctx, cog_name):
        cog = ctx.bot.get_cog(cog_name)
        cog_buttons = []
        for command in cog.get_commands():
            embed = discord.Embed(title=command.qualified_name, description=command.brief, color=ctx.bot.color)
            embed.add_field(name="Usage", value=f"```yaml\n{ctx.prefix}{command.qualified_name} {command.signature}")
            button = BaseButton(label=command.qualified_name, embed=embed)
            cog_buttons.append(button)
        return BaseHelpView(cog_buttons)

    async def get_bot_help(self, ctx):
        bot = ctx.bot
        embed = discord.Embed(title="Help", color=ctx.bot.color)
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
        dsc = "\n\n".join(f"**{cog_name}**" for cog_name in bot.cogs)
        new_dsc = self._caps(dsc)
        embed.description = new_dsc
        return embed

    async def get_command_help(self, ctx, command):
        embed = discord.Embed(title=command.qualified_name, description=command.brief, color=ctx.bot.color)
        embed.add_field(name="Usage", value=f"```yaml\n{ctx.prefix}{command.qualified_name} {command.signature}```")
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
        return embed

    async def get_cog_help(self, ctx, cog_name):
        embed = discord.Embed(title=cog_name)
        bot = ctx.bot
        cog = bot.get_cog(cog_name)
        embed.description = "\n\n".join(f"`{ctx.prefix}{command.qualified_name}`" for command in cog.get_commands())

    @commands.command(name="help", brief="Shows this message")
    async def help(self, ctx, subcommand=None):
        if subcommand is None:
            embed = await self.get_bot_help(ctx)
            base_buttons = []
            for cog_name in bot.cogs:
                cog = bot.get_cog(cog_name)
                embed = self.get_cog_help(ctx, cog)
                button = BaseButton(label=cog_name, embed=embed)
                base_buttons.append(button)
            await ctx.send(embed=embed, view=BaseHelpView(base_buttons))
            return

        if bot.get_command(subcommand) is not None:
            command = bot.get_command(subcommand)
            embed = await get_command_help(ctx, command)
            await ctx.send(embed=embed)
            return

        if bot.get_cog(subcommand) is not None:
            view = await self.get_cog_view(ctx, subcommand)
            embed = await self.get_cog_help(ctx, subcommand)
            await ctx.send(embed=embed, view=view)
            return


def setup(bot):
    bot.add_cog(EclipseHelpCommand(bot))
