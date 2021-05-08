from discord.ext import commands


class CogDisabledException(Exception):
    def __init__(self, cog_name):
        self.cog_name = cog_name
        super().__init__(self.cog_name)

    def __str__(self):
        return f'{self.cog_name} is not allowed to load according to the config'


def load_extension(bot: commands.Bot, cog: str, json: dict):
    if json['load_cogs']:
        try:
            if json['cogs'][cog]:
                bot.load_extension(cog)
            else:
                raise CogDisabledException(cog)
        except KeyError:
            raise CogDisabledException(cog)
