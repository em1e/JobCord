import discord
from discord.ext import commands
import os
import sys

# If a .env file exists, load it so local development is easier.
# python-dotenv is listed in `requirements-bot.txt` so this is optional.
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # dotenv is optional; continue if it's not installed.
    pass

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    print("\nERROR: DISCORD_BOT_TOKEN is not set.\n")
    print("Set it in your shell, or create a .env file with the line:\n")
    print("    DISCORD_BOT_TOKEN=your_token_here\n")
    print("Then run: `export DISCORD_BOT_TOKEN=your_token_here` or start a new shell.\n")
    sys.exit(1)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔧 Synced {len(synced)} commands.")
    except Exception as e:
        print(e)

import importlib
import pkgutil

# Import all submodules from discord_bot.commands so their `bot.tree.command`
# decorators execute and register slash commands. This makes adding new
# command modules automatic without editing this file every time.
from discord_bot import commands as commands_pkg

for finder, name, ispkg in pkgutil.iter_modules(commands_pkg.__path__):
    # skip private modules
    if name.startswith("_"):
        continue
    try:
        importlib.import_module(f"discord_bot.commands.{name}")
    except Exception as e:
        print(f"Warning: failed to import command module {name}: {e}")

bot.run(TOKEN)