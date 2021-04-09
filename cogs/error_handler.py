import os
import random

import discord
import traceback
import sys
from discord.ext import commands


class ErrorHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        if hasattr(ctx.command, 'on_error'):
            return

        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ignored = (commands.CommandNotFound, commands.NotOwner)
        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return

        if isinstance(error, commands.DisabledCommand):
            title = "Disabled Command"
            dsc = f"`{ctx.command}` has been disabled by the developers. Please try later!"
            embed = discord.Embed(title=title, description=dsc, color=discord.Color.random())
            await ctx.reply(embed=embed)

        elif isinstance(error, commands.NoPrivateMessage):
            title = "Server Command"
            dsc = f"`{ctx.command}` can only be used in a server!"
            embed = discord.Embed(title=title, description=dsc, color=discord.Color.random())
            await ctx.reply(embed=embed)

        elif isinstance(error, commands.UserInputError):
            title = "Input Error"
            dsc = "Oops! You've made a mistake while giving me input! Please correct it and try again!"
            embed = discord.Embed(title=title, description=dsc, color=discord.Color.random())
            await ctx.reply(embed=embed)

        elif isinstance(error, commands.CommandOnCooldown):
            title = "Command on cooldown"
            dsc = f"`{ctx.command}` is on cooldown! Please try again after {error.retry_after} seconds!"
            embed = discord.Embed(title=title, description=dsc, color=discord.Color.random())
            await ctx.reply(embed=embed)

        elif isinstance(error, commands.MemberNotFound):
            title = "Member not found"
            dsc = f"I couldn't find member {error.argument} in this server!"
            embed = discord.Embed(title=title, description=dsc, color=discord.Color.random())
            await ctx.reply(embed=embed)

        elif isinstance(error, discord.errors.Forbidden):
            title = "I don't have the permissions"
            dsc = f"Are you sure i have administrator permissions?"
            embed = discord.Embed(title=title, description=dsc, color=discord.Color.random())
            await ctx.reply(embed=embed)

        elif isinstance(error, commands.MissingPermissions):
            title = "Missing Permissions"
            if len(error.missing_perms) == 1:
                perm = error.missing_perms[0]
                dsc = f"You are missing {perm} permission to run `{ctx.command}`"
                embed = discord.Embed(title=title, description=dsc, color=discord.Color.random())
                await ctx.reply(embed=embed)
            else:
                str_perms = ""
                for perm in error.missing_perms:
                    str_perms += f"{perm}, "
                    dsc = f"You are missing these permissions to run `{ctx.command}`: {str_perms}"
                    embed = discord.Embed(title=title, description=dsc, color=discord.Color.random())
                    await ctx.reply(embed=embed)
        elif isinstance(error, commands.BotMissingPermissions):
            title = "Missing Permissions"
            if len(error.missing_perms) == 1:
                perm = error.missing_perms[0]
                dsc = f"You are missing {perm} permission to run `{ctx.command}`"
                embed = discord.Embed(title=title, description=dsc, color=discord.Color.random())
                await ctx.reply(embed=embed)
            else:
                str_perms = ""
                for perm in error.missing_perms:
                    str_perms += f"{perm}, "
                    dsc = f"You are missing these permissions to run `{ctx.command}`: {str_perms}"
                    embed = discord.Embed(title=title, description=dsc, color=discord.Color.random())
                    await ctx.reply(embed=embed)

        else:
            title = "Unknown exception"
            stacktrace = traceback.format_tb(error.__traceback__)
            dsc = f"Sorry, the bot has run into an unknown Exception, it has been reported and is soon to be fixed!"
            embed = discord.Embed(title=title, description=dsc, color=discord.Color.random())
            await ctx.reply(embed=embed)
            dev_embed = discord.Embed(title = f"Unknown Exception found in command {ctx.command}", description = f"**Exception:**\n ```py\n{error}``` **Traceback:**\n ```py\n{stacktrace}```", color = discord.Color.from_rgb(0,255,255))
            embed.add_field(name = "Context Details", value = f"**Guild:** {ctx.guild.name if ctx.guild else None} ({ctx.guild.id if ctx.guild else 0})\n**Author:** {ctx.author}\n**Message:** {ctx.message.content} ({ctx.message.id}"
            ch = bot.get_channel(829970903503994920)
            await ch.send(embed = embed



def setup(bot):
    bot.add_cog(ErrorHandler(bot))
