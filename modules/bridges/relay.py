from web3 import AsyncWeb3

from curl_cffi.requests import AsyncSession

from modules import *
from utils.client import Client
from modules.interfaces import *

logger: Logger = Logger().get_logger()

async def get_data(client: Client, value: int,  module_info):
    headers = {
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/json',
        'origin': 'https://relay.link',
        'priority': 'u=1, i',
        'referer': f'https://relay.link/bridge/ink?fromChainId={module_info.source_network_chain_id}&fromCurrency=0x0000000000000000000000000000000000000000&toCurrency=0x0000000000000000000000000000000000000000',
        'user-agent': client.get_user_agent(),
    }
    
    json_data = {
        'user': client.address,
        'originChainId': module_info.source_network_chain_id,
        'destinationChainId': module_info.destination_network_chain_id,
        'originCurrency': '0x0000000000000000000000000000000000000000',
        'destinationCurrency': '0x0000000000000000000000000000000000000000',
        'recipient': client.address,
        'tradeType': 'EXACT_INPUT',
        'amount': value,
        'referrer': 'relay.link/swap',
        'useExternalLiquidity': False,
    }
    try:
        async with AsyncSession() as session:
            response = await session.post(
                'https://api.relay.link/quote',
                headers=headers,
                json=json_data,
                proxy=client.proxy_init,
            )
            if response.status_code == 200:
                tx_data = response.json()
                return tx_data

            else:
                logger.error(f"{client.name} Failed request: {response.status_code}")
                return None
    except Exception as error:
        logger.error(
            f'{client.name} Failed request:  {error} '
        )
        return None


class BridgeRelayOPtoInkWorker(Logger):
    def __init__(self, client: Client, module_info: BridgeRelayOPtoInkModule):
        super().__init__()

        self.client: Client = client
        self.module_info: BridgeRelayOPtoInkModule = module_info
        self.destination_network: str | None = module_info.destination_network
        self.source_network: str | None = module_info.source_network
        self.source_network_chain_id: int | None = module_info.source_network_chain_id
        self.destination_network_chain_id: int | None = module_info.destination_network_chain_id
        self.module_priority: int | None = module_info.module_priority
        self.module_name: str | None = module_info.module_name
        self.module_display_name: str | None = module_info.module_display_name

    async def run(self):
        result = await self.client.get_value_and_normalized_value(
            normalized_fee=self.module_info.fee,
            normalized_min_available_balance=self.module_info.min_available_balance,
            normalized_min_amount_out=self.module_info.min_amount_out,
            normalized_min_amount_residue=self.module_info.min_amount_residue
        )

        if result is None:
            return

        value, balance = result

        self.logger.info(
            f'{self.client.name} Sending {balance} ETH via the Relay bridge from the OP network to Ink'
        )

        tx_data = await get_data(client=self.client, value=value, module_info=self.module_info)

        if tx_data is None: return

        try:
            tx_params = await self.client.prepare_transaction(value=value)
            tx_params.update({
                'to': AsyncWeb3.to_checksum_address(tx_data["steps"][0]['items'][0]['data']['to']),
                'data': tx_data["steps"][0]['items'][0]['data']['data']
            })
            return await self.client.send_transaction(tx_params, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed to send {balance} ETH from the OP network to Ink. Error: {error} '
            )


class BridgeRelayBasetoInkWorker(Logger):
    def __init__(self, client: Client, module_info: BridgeRelayBasetoInkModule):
        super().__init__()

        self.client: Client = client
        self.module_info: BridgeRelayBasetoInkModule = module_info
        self.destination_network: str | None = module_info.destination_network
        self.source_network: str | None = module_info.source_network
        self.source_network_chain_id: int | None = module_info.source_network_chain_id
        self.destination_network_chain_id: int | None = module_info.destination_network_chain_id
        self.module_priority: int | None = module_info.module_priority
        self.module_name: str | None = module_info.module_name
        self.module_display_name: str | None = module_info.module_display_name

    async def run(self):
        result = await self.client.get_value_and_normalized_value(
            normalized_fee=self.module_info.fee,
            normalized_min_available_balance=self.module_info.min_available_balance,
            normalized_min_amount_out=self.module_info.min_amount_out,
            normalized_min_amount_residue=self.module_info.min_amount_residue
        )

        if result is None:
            return

        value, balance = result

        self.logger.info(
            f'{self.client.name} Sending {balance} ETH via the Relay bridge from the Base network to Ink'
        )

        tx_data = await get_data(client=self.client, value=value, module_info=self.module_info)

        if tx_data is None: return

        try:
            tx_params = await self.client.prepare_transaction(value=value)
            tx_params.update({
                'to': AsyncWeb3.to_checksum_address(tx_data["steps"][0]['items'][0]['data']['to']),
                'data': tx_data["steps"][0]['items'][0]['data']['data']
            })
            result = await self.client.send_transaction(tx_params, need_hash=True)
            return result
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed to send {balance} ETH from the Base network to Ink. Error: {error} '
            )


