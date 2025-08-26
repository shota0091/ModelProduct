# app/main.py
import discord
from discord import app_commands
from dotenv import load_dotenv
from app.repositories.memory_profile import InMemoryProfileRepository
import os

from app.config import Config

load_dotenv()

class AppContext:
    def __init__(self):
        self.config = Config()
        self.intents = discord.Intents.default()
        self.client = discord.Client(intents=self.intents)
        self.tree = app_commands.CommandTree(self.client)
        self.repo = InMemoryProfileRepository()

ctx = AppContext()

@ctx.client.event
async def on_ready():
    try:
        await ctx.tree.sync()
    except Exception as e:
        print("sync error:", e)
    print(f"✅ Logged in as {ctx.client.user}")

ctx.client.run(ctx.config.token)
