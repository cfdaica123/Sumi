import discord
from discord.ext import commands
import json

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        welcome_channel = discord.utils.get(member.guild.text_channels, name="welcome")
        if welcome_channel:
            await welcome_channel.send(f"🎉 Welcome {member.mention} come to server {member.guild.name}!")

        role = discord.utils.get(member.guild.roles, name="Member")
        if role:
            await member.add_roles(role)
            print(f"✅ Added role {role.name} cho {member.name}")

async def setup(bot):
    await bot.add_cog(Welcome(bot))
