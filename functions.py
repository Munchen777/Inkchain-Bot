from utils.client import Client
from modules.bridges import *
from modules.interfaces import *

def get_client(account_name, private_key, proxy, source_network: str) -> Client:
    return Client(account_name, private_key, proxy, source_network)

async def bridge_owlto_op_to_ink(account_name: str, private_key: str, proxy: str | None, module_info: BridgeOwltoOPtoInkModule):
    worker = BridgeOwltoOPtoInkWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def bridge_owlto_base_to_ink(account_name: str, private_key: str, proxy: str | None, module_info: BridgeOwltoBasetoInkModule):
    worker = BridgeOwltoBasetoInkWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def bridge_owlto_ink_to_op(account_name: str, private_key: str, proxy: str | None, module_info: BridgeOwltoInktoOPModule):
    worker = BridgeOwltoInktoOPWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def bridge_owlto_ink_to_base(account_name: str, private_key: str, proxy: str | None, module_info: BridgeOwltoInktoBaseModule):
    worker = BridgeOwltoInktoBaseWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()