class BridgeRelayInktoOPWorker(Logger):
    def __init__(self, client: Client, module_info: BridgeRelayInktoOPModule):
        super().__init__()

        self.client: Client = client
        self.module_info: BridgeRelayInktoOPModule = module_info
        self.destination_network: str | None = module_info.destination_network
        self.source_network: str | None = module_info.source_network
        self.source_network_chain_id: int | None = module_info.source_network_chain_id
        self.destination_network_chain_id: int | None = module_info.destination_network_chain_id
        self.module_priority: int | None = module_info.module_priority
        self.module_name: str | None = module_info.module_name
        self.module_display_name: str | None = module_info.module_display_name

    async def run(self):
        result = await self.client.get_value_and_normalized_value(
            normalized_fee=self.module_info.fee,
            normalized_min_available_balance=self.module_info.min_available_balance,
            normalized_min_amount_out=self.module_info.min_amount_out,
            normalized_min_amount_residue=self.module_info.min_amount_residue
        )

        if result is None:
            return

        value, balance = result

        self.logger.info(
            f'{self.client.name} Sending {balance} ETH via the Relay bridge from the Ink network to OP'
        )

        tx_data = await get_data(client=self.client, value=value, module_info=self.module_info)

        if tx_data is None: return

        try:
            tx_params = await self.client.prepare_transaction(value=value)
            tx_params.update({
                'to': AsyncWeb3.to_checksum_address(tx_data["steps"][0]['items'][0]['data']['to']),
                'data': tx_data["steps"][0]['items'][0]['data']['data']
            })
            result = await self.client.send_transaction(tx_params, need_hash=True)
            return result
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed to send {balance} ETH from the Ink network to OP. Error: {error} '
            )


class BridgeRelayInktoBaseWorker(Logger):
    def __init__(self, client: Client, module_info: BridgeRelayInktoBaseModule):
        super().__init__()

        self.client: Client = client
        self.module_info: BridgeRelayInktoBaseModule = module_info
        self.destination_network: str | None = module_info.destination_network
        self.source_network: str | None = module_info.source_network
        self.source_network_chain_id: int | None = module_info.source_network_chain_id
        self.destination_network_chain_id: int | None = module_info.destination_network_chain_id
        self.module_priority: int | None = module_info.module_priority
        self.module_name: str | None = module_info.module_name
        self.module_display_name: str | None = module_info.module_display_name

    async def run(self):
        result = await self.client.get_value_and_normalized_value(
            normalized_fee=self.module_info.fee,
            normalized_min_available_balance=self.module_info.min_available_balance,
            normalized_min_amount_out=self.module_info.min_amount_out,
            normalized_min_amount_residue=self.module_info.min_amount_residue
        )

        if result is None:
            return

        value, balance = result

        self.logger.info(
            f'{self.client.name} Sending {balance} ETH via the Relay bridge from the Ink network to Base'
        )

        tx_data = await get_data(client=self.client, value=value, module_info=self.module_info)

        if tx_data is None: return

        try:
            tx_params = await self.client.prepare_transaction(value=value)
            tx_params.update({
                'to': AsyncWeb3.to_checksum_address(tx_data["steps"][0]['items'][0]['data']['to']),
                'data': tx_data["steps"][0]['items'][0]['data']['data']
            })
            result = await self.client.send_transaction(tx_params, need_hash=True)
            return result
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed to send {balance} ETH from the Ink network to Base. Error: {error} '
            )
