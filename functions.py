from utils.client import Client
from modules.bridges import*

def get_client(account_name, private_key, proxy) -> Client:
    return Client(account_name, private_key, proxy)

async def bridge_native(account_name, private_key, proxy):
    # здесь выполняется создание инстанса класса и запуск модуля (метода у инстанса класса)
    return True

async def bridge_gg_worker(account_name, private_key, proxy):
    worker = BridGGWorker(get_client(account_name, private_key, proxy))
    return await worker.run()
