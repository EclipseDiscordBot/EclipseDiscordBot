import random
from constants.economy import strid_to_id


async def banknote(db, uid):
    data = (await db.fetch("SELECT * FROM economy WHERE uid=$1", uid))[0]
    if strid_to_id.strid_id['banknote'] not in data['inventory']:
        return f"Hahahahahahahah you ain't having any {strid_to_id.strid_id['banknote']} in your inventory! "
    random_number = random.randint(10000, 30000)
    await db.execute("UPDATE economy SET bank_limit=bank_limit+$1 WHERE uid=$2", random_number, uid)
    await db.execute("UPDATE economy SET inventory=array_remove(inventory, $1) WHERE uid=$2", strid_to_id.strid_id['banknote'], uid)
    return f'You just used your {strid_to_id.strid_id["banknote"]} and got {random_number} of bank space'


consume_funcs = {
    "banknote": banknote
}
