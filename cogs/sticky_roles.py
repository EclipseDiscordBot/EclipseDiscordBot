import discord
from discord.ext import commands
import typing


class StickyRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_sr_details(self, ctx):
        embed = discord.Embed(title="Sticky Roles",
                              description="**Sticky roles** are roles which can be configured to be added when a user"
                                          " with the role leaves the server and rejoins.",
                              color=self.bot.color)
        res = await self.bot.pool.fetch("SELECT * FROM stickyroles WHERE guild_id = $1", ctx.guild.id)
        # CREATE TABLE stickyroles (guild_id BIGINT, role_id BIGINT, index BIGINT, enabled TEXT)
        for row in res:
            try:
                role_name = (ctx.guild.get_role(row["role_id"])).name
            except Exception:
                role_name = "Unknown Role"
            enabled = "🟢 Yes" if (row["enabled"] == "True") else "🔴 No"
            embed.add_field(name=role_name, value=f"**ID:** {row['index']}\n**Enabled:** {enabled}")
        await ctx.send(embed=embed)

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(manage_roles=True)
    async def _stickyroles(self, ctx):
        await send_sr_details(ctx)

    @_stickyroles.command(name="add", brief="Add a sticky role")
    async def add(self, ctx, role: discord.Role):
        if role.position > self.bot.top_role.position:
            await ctx.send(f"{role.name} is higher than my top role, {self.bot.top_role.position.name}. "
                           f"I cannot add it to anyone!")
            return
        res = await self.bot.pool.fetch("SELECT * FROM stickyroles WHERE guild_id=$1", ctx.guild.id)
        if len(res) == 10:
            await ctx.send("Cannot have more than 10 sticky roles!")
            return
        for row in res:
            if role.id == row["role_id"]:
                await ctx.send(f"{role.name} is already configured to be a sticky role!")
                return

        index = len(res) + 1
        await self.bot.pool.execute("INSERT INTO stickyroles (guild_id, role_id, index, enabled) VALUES ($1,$2,$3,$4)",
                                    ctx.guild.id, role.id, index, "True")
        await send_sr_details(ctx)

    @_stickyroles.command(name="remove", brief="Remove a sticky role")
    @commands.has_permissions(manage_roles=True)
    async def remove(self, ctx, index: int):
        res = await self.bot.pool.fetch("SELECT * FROM stickyroles WHERE guild_id=$1", ctx.guild.id)
        try:
            role = res[index - 1]
        except IndexError:
            await ctx.send(f"There wasn't a sticky role with that ID! "
                           f"do `{ctx.prefix}stickyroles` to see the index of all configured roles")
            return
        await self.bot.pool.execute("DELETE FROM stickyroles WHERE role_id=$1", role["role_id"])
        await send_sr_details(ctx)

    @_stickyroles.command(name="enable", brief="Enables a sticky role which is already configured")
    @commands.has_permissions(manage_roles=True)
    async def enable(self, ctx, index):
        res = await self.bot.pool.fetch("SELECT * FROM stickyroles WHERE guild_id=$1", ctx.guild.id)
        try:
            role = res[index - 1]
        except IndexError:
            await ctx.send(f"There wasn't a sticky role with that ID! "
                           f"do `{ctx.prefix}stickyroles` to see the index of all configured roles")
        else:
            await self.bot.pool.execute("UPDATE stickyroles SET enabled=$1 WHERE role_id=$1", "True", role.id)
            await send_sr_details(ctx)

    @_stickyroles.command(name="disable", brief="Disables a sticky role which is already configured")
    @commands.has_permissions(manage_roles=True)
    async def disable(self, ctx, index):
        res = await self.bot.pool.fetch("SELECT * FROM stickyroles WHERE guild_id=$1", ctx.guild.id)
        try:
            role = res[index - 1]
        except IndexError:
            await ctx.send(f"There wasn't a sticky role with that index! "
                           f"do `{ctx.prefix}stickyroles` to see the index of all configured roles")
        else:
            await self.bot.pool.execute("UPDATE stickyroles SET enabled=$1 WHERE role_id=$1", "False", role.id)
            await send_sr_details(ctx)


    @commands.Cog.listener("on_member_leave")
    async def add_to_db(self, member:discord.Member):
        res = await self.bot.pool.fetch("SELECT * FROM stickyroles WHERE (guild_id=$1 AND enabled=$2)", member.guild.id,
                                        "True")
        if not res:
            return

        else:
            for row in res:
                # CREATE TABLE stickyroleslog (member_id BIGINT, role_id BIGINT)
                await self.bot.pool.execute("INSERT INTO stickyroleslog (guild_id, member_id, role_id) VALUES ($1, $2)",
                                            member.guild.id, member.id, row["role_id"])

    @commands.Cog.listener("on_member_join")
    async def remove_from_db(self, member:discord.Member):
        to_be_added = await self.bot.pool.fetch("SELECT * FROM stickyroleslog WHERE (member_id=$1 AND guild_id=$2)",
                                                member.id, member.guild.id)
        for row in to_be_added:
            try:
                role = member.guild.get_role(int(row["role_id"]))
            except Exception:
                continue
            else:
                await member.add_roles(role)
            await self.bot.pool.execute("DELETE FROM stickyroleslog WHERE (member_id=$1 AND role_id=$2)",
                                        member.id, role.id)





def setup(bot):
    bot.add_cog(StickyRoles(bot))

