import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load environment variables
if os.path.exists(".env"):
    load_dotenv(".env")
    print("🚀 Running in PRODUCTION mode")
else:
    load_dotenv(".env.dev")
    print("🌱 Running in DEV mode")

# Get variables
TOKEN = os.getenv("TOKEN")
PREFIX = os.getenv("PREFIX", "!")
COOKIES_DATA = os.getenv("COOKIES_DATA")

# Create cookies.txt from env (if exists)
if COOKIES_DATA:
    with open("cookies.txt", "w", encoding="utf-8") as f:
        f.write(COOKIES_DATA)
    print("🍪 cookies.txt created from environment")
else:
    print("⚠️ COOKIES_DATA not found — cookies.txt not created")

# Setup bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f"🔵 Bot {bot.user} is online")
    
    # Load all cogs
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"✅ Loaded {filename}")
            except Exception as e:
                print(f"❌ Failed to load {filename}: {e}")

bot.run(TOKEN)
