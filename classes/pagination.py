import discord
import datetime
import asyncio

class EclipsePages:
    def __init__(self, embeds: list, timeout: int):
        self.embeds = embeds
        self.message = None
        self.current_page = 0
        self.ctx = None
        self.timeout = timeout
        self.emoji = {
            "stop": "⏹",
            "next": "⏩",
            "prev": "⏪",
            "first": "⏮",
            "last": "⏭"
        }

    def check(self, reaction, user):
        return reaction.message.id == self.message.id and user.id == self.ctx.author.id

    async def start(self, ctx):
        self.ctx = ctx
        self.message = await ctx.send(embed=self.embeds[0])
        await asyncio.sleep(1)
        for em in self.emoji.values():
            self.message.add_reaction(em)

        _start = datetime.datetime.now()
        _end = _start + datetime.timedelta(seconds=self.timeout)
        while True:
            now = datetime.datetime.now()
            if now >= _end:
                await self.message.clear_reactions()
                break
            reaction, user = await self.ctx.bot.wait_for('reaction_add', check=self.check,
                                                     timeout=(datetime.datetime.now() - _end).total_seconds())
            # remove reaction
            if str(reaction.emoji) in self.emoji.values():

                if str(reaction.emoji) == self.emoji["stop"]:
                    await self.message.delete()
                    break

                if str(reaction.emoji) == self.emoji["next"]:
                    await self.message.edit(embed=self.embeds[self.current_page+1])
                    self.current_page += 1

                if str(reaction.emoji) == self.emoji["prev"]:
                    await self.message.edit(embed=self.embeds[self.current_page-1])
                    self.current_page -= 1

                if str(reaction.emoji) == self.emoji["first"]:
                    await self.message.edit(embed=self.embeds[0])
                    self.current_page = 0

                if str(reaction.emoji) == self.emoji["last"]:
                    await self.message.edit(embed=self.embeds[-1])
                    self.current_page = -1
