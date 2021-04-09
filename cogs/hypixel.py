import discord
from discord import Embed
import asyncpixel
import pickle
from constants import bz_ids
from discord.ext import commands


class Hypixel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hypixel = asyncpixel.Hypixel(pickle.load(open("credentials.pkl", 'rb'))['hypixel'])
        self.currentBazaar = None
        self.currentAh = None
        self.Bazaar_Loop.start()
        self.bz_id_item = bz_ids.id_name
        self.bz_item_id = bz_ids.name_id

    @commands.command(name="bazaar", aliases=['bz'], brief="Gives information about a product in the Hypixel Skyblock bazaar")
    async def bazaar(self, ctx, *, itemId=None):
        final_item_id = ""
        final_item_name = ""
        if itemId in self.bz_id_item.keys():
            final_item_id = itemId
            final_item_name = self.bz_id_item[itemId]
        elif itemId.lower() in self.bz_item_id.keys():
            final_item_id = self.bz_item_id[itemId.lower()]
            final_item_name = self.bz_id_item[final_item_id]

        if final_item_name == "" or final_item_id == "":
            await ctx.reply("Sorry, that item isn't in bazaar! please check and try again!")
            return

        item_quick_status = self.currentBazaar[final_item_id].quick_status

        e = Embed(title=final_item_name, description=f"Status of {final_item_name} in the past 30 seconds",
                  color=discord.Color.random())
        e.add_field(name="Buy Price", value=str(round(item_quick_status.buy_price)), inline=True)
        e.add_field(name="Sell Price", value=str(round(item_quick_status.sell_price)), inline=True)
        e.add_field(name="Buy Orders", value=item_quick_status.buy_orders, inline=True)
        e.add_field(name="Sell Orders", value=item_quick_status.sell_orders, inline=True)

        await ctx.reply(embed=e)

def setup(bot):
    bot.add_cog(Hypixel(bot))
