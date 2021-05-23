import discord
from discord.ext import commands
from classes import CustomBotClass, indev_check
from constants import emojis
import asyncio


class TicketingSystem(commands.Cog):
    def __init__(self, bot: CustomBotClass.CustomBot):
        self.bot = bot

    @commands.has_permissions(administrator=True)
    @commands.command(name="setup", brief="Set up ticketing system in your server")
    async def setup(self, ctx):
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        embed = discord.Embed(title="Ticketing Panel Setup", color=self.bot.color)
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        embed.set_footer(text="Type 'cancel' instead of input to cancel setup!")
        embed.description = "Alright! Now mention the channel where the 'panel' or where people should react to open a " \
                            "ticket must be"
        emb_msg = await ctx.send(embed=embed)
        try:
            ch_msg = await self.bot.wait_for('message', check=check, timeout=60)
        except asyncio.TimeoutError:
            embed.description = "You took too long to answer! Try the command again!"
            await emb_msg.edit(embed=embed)
            return
        if ch_msg.content.lower() == 'cancel':
            embed.description = "Cancelled!"
            await emb_msg.edit(embed=embed)
            return
        if not ch_msg.channel_mentions:
            embed.description = "Uh oh! You didn't mention a channel! Try the command again!"
            await emb_msg.edit(embed=embed)
            return
        panel_channel = ch_msg.channel_mentions[0]
        await ch_msg.delete()
        embed.add_field(name="Panel Channel", value=panel_channel.mention)
        embed.description = "Alright, I've set the panel channel. Now tell me what should be shown in the panel " \
                            "message embed description"
        await emb_msg.edit(embed=embed)
        try:
            panel_msg_content_msg = await self.bot.wait_for('message', check=check, timeout=60)
        except asyncio.TimeoutError:
            embed.description = "You took too long to answer! Try the command again!"
            await emb_msg.edit(embed=embed)
            return
        if panel_msg_content_msg.content.lower() == 'cancel':
            embed.description = "Cancelled!"
            await emb_msg.edit(embed=embed)
            return


def setup(bot: CustomBotClass.CustomBot):
    bot.add_cog(TicketingSystem(bot))
