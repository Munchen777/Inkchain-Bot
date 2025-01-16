from web3 import AsyncWeb3
from web3.contract import AsyncContract
from web3.contract.async_contract import AsyncContract
from web3.eth.async_eth import ChecksumAddress

from modules import*
from utils.client import Client
from data.abi import BRIDGE_GG_ABI
from modules.interfaces import BridgeModuleInfo


class BridGGWorker(Logger):
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

    async def run(self):
        value, balance = await self.client.get_value_and_normalized_value(
            normalized_min_available_balance=0.025, normalized_min_amount_out=0.01,
            normalized_min_amount_residue=0.01
        )

        self.logger.info(
            f'{self.client.name} Sending {balance} ETH via the official bridge from the Ethereum network to Ink'
        )

        proxy_address_contract: ChecksumAddress = AsyncWeb3.to_checksum_address(
            '0x88ff1e5b602916615391f55854588efcbb7663f0'
        )

        contract: AsyncContract = self.client.w3.eth.contract(
            proxy_address_contract,
            BRIDGE_GG_ABI
        )
        
        try:
            tx_params = await self.client.prepare_transaction(value=value)
            transaction = await contract.functions.BridgeETHTo(
                self.client.address,
                2000,
                b'6272696467670a'
            ).build_transaction(tx_params)
            await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed to send {balance} ETH from the Ethereum network to Ink'
            )