import os
import json
from discord.ext import commands

LEVEL_FILE = "level_data.json"

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.levels = self.load_levels()

    def load_levels(self):
        if not os.path.isfile(LEVEL_FILE):
            with open(LEVEL_FILE, "w") as f:
                json.dump({}, f)
            return {}
        try:
            with open(LEVEL_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("⚠️ level_data.json broken, rebuild.")
            with open(LEVEL_FILE, "w") as f:
                json.dump({}, f)
            return {}

    def save_levels(self):
        with open(LEVEL_FILE, "w") as f:
            json.dump(self.levels, f, indent=4)

    def add_xp(self, user_id: str, xp: int = 5):
        user = self.levels.get(user_id, {"xp": 0, "level": 1})
        user["xp"] += xp

        while user["xp"] >= user["level"] * 100:
            user["xp"] -= user["level"] * 100
            user["level"] += 1

        self.levels[user_id] = user
        self.save_levels()
        return user["level"]

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        user_id = str(message.author.id)
        old_level = self.levels.get(user_id, {}).get("level", 1)
        new_level = self.add_xp(user_id)

        if new_level > old_level:
            await message.channel.send(f"🎉 {message.author.mention} level up {new_level} there you go!")

    @commands.command(name="level")
    async def level(self, ctx):
        user_id = str(ctx.author.id)
        data = self.levels.get(user_id, {"xp": 0, "level": 1})
        await ctx.send(f"🧬 {ctx.author.mention}, currently at level {data['level']} with {data['xp']} XP.")

async def setup(bot):
    await bot.add_cog(Leveling(bot))
