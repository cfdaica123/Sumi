from discord.ext import commands
import random

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="coinflip")
    async def coinflip(self, ctx):
        result = random.choice(["🪙 Heads!", "🪙 Tails"])
        await ctx.send(f"{ctx.author.mention} Coin toss... {result}")

    @commands.command(name="say")
    async def say(self, ctx, *, message: str):
        await ctx.send(f"📣 {ctx.author.display_name} nói: {message}")

async def setup(bot):
    await bot.add_cog(Fun(bot))
