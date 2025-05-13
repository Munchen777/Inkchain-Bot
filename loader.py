import asyncio

from models import Config
from utils import load_config

config: Config = load_config()
semaphore: asyncio.Semaphore = asyncio.Semaphore()
