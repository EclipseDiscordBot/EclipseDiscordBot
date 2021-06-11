from discord.ext import commands
from classes import CustomBotClass, indev_check


class EconomyBasic(commands.Cog):
    def __init__(self, bot: CustomBotClass.CustomBot):
        """

        The Economy cog

        database table:

         uid | purse | bank | inventory | work | sus
        -----+-------+------+-----------+------+-----


        :param bot:
        """
        self.bot = bot




def setup(bot):
    bot.add_cog(EconomyBasic(bot))
