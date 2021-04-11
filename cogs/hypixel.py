import aiohttp
import discord
from discord import Embed
import asyncpixel
import pickle
from constants import bz_ids
from huge_functions.auction_calc import *
from discord.ext import commands, tasks


class Hypixel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hypixel = asyncpixel.Hypixel(pickle.load(open("credentials.pkl", 'rb'))['hypixel'])
        self.currentBazaar = None
        self.currentAh = None
        self.AHDict = None
        self.bazaar_loop.start()
        self.bz_id_item = bz_ids.id_name
        self.bz_item_id = bz_ids.name_id

    @commands.command(name="key", aliases=["hypixel_key", "hypixel_api_key"],
                      brief="Gives information about a hypixel api key")
    async def key(self, ctx, key):
        key_data = await self.hypixel.key_data(key)
        owner_uuid = key_data.owner
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://api.mojang.com/user/profiles/{owner_uuid}/names') as response:
                json = await response.json()
                owner_name = json[len(json) - 1]["name"]
        limit = key_data.limit
        queries_in_past_min = key_data.queries_in_past_min
        total_queries = key_data.total_queries

        e = Embed(title="Here's some info about your API key",
                  description="**PLEASE NOTE IF THIS ISNT YOUR API KEY DESTROY IT IMMEDIATELY AND INFORM THE OWNER**")
        e.add_field(name="Owner", value=owner_name, inline=False)
        e.add_field(name="Global limit (queries / 2 minutes)", value=str(limit), inline=False)
        e.add_field(name="No. of Queries in the past minute", value=str(queries_in_past_min), inline=False)
        e.add_field(name="Total queries", value=str(total_queries), inline=False)

        await ctx.reply(embed=e)

    @commands.command(name="bazaar", aliases=['bz'],
                      brief="Gives information about a product in the Hypixel Skyblock bazaar")
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

    @tasks.loop(seconds=30)
    async def bazaar_loop(self):
        bz = await self.hypixel.bazaar()
        formattedbz = {}
        for item in bz.bazaar_items:
            formattedbz[item.product_id] = item

        self.currentBazaar = formattedbz

    @tasks.loop(minutes=15)
    async def auction_loop(self):
        pages = []
        final_ah = []
        ah = await self.hypixel.auctions()
        for page_no in range(ah.total_pages):
            page = await self.hypixel.auctions(page_no)
            pages.append(page)
        for page in pages:
            for auction in page:
                final_ah.append(auction)

        self.currentAh = final_ah
        self.AHDict = await calc_auc(self.hypixel, self.currentAh)


def setup(bot):
    bot.add_cog(Hypixel(bot))
