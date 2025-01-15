from web3 import AsyncWeb3
from web3.contract import AsyncContract
from web3.contract.async_contract import AsyncContract
from web3.eth.async_eth import ChecksumAddress

from modules import*
from utils.client import Client
from data.abi import BRIDGE_OWLTO_ABI

class BridgeOwltoOPtoInkWorker(Logger):
    def __init__(self, client: Client, module_info):
        super().__init__()
        self.client = client
        self.module_info = module_info

    async def run(self):
        value, balance = await self.client.get_value_and_normalized_value(normalized_fee=0.0005)

        self.logger.info(
            f'{self.client.name} Sending {balance} ETH via the official bridge from the Optimism network to Ink'
        )

        proxy_address_contract: ChecksumAddress = AsyncWeb3.to_checksum_address(
            '0x0e83ded9f80e1c92549615d96842f5cb64a08762'
        )

        contract: AsyncContract = self.client.w3.eth.contract(
            proxy_address_contract,
            BRIDGE_OWLTO_ABI
        )

        try:
            tx_params = await self.client.prepare_transaction(value=value)
            transaction = await contract.functions.deposit(
                self.client.address,
                AsyncWeb3.to_checksum_address('0x0000000000000000000000000000000000000000'),
                AsyncWeb3.to_checksum_address('0x5e809A85Aa182A9921EDD10a4163745bb3e36284'),
                value,
                88,
                98675412
            ).build_transaction(tx_params)
            await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed to send {balance} ETH from the Optimism network to Ink'
            )

    async def bridge_from_base_to_ink(self):
        value, balance = await self.client.get_value_and_normalized_value(normalized_fee=0.0005)

        self.logger.info(
            f'{self.client.name} Sending {balance} ETH via the official bridge from the Base network to Ink'
        )

        proxy_address_contract: ChecksumAddress = AsyncWeb3.to_checksum_address(
            '0xb5cedaf172425bdea4c186f6fcf30b367273da19'
        )

        contract: AsyncContract = self.client.w3.eth.contract(
            proxy_address_contract,
            BRIDGE_OWLTO_ABI
        )

        try:
            tx_params = await self.client.prepare_transaction(value=value)
            transaction = await contract.functions.deposit(
                self.client.address,
                AsyncWeb3.to_checksum_address('0x0000000000000000000000000000000000000000'),
                AsyncWeb3.to_checksum_address('0x5e809A85Aa182A9921EDD10a4163745bb3e36284'),
                value,
                88,
                98675412
            ).build_transaction(tx_params)
            await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed to send {balance} ETH from the Base network to Ink'
            )

    async def bridge_from_ink_to_op(self):
        value, balance = await self.client.get_value_and_normalized_value(normalized_fee=0.0005)

        self.logger.info(
            f'{self.client.name} Sending {balance} ETH via the official bridge from the Ink network to OP'
        )

        proxy_address_contract: ChecksumAddress = AsyncWeb3.to_checksum_address(
            ''
        )

        contract: AsyncContract = self.client.w3.eth.contract(
            proxy_address_contract,
            BRIDGE_OWLTO_ABI
        )

        try:
            tx_params = await self.client.prepare_transaction(value=value)
            transaction = await contract.functions.deposit(            ).build_transaction(tx_params)
            await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed to send {balance} ETH from the Ink network to OP'
            )

    async def bridge_from_ink_to_op(self):
        value, balance = await self.client.get_value_and_normalized_value(normalized_fee=0.0005)

        self.logger.info(
            f'{self.client.name} Sending {balance} ETH via the official bridge from the Ink network to Base'
        )

        proxy_address_contract: ChecksumAddress = AsyncWeb3.to_checksum_address(
            ''
        )

        contract: AsyncContract = self.client.w3.eth.contract(
            proxy_address_contract,
            BRIDGE_OWLTO_ABI
        )

        try:
            tx_params = await self.client.prepare_transaction(value=value)
            transaction = await contract.functions.deposit(            ).build_transaction(tx_params)
            await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed to send {balance} ETH from the Ink network to Base'
            )