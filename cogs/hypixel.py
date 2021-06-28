import json
import sys
import aiohttp
import asyncpixel.exceptions.exceptions
import discord
from discord import Embed
import pickle

from classes.paginator import SpecialPaginator
from constants import bz_ids, emojis
from classes import CustomBotClass
from discord.ext import commands, tasks


class Hypixel(commands.Cog):
    def __init__(self, bot: CustomBotClass.CustomBot):
        self.bot = bot
        self.hypixel = asyncpixel.Hypixel(pickle.load(
            open("credentials.pkl", 'rb'))['hypixel'])
        self.currentBazaar = None
        self.currentAh = None
        self.AHDict = None
        self.bazaar_loop.start()
        # self.auction_loop.start()
        self.bz_id_item = bz_ids.id_name
        self.bz_item_id = bz_ids.name_id

    async def get_uuid(self, username):
        async with aiohttp.ClientSession() as sess:
            async with sess.get(f"https://api.mojang.com/users/profiles/minecraft/{username}") as res:
                if not res.status == 200:
                    return False
                json = await res.json()
                return json['id']


    @commands.command(name="key", aliases=["hypixel_key", "hypixel_api_key"],
                      brief="Gives information about a hypixel api key")
    async def key(self, ctx, key):
        key_data = await self.hypixel.key_data(key)
        owner_uuid = key_data.owner
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://api.mojang.com/user/profiles/{owner_uuid}/names') as response:
                json = await response.json()
                owner_name = json[-1]['name']
        limit = key_data.limit
        queries_in_past_min = key_data.queries_in_past_min
        total_queries = key_data.total_queries

        e = Embed(
            title="Here's some info about your API key",
            description="**PLEASE NOTE IF THIS ISNT YOUR API KEY DESTROY IT IMMEDIATELY AND INFORM THE OWNER**")
        e.add_field(name="Owner", value=owner_name, inline=False)
        e.add_field(
            name="Global limit (queries / 2 minutes)",
            value=str(limit),
            inline=False)
        e.add_field(name="No. of Queries in the past minute",
                    value=str(queries_in_past_min), inline=False)
        e.add_field(
            name="Total queries",
            value=str(total_queries),
            inline=False)

        await ctx.reply(embed=e)

    @commands.command(name="bazaar",
                      aliases=['bz'],
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

        e = Embed(
            title=final_item_name,
            description=f"Status of {final_item_name} in the past 30 seconds",
            color=discord.Color.random())
        e.add_field(
            name="Buy Price",
            value=str(
                round(
                    item_quick_status.buy_price)),
            inline=True)
        e.add_field(
            name="Sell Price",
            value=str(
                round(
                    item_quick_status.sell_price)),
            inline=True)
        e.add_field(
            name="Buy Orders",
            value=item_quick_status.buy_orders,
            inline=True)
        e.add_field(
            name="Sell Orders",
            value=item_quick_status.sell_orders,
            inline=True)

        await ctx.reply(embed=e)

    @tasks.loop(seconds=30)
    async def bazaar_loop(self):
        bz = await self.hypixel.bazaar()
        formattedbz = {}
        for item in bz.bazaar_items:
            formattedbz[item.product_id] = item

        self.currentBazaar = formattedbz

    @tasks.loop(hours=1)
    async def auction_loop(self):
        pages = []
        final_ah = []
        ah = await self.hypixel.auctions()
        print(f'Total pages: {ah.total_pages}')
        for page_no in range(ah.total_pages):
            for attempt in range(100):
                try:
                    page = await self.hypixel.auctions(page_no)
                except asyncpixel.exceptions.exceptions.ApiNoSuccess:
                    print(f"Attempt {attempt} Failed for page {page_no}")
                else:
                    break
            else:
                print("Failed getting page ", page_no)
                sys.exit(54)
            pages.append(page)
            print("appended page:", page_no)
            for page in pages:
                for auction in page.auctions:
                    final_ah.append(auction)

        self.currentAh = final_ah
        print("proccessed hypixel AH")
        # self.currentAh = pickle.load(open('data/test.pkl', 'rb')) # a sample AH
        # self.AHDict = await calc_auc(self.hypixel, self.currentAh, self.bot)

    @commands.command("stats", brief="Gets the hypixel stats of a person")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def _stats(self, ctx: commands.Context, uname: str=None):
        if uname is None:
            await ctx.reply("ey! You didn't provide a username! I'm not gonna accept empty usernames :unamused:")
            return
        ch: discord.TextChannel = ctx.channel
        async with ch.typing():
            uuid = await self.get_uuid(uname)
            if not uuid:
                await ctx.reply("Woah! that's a invalid username!")
                return
            all_stats = json.loads((await self.hypixel.player(uuid)).json())['raw']['player']
            random_color = discord.Color.random()
            # Bedwars
            bedwars_e = discord.Embed(title=f'Bedwars', colour=random_color)
            bedwars_e.add_field(name="Stars", value=all_stats['achievements']['bedwars_level'])
            bedwars_e.add_field(name="Wins", value=all_stats['achievements']['bedwars_wins'])
            bedwars_e.add_field(name="Total games played", value=all_stats['stats']['Bedwars']['games_played_bedwars'])
            bedwars_e.add_field(name="Win Streak", value=all_stats['stats']['Bedwars']['winstreak'])
            bedwars_e.add_field(name="Beds Broken", value=all_stats['achievements']['bedwars_beds'])
            bedwars_e.add_field(name="Deaths", value=all_stats['stats']['Bedwars']['deaths_bedwars'])
            bedwars_e.add_field(name="Coins", value=all_stats['stats']['Bedwars']['coins'])
            bedwars_e.add_field(name="Kills", value=all_stats['stats']['Bedwars']['kills_bedwars'])
            bedwars_e.add_field(name="Total Items purchased", value=all_stats['stats']['Bedwars']['items_purchased_bedwars'])
            # Skywars
            skywars_e = discord.Embed(title=f'Skywars', colour=random_color)
            skywars_e.add_field(name="Souls", value=all_stats['stats']['SkyWars']['souls'])
            skywars_e.add_field(name="Soul Well Level", value=all_stats['stats']['SkyWars']['soul_well'])
            skywars_e.add_field(name="Total games played", value=all_stats['stats']['SkyWars']['games_played_skywars'])
            skywars_e.add_field(name="Coins", value=all_stats['stats']['SkyWars']['coins'])
            skywars_e.add_field(name="Deaths", value=all_stats['stats']['SkyWars']['deaths'])
            skywars_e.add_field(name="Win Streak", value=all_stats['stats']['SkyWars']['win_streak'])
            skywars_e.add_field(name="Kills", value=all_stats['stats']['SkyWars']['kills'])
            skywars_e.add_field(name="Kill Streak", value=all_stats['stats']['SkyWars']['killstreak'])
            skywars_e.add_field(name="Wins", value=all_stats['stats']['SkyWars']['wins'])
            # Duels
            duels_e = discord.Embed(title=f'Duels', colour=random_color)
            duels_e.add_field(name="Coins", value=all_stats['stats']['Duels']['coins'])
            duels_e.add_field(name="Total Games Played", value=all_stats['stats']['Duels']['games_played_duels'])
            duels_e.add_field(name="Blocks placed", value=all_stats['stats']['Duels']['blocks_placed'])
            duels_e.add_field(name="Total damage dealt", value=all_stats['stats']['Duels']['damage_dealt'])
            duels_e.add_field(name="Wins", value=all_stats['stats']['Duels']['wins'])
            duels_e.add_field(name="Deaths", value=all_stats['stats']['Duels']['deaths'])
            duels_e.add_field(name="Total Bridge Goals", value=all_stats['stats']['Duels']['goals'])
            duels_e.add_field(name="Ping Preference", value=all_stats['stats']['Duels']['pingPreference'])
            # Skyblock
            skyblock_e = discord.Embed(title=f'Skyblock', colour=random_color)
            skyblock_e.add_field(name="Profile name(First profile)", value=list(all_stats['stats']['SkyBlock']['profiles'].values())[0]['cute_name'])
            prof_id =   list(all_stats['stats']['SkyBlock']['profiles'].values())[0]['profile_id']
            message = await ctx.reply(f"Fetching data {emojis.loading}")
            _paginator = SpecialPaginator(message, [bedwars_e, skywars_e, duels_e, skyblock_e])
            await message.edit(view=_paginator, embed=bedwars_e, content=f"Here are `{uname}`'s stats")


def setup(bot):
    bot.add_cog(Hypixel(bot))
