from constants.economy import basic as basic_eco
from constants import basic as basic


async def check_create_db(bot, ctx):
    row = await bot.pool.fetch("SELECT * FROM economy WHERE uid=$1", ctx.author.id)
    if not row:
        async with bot.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("INSERT INTO economy(uid,purse,bank,inventory,work,sus,passive) VALUES($1,$2,$3,$4,$5,$6,$7)", ctx.author.id, 0, 0, str({"legnth": 0}), 0, False, False)
        await ctx.author.send(basic_eco.first_interaction.format(user_mention=ctx.author.mention, prefix=ctx.prefix, bot_invite=basic.invite, support_server=basic.support_server))
