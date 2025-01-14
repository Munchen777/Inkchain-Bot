from ..logger import Logger
from utils.client import Client


class BridgeNativeWorker(Logger):
    def __init__(self, client: Client):
        super().__init__()
        self.client = client

    async def bridge(self):
        pass
