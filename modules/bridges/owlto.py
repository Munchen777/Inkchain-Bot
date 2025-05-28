from web3.contract.async_contract import AsyncContract
from web3.eth.async_eth import ChecksumAddress

from modules import *
from utils.client import Client, CustomAsyncWeb3
from data.abi import BRIDGE_OWLTO_ABI
from modules.interfaces import *


class BridgeOwltoOPtoInkWorker(Logger):
    def __init__(self, client: Client, module_info: BridgeOwltoOPtoInkModule):
        super().__init__()

        self.client: Client = client
        self.module_info: BridgeOwltoOPtoInkModule = module_info
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
            return False

        value, balance = result

        self.logger.info(
            f'{self.client.name} Sending {balance} ETH via the Owlto bridge from the Optimism network to Ink'
        )

        proxy_address_contract: ChecksumAddress = CustomAsyncWeb3.to_checksum_address(
            '0x0e83ded9f80e1c92549615d96842f5cb64a08762'
        )

        contract: AsyncContract = self.client.w3.eth.contract(
            address=proxy_address_contract,
            abi=BRIDGE_OWLTO_ABI
        )

        try:
            tx_params = await self.client.prepare_transaction(value=value)
            transaction = await contract.functions.deposit(
                self.client.address,
                CustomAsyncWeb3.to_checksum_address('0x0000000000000000000000000000000000000000'),
                CustomAsyncWeb3.to_checksum_address('0x5e809A85Aa182A9921EDD10a4163745bb3e36284'),
                value,
                88,
                98675412
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed to send {balance} ETH from the OP network to Ink. Error: {error} '
            )
            return False


class BridgeOwltoBasetoInkWorker(Logger):
    def __init__(self, client: Client, module_info: BridgeOwltoBasetoInkModule):
        super().__init__()

        self.client: Client = client
        self.module_info: BridgeOwltoBasetoInkModule = module_info
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
            return False

        value, balance = result

        self.logger.info(
            f'{self.client.name} Sending {balance} ETH via the Owlto bridge from the Base network to Ink'
        )

        proxy_address_contract: ChecksumAddress = CustomAsyncWeb3.to_checksum_address(
            '0xb5cedaf172425bdea4c186f6fcf30b367273da19'
        )

        contract: AsyncContract = self.client.w3.eth.contract(
            address=proxy_address_contract,
            abi=BRIDGE_OWLTO_ABI
        )

        try:
            tx_params = await self.client.prepare_transaction(value=value)
            transaction = await contract.functions.deposit(
                self.client.address,
                CustomAsyncWeb3.to_checksum_address('0x0000000000000000000000000000000000000000'),
                CustomAsyncWeb3.to_checksum_address('0x5e809A85Aa182A9921EDD10a4163745bb3e36284'),
                value,
                88,
                98675412
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed to send {balance} ETH from the Base network to Ink. Error: {error} '
            )
            return False


class BridgeOwltoInktoOPWorker(Logger):
    def __init__(self, client: Client, module_info: BridgeOwltoInktoOPModule):
        super().__init__()

        self.client: Client = client
        self.module_info: BridgeOwltoInktoOPModule = module_info
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
            return False

        value, balance = result

        self.logger.info(
            f'{self.client.name} Sending {balance} ETH via the Owlto bridge from the Ink network to OP'
        )

        proxy_address_contract: ChecksumAddress = CustomAsyncWeb3.to_checksum_address(
            '0x7CFE8Aa0d8E92CCbBDfB12b95AEB7a54ec40f0F5'
        )

        contract: AsyncContract = self.client.w3.eth.contract(
            address=proxy_address_contract,
            abi=BRIDGE_OWLTO_ABI
        )
        
        try:
            tx_params = await self.client.prepare_transaction(value=value)
            transaction = await contract.functions.deposit(
                self.client.address,
                CustomAsyncWeb3.to_checksum_address('0x0000000000000000000000000000000000000000'),
                CustomAsyncWeb3.to_checksum_address('0x1f49a3fa2b5B5b61df8dE486aBb6F3b9df066d86'),
                value,
                3,
                98675412
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed to send {balance} ETH from the Ink network to OP. Error: {error} '
            )
            return False


class BridgeOwltoInktoBaseWorker(Logger):
    def __init__(self, client: Client, module_info: BridgeOwltoInktoBaseModule):
        super().__init__()

        self.client: Client = client
        self.module_info: BridgeOwltoInktoBaseModule = module_info
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
            return False

        value, balance = result

        self.logger.info(
            f'{self.client.name} Sending {balance} ETH via the Owlto bridge from the Ink network to Base'
        )

        proxy_address_contract: ChecksumAddress = CustomAsyncWeb3.to_checksum_address(
            '0x7cfe8aa0d8e92ccbbdfb12b95aeb7a54ec40f0f5'
        )

        contract: AsyncContract = self.client.w3.eth.contract(
            address=proxy_address_contract,
            abi=BRIDGE_OWLTO_ABI
        )

        try:
            tx_params = await self.client.prepare_transaction(value=value)
            transaction = await contract.functions.deposit(
                self.client.address,
                CustomAsyncWeb3.to_checksum_address('0x0000000000000000000000000000000000000000'),
                CustomAsyncWeb3.to_checksum_address('0x1f49a3fa2b5B5b61df8dE486aBb6F3b9df066d86'),
                value,
                12,
                98675412
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed to send {balance} ETH from the Ink network to Base. Error: {error} '
            )
            return False