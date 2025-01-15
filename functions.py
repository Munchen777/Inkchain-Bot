from utils.client import Client
from modules.bridges import *


def get_client(account_name, private_key, proxy) -> Client:
    return Client(account_name, private_key, proxy)

async def bridge_native(account_name, private_key, proxy, module_info):
    worker = BridgeNativeWorker(
        client=get_client(account_name, private_key, proxy),
        module_info=module_info
    )
    return await worker.bridge()

async def bridge_owlto_op_to_ink(account_name, private_key, proxy, module_info):
    worker = BridgeOwltoOPtoInkWorker(
        client=get_client(account_name, private_key, proxy),
        module_info=module_info
    )
    return await worker.run()
