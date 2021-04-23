import discord
from discord.ext import commands


class StatusRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def sr(self, ctx):
        # TODO
        #  @zapd0s add names and description to every command
        #  Also this file might have been broken by auto-pep8
        #  cogs/status_roles.py
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                role_id = await conn.fetchval("SELECT role_id FROM sr WHERE guild_id = $1", ctx.guild.id)
                key = await conn.fetchval("SELECT key FROM sr WHERE guild_id = $1", ctx.guild.id)
        role = ctx.guild.get_role(role_id)
        if role is None:
            txt = "Not setup yet"
        else:
            txt = role.mention
        if key == "placeholder":
            key = "Not setup yet"
        embed = discord.Embed(
            title="Status Roles",
            description=f"Status roles gives a role to a person if they have a certain keyword in their custom activity.\n **Here is {ctx.guild.name}'s configuration**",
            color=self.bot.color)
        embed.add_field(name="Role", value=txt)
        embed.add_field(name="Keyword", value=key)
        await ctx.send(embed=embed)

        @commands.command()
        @commands.has_permissions(administrator=True)
        @commands.guild_only()
        async def keyword(self, ctx, keyword1: str):
            async with self.bot.pool.acquire() as conn:
                async with conn.transaction():
                    await conn.execute("UPDATE sr SET keyword = $1 WHERE guild_id = $1", ctx.guild.id)
                    role_id = await conn.fetchval("SELECT role_id FROM sr WHERE guild_id = $1", ctx.guild.id)
                    role = ctx.guild.get_role(role_id)
                    if role is None:
                        txt = "Not setup yet"
                    else:
                        txt = role.mention
                    embed = discord.Embed(
                        title="Status Roles has been updated!",
                        description=f"Status roles gives a role to a person if they have a certain keyword in their custom activity.\n **Here is {ctx.guild.name}'s configuration**",
                        color=self.bot.color)
                    embed.add_field(name="Role", value=txt)
                    embed.add_field(name="Keyword", value=keyword1)
                    await ctx.send(embed=embed)

        @commands.command()
        @commands.guild_only()
        @commands.has_permissions(administrator=True)
        async def role(self, ctx, role_id):
            if isinstance(role_id, int):
                try:
                    role = ctx.guild.get_role(role_id)
                except Exception:
                    await ctx.send("That role doesn't exist!")
                    return
            elif isinstance(role_id, discord.Role):
                role = role_id
            else:
                await ctx.send("Please provide an ID or a role mention!")
                return
            async with self.bot.pool.acquire() as conn:
                async with conn.transaction():
                    await conn.execute("UPDATE sr SET role_id = $1 WHERE guild_id = $2", role.id, ctx.guild.id)
                    keyword = await conn.fetchval("SELECT key FROM sr WHERE guild_id = $1", ctx.guild.id)
            txt = role.mention
            embed = discord.Embed(
                title="Status Roles has been updated!",
                description=f"Status roles gives a role to a person if they have a certain keyword in their custom activity.\n **Here is {ctx.guild.name}'s configuration**",
                color=self.bot.color)
            embed.add_field(name="Role", value=txt)
            embed.add_field(name="Keyword", value=keyword)
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(StatusRoles(bot))
