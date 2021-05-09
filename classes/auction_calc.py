from classes.deprecated import deprecated
import asyncpixel
from matplotlib import pyplot as plt
from classes import CustomBotClass, ignore
from typing import List, Dict


@deprecated
def stage_1(input_list: List[str]):
    for item in input_list:
        condition = item.isascii()
        if not condition:
            input_list.pop(input_list.index(item))
    return input_list


async def calculate_and_graph(items: Dict[str, List[asyncpixel.models.AuctionItem]]):
    """
    SHOULD BE CALLED FOR EVERY ITEM!
    :param items:
    :return:
    """
    
    BIN = items['bin']
    auctions = items['ah']

    bin_prices = []
    bin_times = []
    auc_prices = []
    auc_times = []
    for item in BIN:
        bin_prices.append(item.starting_bid)
        bin_times.append(item.start.strftime("%Y-%m-%d %H:%M:%S"))
    for item in auctions:
        auc_prices.append(item.highest_bid_amount)
        auc_times.append(item.start.strftime("%Y-%m-%d %H:%M:%S"))

    avg_bin_price = sum(bin_prices) / len(bin_prices)

    ignore.ignore(avg_bin_price)

    plt.plot(bin_prices, bin_times)
    plt.plot(auc_prices, auc_times)
    plt.title(BIN[0].item_name.lower())
    plt.legend(["Bin", "Auctions"])
    plt.savefig(f'data/hypixel/auctions/{BIN[0].item_name.lower()}.png')


async def calc_auc(hypixel: asyncpixel.Hypixel, currentAh: List[asyncpixel.models.AuctionItem],
                   bot: CustomBotClass.CustomBot) -> dict:
    ahDict = {}
    binDict = {}
    for item in currentAh:
        if item.bin:
            try:
                if not binDict[item.item_name.lower()]:
                    binDict[item.item_name.lower()] = []
            except KeyError:
                binDict[item.item_name.lower()] = []
            binDict[item.item_name.lower()].append(item)
        else:
            try:
                if not ahDict[item.item_name.lower()]:
                    ahDict[item.item_name.lower()] = []
            except KeyError:
                ahDict[item.item_name.lower()] = []
            ahDict[item.item_name.lower()].append(item)

    listofnames = []
    async with bot.pool.acquire() as conn:
        async with conn.transaction():
            for item in currentAh:
                if item.item_name.isascii():
                    if not item.item_name.lower() in listofnames:
                        listofnames.append(item.item_name.lower())
                    await conn.execute(
                        "INSERT INTO hypixel_items(item,price,bin,timestamp,auction_uuid,auctioneer_uuid,auctioneer_profile_id) VALUES($1,$2,$3,$4,$5,$6,$7)",
                        item.item_name.lower(), (item.starting_bid if item.bin else item.highest_bid_amount), item.bin,
                        item.end.timestamp(), str(item.uuid), str(item.auctioneer), str(item.profile_id))
                    print(f"proccessed auction {item.uuid}")
    for item in listofnames:
        try:
            await calculate_and_graph({
                "bin": binDict[item.lower()],
                "ah": ahDict[item.lower()]
            })
        except KeyError:
            pass

    return {"ahDict": ahDict, "binDict": binDict}
