from modules.interfaces import BridgeModuleInfo
from ..logger import Logger
from utils.client import Client


class BridgeNativeWorker(Logger):
    def __init__(self, client: Client, module_info: BridgeModuleInfo):
        super().__init__()

        self.client: Client = client
        self.destination_network: str | None = module_info.destination_network
        self.source_network: str | None = module_info.source_network
        self.source_network_chain_id: int | None = module_info.source_network_chain_id
        self.destination_network_chain_id: int | None = module_info.destination_network_chain_id
        self.module_priority: int | None = module_info.module_priority
        self.module_name: str | None = module_info.module_name
        self.module_display_name: str | None = module_info.module_display_name

    async def bridge(self):
        pass
