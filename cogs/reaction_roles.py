from discord.ext import commands
import discord
from classes import CustomBotClass
import asyncio


class ReactionRoles(commands.Cog):

    def __init__(self, bot: CustomBotClass.CustomBot):
        self.bot = bot
        self.pool = bot.pool

        # server_id int, msg_id int, reaction text, role_id int

    @commands.command(name="reactionroles", aliases=['rr', 'reaction'])
    @commands.has_permissions(manage_guild=True)
    async def rr(self, ctx: commands.Context, subcommand: str, argv1: str, argv2: discord.Role):
        def check(u):
            return u.author == ctx.author

        subcommand = subcommand.lower()
        if subcommand == "add":
            await ctx.reply("Aight, so send me the message ID to react on!")
            try:
                msg: discord.Message = await self.bot.wait_for('message', check=check, timeout=50)
            except asyncio.TimeoutError:
                await ctx.reply("time's up mate!")
                return
            else:
                try:
                    int(msg.content)
                except ValueError:
                    await ctx.reply("oops! that isn't a valid id bro!")
                    return
                await ctx.reply("mention the channel that message is located in")
                try:
                    chnl: discord.Message = await self.bot.wait_for('message', check=check, timeout=50)
                except asyncio.TimeoutError:
                    await ctx.reply("time's up mate!")
                    return
                else:
                    try:
                        channel: discord.TextChannel = await commands.TextChannelConverter().convert(ctx, str(chnl.content))
                    except commands.ChannelNotFound:
                        await ctx.reply("Nope! Not a valid channel")
                        return
                    try:
                        react_msg = await channel.fetch_message(msg.content)
                    except Exception:
                        await ctx.reply("Message doesn't exist boi!")
                        return

                    async with self.pool.acquire() as conn:
                        async with conn.transaction():
                            gid = int(ctx.guild.id)
                            mid = int(msg.content)
                            rid = int(argv2.id)
                            await conn.execute(
                                "INSERT INTO reaction_roles(server_id,msg_id,reaction,role_id) VALUES($1, $2, $3, $4)",
                                gid, mid, argv1, rid)
                    await react_msg.add_reaction(argv1)
                    await ctx.reply("Reaction Role added!")
        if subcommand == "remove":
            await ctx.reply("Aight, so send me the message ID of the RR")
            try:
                msg: discord.Message = await self.bot.wait_for('message', check=check, timeout=50)
            except asyncio.TimeoutError:
                await ctx.reply("time's up mate!")
                return
            else:
                try:
                    int(msg.content)
                except ValueError:
                    await ctx.reply("oops! that isn't a valid id bro!")
                    return
                await ctx.reply("mention the channel that message is located in")
                try:
                    chnl: discord.Message = await self.bot.wait_for('message', check=check, timeout=50)
                except asyncio.TimeoutError:
                    await ctx.reply("time's up mate!")
                    return
                else:
                    try:
                        channel: discord.TextChannel = await commands.TextChannelConverter().convert(ctx, str(chnl.content))
                    except commands.ChannelNotFound:
                        await ctx.reply("Nope! Not a valid channel")
                        return
                    try:
                        react_msg = await channel.fetch_message(msg.content)
                    except Exception:
                        await ctx.reply("Message doesn't exist boi!")
                        return

                    async with self.pool.acquire() as conn:
                        async with conn.transaction():
                            mid = int(msg.content)
                            rid = int(argv2.id)
                            await conn.execute(
                                "DELETE FROM reaction_roles WHERE role_id = $1 AND msg_id = $2",
                                rid, mid)
                    await react_msg.remove_reaction(argv1, self.bot.user)
                    await ctx.reply("Reaction Role Removed!")

    @commands.Cog.listener('on_raw_reaction_add')
    async def reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.member == self.bot.user:
            return
        async with self.pool.acquire():
            async with self.bot.pool.acquire() as conn:
                async with conn.transaction():
                    res = await conn.fetch("SELECT * FROM reaction_roles")
            for row in res:
                emoji_check = (str(payload.emoji) == row['reaction'])
                msg_check = (row['msg_id'] == payload.message_id)
                server_check = (row['server_id'] == payload.guild_id)
                if server_check and msg_check and emoji_check:
                    role: discord.Role = self.bot.get_guild(
                        payload.guild_id).get_role(row['role_id'])
                    member: discord.Member = payload.member
                    try:
                        await member.add_roles(role, reason=f"Self-Role. MSG_ID:{row['msg_id']}")
                    except discord.errors.Forbidden:
                        return
                    try:
                        await member.send(f"Gave you the `{role.name}` Role in `{self.bot.get_guild(payload.guild_id).name}`")
                    except discord.Forbidden:
                        pass

    @commands.Cog.listener('on_raw_reaction_remove')
    async def reaction_remove(self, payload: discord.RawReactionActionEvent):
        if payload.member == self.bot.user:
            return
        async with self.pool.acquire():
            async with self.bot.pool.acquire() as conn:
                async with conn.transaction():
                    res = await conn.fetch("SELECT * FROM reaction_roles")
            for row in res:
                emoji_check = (str(payload.emoji) == row['reaction'])
                msg_check = (row['msg_id'] == payload.message_id)
                server_check = (row['server_id'] == payload.guild_id)
                if server_check and msg_check and emoji_check:
                    role: discord.Role = self.bot.get_guild(
                        payload.guild_id).get_role(row['role_id'])
                    member: discord.Member = self.bot.get_guild(
                        payload.guild_id).get_member(payload.user_id)
                    await member.remove_roles(role, reason=f"Self-Role. MSG_ID:{row['msg_id']}")
                    try:
                        await member.send(
                            f"Removed your `{role.name}` role in `{self.bot.get_guild(payload.guild_id).name}`")
                    except discord.Forbidden:
                        pass


def setup(bot):
    bot.add_cog(ReactionRoles(bot))
