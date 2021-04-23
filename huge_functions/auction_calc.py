import asyncpixel

async def calc_auc(hypixel: asyncpixel.Hypixel, currentAh: list) -> dict:
    # TODO Finish calc_auc in huge functions
    ahDict = {}
    binDict = {}
    counter = 0
    print(currentAh[0:5])
    for item in currentAh:
        if item.bin:
            binDict[f"{item.item_name}_{counter}"] = item
        else:
            ahDict[f"{item.item_name}_{counter}"] = item
        counter += 1
    print(f"Ah dict: {ahDict}.\n.\n.\n.\n.\nBin dict: {binDict}")
    return {'a': 'b'}
