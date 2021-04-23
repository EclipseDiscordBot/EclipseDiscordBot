import asyncpixel
import pickle
import matplotlib.pyplot as plt


async def calc_auc(hypixel: asyncpixel.Hypixel, currentAh: list) -> dict:
    # TODO Finish calc_auc in huge functions
    ahDict = {}
    binDict = {}
    for item in currentAh:
        if item.bin:
            try:
                if not binDict[item.item_name]:
                    binDict[item.item_name] = []
            except KeyError:
                binDict[item.item_name] = []
            binDict[item.item_name].append(item)
        else:
            try:
                if not ahDict[item.item_name]:
                    ahDict[item.item_name] = []
            except KeyError:
                ahDict[item.item_name] = []
            ahDict[item.item_name].append(item)

    listofnames = []
    for item in currentAh:
        listofnames.append(item.item_name)
    pickle.dump(listofnames, open('data/hypixelCog/ah_names.pkl', 'wb'))
    pickle.dump(ahDict, open('data/hypixelCog/ah_items.pkl', 'wb'))
    pickle.dump(binDict, open('data/hypixelCog/bin_items.pkl', 'wb'))
    return {"ahDict": ahDict, "binDict": binDict}
