
from web3 import AsyncWeb3
from web3.contract import AsyncContract
from web3.contract.async_contract import AsyncContract
from web3.eth.async_eth import ChecksumAddress

from modules import *
from utils.client import Client
from data.abi import BRIDGE_GG_ABI
from modules.interfaces import BridGGEthereumtoInkModule


class BridGGEthereumtoInkWorker(Logger):
    def __init__(self, client: Client, module_info: BridGGEthereumtoInkModule):
        super().__init__()

        self.client: Client = client
        self.module_info: BridGGEthereumtoInkModule = module_info
        self.destination_network: str | None = module_info.destination_network
        self.source_network: str | None = module_info.source_network
        self.source_network_chain_id: int | None = module_info.source_network_chain_id
        self.destination_network_chain_id: int | None = module_info.destination_network_chain_id
        self.module_priority: int | None = module_info.module_priority
        self.module_name: str | None = module_info.module_name
        self.module_display_name: str | None = module_info.module_display_name

    async def run(self):
        value, balance = await self.client.get_value_and_normalized_value(
            normalized_fee=self.module_info.fee,
            normalized_min_available_balance=self.module_info.min_available_balance,
            normalized_min_amount_out=self.module_info.min_amount_out,
            normalized_min_amount_residue=self.module_info.min_amount_residue
        )

        self.logger.info(
            f'{self.client.name} Sending {balance} ETH via the official bridge from the Ethereum network to Ink'
        )

        proxy_address_contract: ChecksumAddress = AsyncWeb3.to_checksum_address(
            '0x88ff1e5b602916615391f55854588efcbb7663f0'
        )

        contract: AsyncContract = self.client.w3.eth.contract(
            address=proxy_address_contract,
            abi=BRIDGE_GG_ABI
        )
        
        try:
            tx_params = await self.client.prepare_transaction(value=value)
            transaction = await contract.functions.bridgeETHTo(
                self.client.address,
                200000,
                b'6272696467670a'
            ).build_transaction(tx_params)
            await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed to send {balance} ETH via the official bridge from the Ethereum network to Ink. Error: {error} '
            )
