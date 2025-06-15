from discord.ext import commands

class AIChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping")
    async def ping(self, ctx):
        await ctx.send("🏓 Pong! I'm still alive, Boss, don't worry.~")

    @commands.command(name="chat")
    async def chat(self, ctx, *, message: str):
        response = f"🤖 I heard Boss said: '{message}'. But I wasn't taught how to respond wisely... coming soon!"
        await ctx.send(response)

async def setup(bot):
    await bot.add_cog(AIChat(bot))
