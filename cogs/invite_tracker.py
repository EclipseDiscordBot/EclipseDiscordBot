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
    async def invite_created(self, invite):
        row = await self.bot.pool.fetch("SELECT * FROM config WHERE server_id=$1", invite.guild.id)
        if not row[0]['invite_tracker_enable']:
            return
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("INSERT INTO invites(id,inviter,guild,uses) VALUES($1,$2,$3,$4)", invite.code, invite.inviter.id, invite.guild.id, 0)
                rows = await conn.fetch("SELECT * FROM invite_stats WHERE guild=$1", invite.guild.id)
                final_list = []
                for row in rows:
                    final_list.append(row['user_id'])
                if invite.inviter.id not in final_list:
                    await conn.execute("INSERT INTO invite_stats(guild,user_id,count) VALUES($1,$2,$3)", invite.guild.id, invite.inviter.id, 0)

    @commands.Cog.listener("on_invite_delete")
    async def invite_deleted(self, invite: discord.Invite):
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
        parsed_new_invites = {}
        for invite in new_invites:
            parsed_new_invites[invite.code] = invite
        for invite in invites:
            updated_invite = parsed_new_invites[invite['id']]
            if updated_invite.uses > invite['uses']:
                async with self.bot.pool.acquire() as conn:
                    async with conn.transaction():
                        await conn.execute("UPDATE invites SET uses = $1 WHERE id = $2", updated_invite.uses, invite['id'])
                        await conn.execute("UPDATE invite_stats SET count=$1 WHERE guild=$2 AND user_id=$3", updated_invite.uses, member.guild.id, updated_invite.inviter.id)
                        user_invites = await conn.fetch("SELECT * FROM invite_stats WHERE guild=$1 AND user_id=$2", member.guild.id, updated_invite.inviter.id)
                        user_invites = user_invites[0]
                        user_invites_count = user_invites['count']
                        channel_id = row[0]['invite_tracker_channel']
                        channel = member.guild.get_channel(channel_id)
                        await channel.send(f"`{member.display_name}` Joined! Invited by `{updated_invite.inviter.display_name}`, who now has {user_invites_count} invites!")



def setup(bot):
    bot.add_cog(InviteTracker(bot))
