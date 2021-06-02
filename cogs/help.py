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
    def __init__(self, label, embed: discord.Embed = None, ctx: commands.Context = None, custom_view:discord.ui.View=None):
        if label == "Exit":
            super().__init__(style=discord.ButtonStyle.red, label="Exit")
            self.embed = None
            self.custom_view = None
            self.ctx = ctx
        else:
            super().__init__(style=discord.ButtonStyle.blurple, label=re.sub("([A-Z])", " \\1", label).strip())
            self.embed = embed
            self.custom_view = custom_view
            self.ctx = ctx

    async def callback(self, interaction):
        if interaction.user.id == self.ctx.author.id:
            if self.custom_view is not None:
                await interaction.message.edit(embed=self.embed, view=self.custom_view)
            if self.custom_view is None:
                await interaction.message.edit(embed=self.embed)
        else:
            await interaction.response.send_message(f"Hey, that button can only be used by {ctx.author}! "
                                                    f"Do {ctx.prefix}help if you want help!", ephemeral=True)


class EclipseHelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.original_help_command = bot.help_command
        bot.help_command = None

    def cog_unload(self):
        self.bot.help_command = self.original_help_command

    def _caps(self, str):
        return re.sub("([A-Z])", " \\1", str).strip()

    async def get_cog_view(self, ctx, cog_name):
        cog = ctx.bot.get_cog(cog_name)
        cog_buttons = []
        for command in cog.get_commands():
            embed = await self.get_command_help(ctx, command)
            button = BaseButton(label=command.qualified_name, embed=embed, ctx=ctx)
            cog_buttons.append(button)
        exit = BaseButton(label="Exit")
        return BaseHelpView(cog_buttons)

    async def get_bot_help(self, ctx):
        bot = ctx.bot
        embed = discord.Embed(title="Help", color=ctx.bot.color)
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
        dsc = "\n\n".join(f"**{cog_name}**" for cog_name in bot.cogs)
        new_dsc = self._caps(dsc)
        embed.description = new_dsc
        return embed

    async def get_command_help(self, ctx, command):  # yes
        embed = discord.Embed(title=command.qualified_name, description=command.brief, color=ctx.bot.color)
        embed.add_field(name="Usage", value=f"```yaml\n{ctx.prefix}{command.qualified_name} {command.signature}```")
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
        if command.aliases:
            embed.add_field(name="Aliases", value=" ".join(f"`{alias}`" for alias in command.aliases))
        return embed

    async def get_cog_help(self, ctx, cog_name):
        embed = discord.Embed(title=cog_name, color=self.bot.color)
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
        bot = ctx.bot
        cog = bot.get_cog(cog_name)
        embed.description = "\n\n".join(f"`{ctx.prefix}{command.qualified_name}`" for command in cog.get_commands())
        return embed

    @commands.command(name="help", brief="Shows this message")
    async def help(self, ctx, subcommand=None):
        bot = ctx.bot
        if subcommand is None:
            act_embed = await self.get_bot_help(ctx)
            base_buttons = []
            for cog_name in bot.cogs:
                embed = await self.get_cog_help(ctx, cog_name)
                view = await self.get_cog_view(ctx, cog_name)
                button = BaseButton(label=cog_name, embed=embed, ctx=ctx, custom_view=view)
                base_buttons.append(button)
            exit = BaseButton(label="Exit")
            base_buttons.append(exit)
            await ctx.send(embed=act_embed, view=BaseHelpView(base_buttons))
            return

        if bot.get_command(subcommand) is not None:
            command = bot.get_command(subcommand)
            embed = await self.get_command_help(ctx, command)
            await ctx.send(embed=embed)
            return

        if bot.get_cog(subcommand) is not None:
            view = await self.get_cog_view(ctx, subcommand)
            embed = await self.get_cog_help(ctx, subcommand)
            await ctx.send(embed=embed, view=view)
            return


def setup(bot):
    bot.add_cog(EclipseHelpCommand(bot))
