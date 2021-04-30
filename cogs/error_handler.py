import random
import string
import discord
import traceback
from discord.ext import commands
import datetime


class ErrorHandler(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        error_code = ''.join(
            random.choices(
                string.ascii_uppercase +
                string.digits,
                k=15))
        if hasattr(ctx.command, 'on_error'):
            return

        cog = ctx.cog
        if cog and cog._get_overridden_method(
                cog.cog_command_error) is not None:
            return

        ignored = (commands.CommandNotFound, commands.NotOwner)
        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return

        if isinstance(error, commands.DisabledCommand):
            title = "Disabled Command"
            dsc = f"`{ctx.command}` has been disabled by the developers. Please try later!"
            embed = discord.Embed(
                title=title,
                description=dsc,
                color=discord.Color.random())
            await ctx.reply(embed=embed)

        elif isinstance(error, commands.NoPrivateMessage):
            title = "Server Command"
            dsc = f"`{ctx.command}` can only be used in a server!"
            embed = discord.Embed(
                title=title,
                description=dsc,
                color=discord.Color.random())
            embed.add_field(
                name="Think its a bug and needs to be fixed very quick?",
                value=f"if that's the case, do `{ctx.prefix}emergency {error_code}`")
            await ctx.reply(embed=embed)

        elif isinstance(error, commands.UserInputError):
            title = "Input Error"
            dsc = "Oops! You've made a mistake while giving me input! Please correct it and try again!"
            embed = discord.Embed(
                title=title,
                description=dsc,
                color=discord.Color.random())
            await ctx.reply(embed=embed)

        elif isinstance(error, commands.CommandOnCooldown):
            title = "Command on cooldown"
            dsc = f"`{ctx.command}` is on cooldown! Please try again after {round(error.retry_after)} seconds!"
            embed = discord.Embed(
                title=title,
                description=dsc,
                color=discord.Color.random())
            await ctx.reply(embed=embed)

        elif isinstance(error, commands.MemberNotFound):
            title = "Member not found"
            dsc = f"I couldn't find member {error.argument} in this server!"
            embed = discord.Embed(
                title=title,
                description=dsc,
                color=discord.Color.random())
            embed.add_field(
                name="Think its a bug and needs to be fixed very quick?",
                value=f"if that's the case, do `{ctx.prefix}emergency {error_code}`")
            await ctx.reply(embed=embed)

        elif isinstance(error, discord.errors.Forbidden):
            title = "I don't have the permissions"
            dsc = "Are you sure i have administrator permissions?"
            embed = discord.Embed(
                title=title,
                description=dsc,
                color=discord.Color.random())
            embed.add_field(
                name="Think its a bug and needs to be fixed very quick?",
                value=f"if that's the case, do `{ctx.prefix}emergency {error_code}`")
            await ctx.reply(embed=embed)

        elif isinstance(error, commands.MissingPermissions):
            title = "Missing Permissions"
            if len(error.missing_perms) == 1:
                perm = error.missing_perms[0]
                dsc = f"You are missing {perm} permission to run `{ctx.command}`"
                embed = discord.Embed(
                    title=title,
                    description=dsc,
                    color=discord.Color.random())
                embed.add_field(
                    name="Think its a bug and needs to be fixed very quick?",
                    value=f"if that's the case, do `{ctx.prefix}emergency {error_code}`")
                await ctx.reply(embed=embed)
            else:
                str_perms = ""
                for perm in error.missing_perms:
                    str_perms += f"{perm}, "
                    dsc = f"You are missing these permissions to run `{ctx.command}`: {str_perms}"
                    embed = discord.Embed(
                        title=title, description=dsc, color=discord.Color.random())
                    embed.add_field(
                        name="Think its a bug and needs to be fixed very quick?",
                        value=f"if that's the case, do `{ctx.prefix}emergency {error_code}`")
                    await ctx.reply(embed=embed)
        elif isinstance(error, commands.BotMissingPermissions):
            title = "Missing Permissions"
            if len(error.missing_perms) == 1:
                perm = error.missing_perms[0]
                dsc = f"You are missing {perm} permission to run `{ctx.command}`"
                embed = discord.Embed(
                    title=title,
                    description=dsc,
                    color=discord.Color.random())
                embed.add_field(
                    name="Think its a bug and needs to be fixed very quick?",
                    value=f"if that's the case, do `{ctx.prefix}emergency {error_code}`")
                await ctx.reply(embed=embed)
            else:
                str_perms = ""
                for perm in error.missing_perms:
                    str_perms += f"{perm}, "
                    dsc = f"You are missing these permissions to run `{ctx.command}`: {str_perms}"
                    embed = discord.Embed(
                        title=title, description=dsc, color=discord.Color.random())
                    embed.add_field(
                        name="Think its needs to be fixed very quick?",
                        value=f"if that's the case, do `{ctx.prefix}emergency {error_code}`")
                    await ctx.reply(embed=embed)

        else:
            title = "Unknown exception"
            dsc = "Sorry, the bot has run into an unknown Exception, it has been reported and is soon to be fixed!"
            embed = discord.Embed(
                title=title,
                description=dsc,
                color=discord.Color.random())
            embed.add_field(
                name="Think its needs to be fixed very quick?",
                value=f"if that's the case, do `{ctx.prefix}emergency {error_code}`")
            await ctx.reply(embed=embed)

        stacktrace = traceback.format_tb(error.__traceback__)

        log_channel = self.bot.get_channel(830069392976773120)
        embed = discord.Embed(
            title=f"Unknown Exception caught in command {ctx.command}",
            description=f"Traceback: \n ```py\n{stacktrace[0]}```",
            color=discord.Color.from_rgb(
                255,
                0,
                0))
        embed.add_field(
            name="Context Details",
            value=f"Guild: {ctx.guild} ({ctx.guild.id if ctx.guild else None})\n User: {ctx.author} ({ctx.author.id})")
        embed.set_footer(text="Command invoked at:")
        embed.timestamp = datetime.datetime.now()
        embed.set_author(name=error)
        await log_channel.send(f"code: {error_code}", embed=embed)

    @commands.command(name="emergency",
                      aliases=["error"],
                      brief="Mark an error as an emergency to prioritize its fixing")
    @commands.cooldown(1, 86400, commands.BucketType.member)
    async def emergency(self, ctx, error_code):
        log_channel = self.bot.get_channel(830069392976773120)
        async for msg in log_channel.history(limit=50):
            if error_code in msg.content:
                await msg.reply(
                    f"hey <@605364556465963018> <@694839986763202580> {ctx.author} declares this as emergency! do something")
                break
        await ctx.message.reply("Alright, I've informed the devs about the emergency!")


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
