import logging

from config import Config
from http_client import McApiClient
from discord.ext import commands

from libs import Database

logger = logging.getLogger(__name__)

class McCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        #client = McApiClient()
        #client.start()

async def setup(bot):
    await bot.add_cog(McCog(bot))