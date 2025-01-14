from utils.client import Client
from modules.bridges import *
from modules.interfaces import (BridgeModuleInfo, BridgeOwltoModule, BridgeGGModule)


def get_client(account_name, private_key, proxy) -> Client:
    return Client(account_name, private_key, proxy)


async def bridge_native_worker(account_name: str, private_key: str, proxy: str | None, module_info: BridgeModuleInfo):
    worker = BridgeNativeWorker(
        client=get_client(account_name, private_key, proxy),
        module_info=module_info,
    )
    return await worker.bridge()

async def bridge_gg_worker(account_name: str, private_key: str, proxy: str | None, module_info: BridgeGGModule):
    worker = BridGGWorker(
        client=get_client(account_name, private_key, proxy),
        module_info=module_info
    )
    return await worker.run()

async def bridge_owlto_worker(account_name: str, private_key: str, proxy: str | None, module_info: BridgeOwltoModule):
    worker = BridgeOwltoWorker(
        client=get_client(account_name, private_key, proxy),
        module_info=module_info
    )
    return await worker.run()
