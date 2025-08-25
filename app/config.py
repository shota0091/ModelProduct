import os

class Config:
    def __init__(self):
        self.token = os.getenv("DISCORD_BOT_TOKEN")