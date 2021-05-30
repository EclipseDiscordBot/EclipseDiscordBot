import constants.basic as basicC
from classes import CustomBotClass
from discord.ext import commands


class Basic(commands.Cog):
    def __init__(self, bot: CustomBotClass.CustomBot):
        self.bot = bot
        filee = open("constants/version.txt", 'r')
        self.version = filee.read()
        filee.close()

    @commands.command(name="ping",
                      aliases=['pong'],
                      brief='Gives the bot\'s latency')
    async def ping(self, ctx):
        """
        :returns bot's latency
        :param ctx:
        :return:
        """
        await ctx.reply(f"Pong! {round(self.bot.latency * 1000)} ms")

    @commands.command(name="version", brief="Gives the bot's version")
    async def _version(self, ctx):
        """
        :returns bot's version
        :param ctx:
        :return:
        """
        await ctx.reply(self.version)

    @commands.command(name="invite", brief="Gives the bot's invite link!")
    async def invite(self, ctx):
        """
        :returns bot's invite link
        :param ctx:
        :return:
        """
        await ctx.reply(f"{basicC.invite} ,I'll be waiting!")

    @commands.command(name="test", brief="Tests an aspect of the bot")
    @commands.is_owner()
    async def test(self, ctx, aspect: str):
        """
        Tests an aspect of the bot
        :param ctx:
        :param aspect:
        :return:
        """
        aspect = aspect.lower()
        if aspect == "error" or aspect == "exception":
            await ctx.reply("ok, testing!")
            raise Exception("TESTTTTTTT")

    @commands.command(name="servers",
                      aliases=["servercount"],
                      brief="Tells how many servers the bot is in")
    @commands.is_owner()
    async def servers(self, ctx):
        """
        :returns The number of guilds the bot is in
        :param ctx:
        :return:
        """
        await ctx.send(f"I am in {len(self.bot.guilds)} servers")

    @commands.command("source", aliases=['src', 'license'])
    async def _source(self, ctx):
        """
        :returns The bot's source code, and its license
        :param ctx:
        :return:
        """

        await ctx.reply("""
Eclipse is licensed under GPL 3: https://github.com/EclipseDiscordBot/EclipseDiscordBot/blob/master/LICENSE
**To sum it up**:
```diff
+Commercial use
+Modification
+Distribution
+Patent use
+Private use
-Liability
-Warranty
```
Also you **MUST** Follow these with whatever you do with the source:
```
License and copyright notice
State changes
Disclose source
Same license
```

You are legally bound to do the above. if not, you are violating a license, which is illegal

Source: https://github.com/EclipseDiscordBot/EclipseDiscordBot/
        """)


def setup(bot):
    bot.add_cog(Basic(bot))
