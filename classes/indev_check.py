from discord.ext import commands
from constants.basic import owners, beta_testers
from discord.ext import commands
import discord.ext


class CommandInDevException(discord.ext.commands.CheckFailure):
    def __init__(self, command_name):
        self.command_name = command_name
        super().__init__(command_name)

    def __str__(self):
        return f'The command `{self.command_name}` is still in development! please check back again later. if this is a mistake DM <@605364556465963018>'


def command_in_development():
    async def predicate(ctx: commands.Context):
        if ctx.author.id in owners:
            return True
        elif ctx.author.id in beta_testers:
            await ctx.reply("hey! this command is still in development! report any bugs you find and leave feedback in <@605364556465963018>'s DMs")
            return True
        else:
            raise CommandInDevException(ctx.command.name)

    return commands.check(predicate)
