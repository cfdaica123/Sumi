import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Prefer to use .env.production if available (when running for real)
if os.path.exists(".env"):
    load_dotenv(".env")
    print("🚀 Running in PRODUCTION mode")
else:
    load_dotenv(".env.dev")
    print("🌱 Running in DEV mode")

# Get variables from environment file
TOKEN = os.getenv("TOKEN")
PREFIX = os.getenv("PREFIX", "!")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f"🔵 Bot {bot.user} is online")
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
    print("✅ Loaded all cogs.")

bot.run(TOKEN)