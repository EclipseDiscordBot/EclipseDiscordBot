import asyncio

from discord import Embed
import discord
from discord.ext import commands
from classes import CustomBotClass, indev_check, context, ignore


class InviteTracker(commands.Cog):
    def __init__(self, bot: CustomBotClass.CustomBot):
        self.bot = bot
        ignore.ignore(ignore)
        ignore.ignore(discord)
        ignore.ignore(Embed)

    @commands.command("invitetracker", brief="track invites on your server", aliases=['it', 'trackinvites'])
    @indev_check.command_in_development()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def _invitetracker(self, ctx: context.Context, text_channel: discord.TextChannel):
        await ctx.reply("First of all, you should know. invites will only be counter with any invite links created AFTER this message is sent, this is due to discord API limitations")
        await asyncio.sleep(1)
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("UPDATE config SET invite_tracker_enable=$1,invite_tracker_channel=$2 WHERE server_id=$3", True, text_channel.id, ctx.guild.id)
        await ctx.reply(f"Ok invite tracker is now set up. any invites created after this point will have their invites counter and show in {text_channel.mention}")

    @commands.Cog.listener("on_invite_create")
    async def invite_created(self, invite: discord.Invite):
        row = await self.bot.pool.fetch("SELECT * FROM config WHERE server_id=$1", invite.guild.id)
        if not row[0]['invite_tracker_enable']:
            return
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("INSERT INTO invites(id,inviter,guild,uses) VALUES($1,$2,$3,$4)", invite.id, invite.inviter.id, invite.guild.id, 0)

    @commands.Cog.listener("on_invite_delete")
    async def invite_created(self, invite: discord.Invite):
        row = await self.bot.pool.fetch("SELECT * FROM config WHERE server_id=$1", invite.guild.id)
        if not row[0]['invite_tracker_enable']:
            return
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("DELETE FROM invites WHERE guild=$1", invite.guild.id)

    @commands.Cog.listener("on_member_join")
    async def user_join(self, member: discord.Member):
        row = await self.bot.pool.fetch("SELECT * FROM config WHERE server_id=$1", member.guild.id)
        if not row[0]['invite_tracker_enable']:
            return
        invites = await self.bot.pool.fetch("SELECT * FROM invites WHERE guild=$1", member.guild.id)
        new_invites = await member.guild.invites()
        parsed_invites = {}
        for invitee in new_invites:
            parsed_invites[invitee.id] = invitee
        for invitee in invites:
            try:
                parsed_invites[invitee['id']]
            except KeyError:
                return
            print(invitee)
            print(parsed_invites[invitee['id']])



def setup(bot):
    bot.add_cog(InviteTracker(bot))
