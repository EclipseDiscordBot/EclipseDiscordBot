import json
import os
import discord
from classes import CustomBotClass, proccessname_setter, testexception, check_create_db_entries
import pickle
from discord.ext import commands
from constants.basic import owners
from classes.LoadCog import CogDisabledException


class OwnerOnlyCommands(commands.Cog, name="DeveloperCommands"):
    def __init__(self, bot: CustomBotClass.CustomBot):
        self.bot = bot

    def cog_check(self, ctx):
        """
        So that only owners can use any command from this cog
        :param ctx:
        :return:
        """
        return ctx.author.id in owners

    @commands.command(hidden=True,
                      brief="Repeatedly sends the mentioned user's mention",
                      name="spamping")
    @commands.is_owner()
    async def spamping(self, ctx: discord.ext.commands.Context, times: int, member: discord.Member):
        """
        Repeatedly mentions the mentioned user
        :param ctx:
        :param times: the number of times to repeat
        :param member: the member whose mention will be repeated
        :return:
        """
        if member.id not in owners:
            await ctx.reply("It's mean to spam ping anyone that's not a dev :P")
            return

        for i in range(times):
            await ctx.reply(f"{member.mention} {i}")

    @commands.command(hidden=True, name="disablecog", brief="Disables a cog")
    @commands.is_owner()
    async def _disable(self, ctx, cog: str):
        """
        Disables a cog so it doesn't automatically load on startup
        :param ctx:
        :param cog: the cog file path
        :return:
        """
        self.bot.config['cogs'][cog] = False
        with open('config/config.json', 'w') as file:
            json.dump(self.bot.config, file, sort_keys=True,
                      indent=2, separators=(',', ': '))
            file.flush()
        await ctx.reply(f"{cog} has been disabled until re-enabled! Rebooting!")
        await self.restart(ctx)

    @commands.command(hidden=True, name="enablecog", brief="Enables a cog")
    @commands.is_owner()
    async def _enable(self, ctx, cog: str):
        """
        Enables a cog so that it automatically loads on startup
        :param ctx:
        :param cog:
        :return:
        """
        self.bot.config['cogs'][cog] = True
        with open('config/config.json', 'w') as file:
            json.dump(self.bot.config, file, sort_keys=True,
                      indent=2, separators=(',', ': '))
            file.flush()
        await ctx.reply(f"{cog} has been enabled! Rebooting!")
        await self.restart(ctx)

    @commands.command(name="restart", brief="Restarts the bot", hidden=True)
    @commands.is_owner()
    async def restart(self, ctx):
        """
        Restarts the bot
        Fun Fact: this is the most used command
        :param ctx:
        :return:
        """
        await ctx.reply("Restarting...")

        def reload_extension(bot: commands.Bot, cog: str, json: dict):
            """
            Loads a cog after checking if it is allowed to be loaded in config.json
            :param bot:
            :param cog:
            :param json:
            :return:
            """
            if json['load_cogs']:
                try:
                    if json['cogs'][cog]:
                        try:
                            bot.reload_extension(cog)
                        except Exception:
                            bot.load_extension(cog)
                    else:
                        raise CogDisabledException(cog)
                except KeyError:
                    raise CogDisabledException(cog)

        os.system(
            "git pull 'https://github.com/EclipseDiscordBot/EclipseDiscordBot.git' --allow-unrelated-histories")
        exceptions = ""
        counter = 0
        failed_counter = 0
        with open("config/config.json", "r") as read_file:
            data = json.load(read_file)
            self.bot.config = data
        for file in os.listdir("./cogs"):
            if file.endswith('.py'):
                try:
                    reload_extension(
                        self.bot, f'cogs.{file[:-3]}', self.bot.config)
                    counter += 1
                    print(f"loaded cogs.{file[:-3]}")
                except Exception as e:
                    if isinstance(e, CogDisabledException):
                        failed_counter += 1
                    else:
                        exceptions += f"- Error while loading {file} [{e}]\n"
        f_exceptions = f"+ {counter} cogs loaded successfully\n" \
                       f"- {failed_counter} cogs were not loaded due to config\n{exceptions} "
        embed = discord.Embed(
            title="Restarted",
            description=f"```diff\n{f_exceptions}```",
            color=self.bot.color)
        await ctx.send(embed=embed)

    @commands.command(hidden=True, name="updatesra",
                      aliases=["sra"], brief="Updates SRA key")
    @commands.is_owner()
    @commands.dm_only()
    async def updatesra(self, ctx, key: str):
        """
        The two facts that lead to this command:
            - SRA keys expire every 5 days or so
            - Developers are lazy
        :param ctx:
        :param key: the key to replace it with
        :return:
        """
        prev_credd = pickle.load(open('credentials.pkl', 'rb'))
        prev_credd['some_random_api'] = key
        pickle.dump(prev_credd, open('credentials.pkl', 'wb'))
        await ctx.reply("Done! rebooting!")
        await self.restart(ctx)

    @commands.Cog.listener('on_message')
    async def check_for_token(self, message: discord.Message):
        """
        Worst case scenario management
        :param message:
        :return:
        """
        if self.bot.token in message.content:
            try:
                await message.delete()
            except Exception:
                pass
            for id in owners:
                dev = self.bot.get_user(int(id))
                await dev.send(
                    f"PANIK! token has been leaked! in `{message.guild.name}` by `{message.author}`! but "
                    f"Regen it to be safe")

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
            raise testexception.TestException("TESTTTTTTT")

    @commands.Cog.listener("on_command")
    async def command_listener(self, ctx):
        await check_create_db_entries.check_create_db(self.bot, ctx.author)

    @commands.command("cleanup")
    @commands.is_owner()
    async def cleanup_command(self, ctx, amt: int = 20):
        await ctx.message.delete()

        def check(m):
            return (m.author == ctx.author) or (m.author == self.bot.user)

        msgs = await ctx.channel.purge(limit=amt, check=check)
        await ctx.send(f"Cleaned up {len(msgs)} messages.", delete_after=5)


def setup(bot):
    bot.add_cog(OwnerOnlyCommands(bot))
