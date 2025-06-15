from discord.ext import commands
import discord

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason"):
        await member.kick(reason=reason)
        await ctx.send(f"👢 Đã kick {member.mention} because: {reason}")

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason"):
        await member.ban(reason=reason)
        await ctx.send(f"🔨 Banned {member.mention} because: {reason}")

    @commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member_name):
        banned_users = []
        async for entry in ctx.guild.bans():
            banned_users.append(entry)

        for ban_entry in banned_users:
            user = ban_entry.user
            if member_name.lower() in f"{user.name}#{user.discriminator}".lower():
                await ctx.guild.unban(user)
                await ctx.send(f"✅ Unban {user.mention}")
                return

        await ctx.send("❌ No banned users found.")


async def setup(bot):
    await bot.add_cog(Moderation(bot))
