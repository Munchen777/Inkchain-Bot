import time
import random

from web3 import AsyncWeb3
from web3.contract import AsyncContract
from web3.contract.async_contract import AsyncContract
from web3.eth.async_eth import ChecksumAddress

from modules import *
from utils.client import Client
from data.abi import *
from modules.interfaces import *
from settings import NETWORK_TOKEN_CONTRACTS


logger: Logger = Logger().get_logger()


async def approve(
        client: Client, token_out_name: str, amount_out: int, address_contract: ChecksumAddress = None,
        spender_address: ChecksumAddress = '0xb5B494e63c3a52391E6C8E4a4D6aa1AEF369Fb6B'
    ):
    address_contract = AsyncWeb3.to_checksum_address(NETWORK_TOKEN_CONTRACTS.get(client.network.name, {}).get(token_out_name, ""))

    contract: AsyncContract = client.w3.eth.contract(
        address=address_contract,
        abi=SWAP_TOKEN_ABI
    )

    allowance = await contract.functions.allowance(client.address, spender_address).call()

    if allowance > amount_out: return True

    contract: AsyncContract = client.w3.eth.contract(
        address=address_contract,
        abi=SWAP_TOKEN_ABI
    )

    try:
        tx_params = await client.prepare_transaction()
        transaction = await contract.functions.approve(
            AsyncWeb3.to_checksum_address(spender_address),
            115792089237316195423570985008687907853269984665640564039457584007913129639935                           
        ).build_transaction(tx_params)
        await client.send_transaction(transaction, need_hash=True)
    except Exception as error:
        logger.error(
            f'{client.name} Failed approve {token_out_name}. Error: {error}'
        )

async def canculate_amount_out_swaps(
        client: Client, token_out_name: str, token_get_name: str, min_available_balance_token: float,
        min_clearance: float, from_eth: bool
    ):
    if from_eth:
        balance = await client.get_token_balance(token_name=token_get_name)      
        decimals = await client.get_decimals(token_name=token_get_name)
    if not from_eth:
        balance = await client.get_token_balance(token_name=token_out_name)      
        decimals = await client.get_decimals(token_name=token_out_name)

    value = 0 if balance is None else balance / 10 ** decimals

    if from_eth:
        if value > min_available_balance_token or min_available_balance_token - value < min_clearance:
            logger.warning(
                f'{client.name} Skip the swap {token_out_name} to {token_get_name} on the Ink network, because we already have enough tokens {token_get_name}'
            )
            return None
        
        free_amount = min_available_balance_token - value
        
    if not from_eth:
        if value < min_available_balance_token or value < min_available_balance_token + min_clearance:
            logger.warning(
                f'{client.name} Skip the swap {token_out_name} to {token_get_name} on the Ink network, because you have a minimum number of {token_out_name} tokens'
            )
            return None
        
        free_amount = value - min_available_balance_token

    if free_amount < min_clearance:
        percent = 100
    else:
        percent = random.randint(50, 100)

    amount_out = round(free_amount * (1 - percent / 100), random.randint(2, 4))

    if amount_out < min_clearance:
        amount_out = (random.randint(int(min_clearance * 10 ** decimals), int(free_amount * 10 ** decimals)) / 10 ** decimals)
        
    return amount_out, decimals


class SwapInkswapETHtoISWAPWorker(Logger):
    def __init__(self, client: Client, module_info: SwapInkswapETHtoISWAPModule):
        super().__init__()

        self.client: Client = client
        self.module_info: SwapInkswapETHtoISWAPModule = module_info
        self.destination_network: str | None = module_info.destination_network
        self.source_network: str | None = module_info.source_network
        self.source_network_chain_id: int | None = module_info.source_network_chain_id
        self.destination_network_chain_id: int | None = module_info.destination_network_chain_id
        self.module_priority: int | None = module_info.module_priority
        self.module_name: str | None = module_info.module_name
        self.module_display_name: str | None = module_info.module_display_name

        self.deadline = int(time.time()) + 20 * 60

    async def run(self):
        result = await canculate_amount_out_swaps(
            client=self.client, token_out_name='ETH', token_get_name='ISWAP',
            min_available_balance_token=25.0, min_clearance=10.0, from_eth=True
        )
        
        if result is None: return

        amount_out, decimals = result

        self.logger.info(
            f'{self.client.name} Swap ETH to {amount_out} ISWAP on the Ink network'
        )

        address_contract: ChecksumAddress = AsyncWeb3.to_checksum_address(
            '0xb5B494e63c3a52391E6C8E4a4D6aa1AEF369Fb6B'
        )

        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract,
            abi=SWAP_INKSWAP_ABI
        )

        amount_out = int(amount_out * 10 ** decimals)
        path = [
            AsyncWeb3.to_checksum_address("0x4200000000000000000000000000000000000006"),
            AsyncWeb3.to_checksum_address("0x6814B9C5dae3DD05A8dBE9bF2b4E4FbB9Cef5302")
        ]
        slippage_tolerance = 0.005 

        amounts_in = await contract.functions.getAmountsIn(amount_out, path).call()

        value = int(amounts_in[0] * (1 + slippage_tolerance)) 

        balance_nativ = await self.client.get_token_balance(check_native=True) 
        min_balance = int(self.module_info.min_available_balance * 10 ** 18) 
        if balance_nativ < min_balance + value:
            self.logger.warning(
                f'{self.client.name} Skip the swap ETH to ISWAP on the Ink network. Insufficient ETH'
            )
            return

        try:
            tx_params = await self.client.prepare_transaction(value=value)
            transaction = await contract.functions.swapETHForExactTokens(
                amount_out,
                path,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap ETH to ISWAP on the Ink network. Error: {error}'
            )


class SwapInkswapETHtoSINKWorker(Logger):
    def __init__(self, client: Client, module_info: SwapInkswapETHtoSINKModule):
        super().__init__()

        self.client: Client = client
        self.module_info: SwapInkswapETHtoSINKModule = module_info
        self.destination_network: str | None = module_info.destination_network
        self.source_network: str | None = module_info.source_network
        self.source_network_chain_id: int | None = module_info.source_network_chain_id
        self.destination_network_chain_id: int | None = module_info.destination_network_chain_id
        self.module_priority: int | None = module_info.module_priority
        self.module_name: str | None = module_info.module_name
        self.module_display_name: str | None = module_info.module_display_name

        self.deadline = int(time.time()) + 20 * 60

    async def run(self):
        result = await canculate_amount_out_swaps(
            client=self.client, token_out_name='ETH', token_get_name='SINK',
            min_available_balance_token=5000.0, min_clearance=750.0, from_eth=True
        )
        
        if result is None: return

        amount_out, decimals = result

        self.logger.info(
            f'{self.client.name} Swap ETH to {amount_out} SINK on the Ink network'
        )

        address_contract: ChecksumAddress = AsyncWeb3.to_checksum_address(
            '0xb5b494e63c3a52391e6c8e4a4d6aa1aef369fb6b'
        )

        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract,
            abi=SWAP_INKSWAP_ABI
        )

        amount_out = int(amount_out * 10 ** decimals)
        path = [
            AsyncWeb3.to_checksum_address("0x4200000000000000000000000000000000000006"),
            AsyncWeb3.to_checksum_address("0xD43e76fF8f95035E220070BdDFD3C0C2bdD3051B")
        ]
        slippage_tolerance = 0.005 

        amounts_in = await contract.functions.getAmountsIn(amount_out, path).call()

        value = int(amounts_in[0] * (1 + slippage_tolerance)) 

        balance_nativ = await self.client.get_token_balance(check_native=True) 
        min_balance = int(self.module_info.min_available_balance * 10 ** 18) 
        if balance_nativ < min_balance + value:
            self.logger.warning(
                f'{self.client.name} Skip the swap ETH to SINK on the Ink network. Insufficient ETH'
            )
            return

        try:
            tx_params = await self.client.prepare_transaction(value=value)
            transaction = await contract.functions.swapETHForExactTokens(
                amount_out,
                path,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap ETH to SINK on the Ink network. Error: {error}'
            )


class SwapInkswapETHtoKRAKENWorker(Logger):
    def __init__(self, client: Client, module_info: SwapInkswapETHtoKRAKENModule):
        super().__init__()

        self.client: Client = client
        self.module_info: SwapInkswapETHtoKRAKENModule = module_info
        self.destination_network: str | None = module_info.destination_network
        self.source_network: str | None = module_info.source_network
        self.source_network_chain_id: int | None = module_info.source_network_chain_id
        self.destination_network_chain_id: int | None = module_info.destination_network_chain_id
        self.module_priority: int | None = module_info.module_priority
        self.module_name: str | None = module_info.module_name
        self.module_display_name: str | None = module_info.module_display_name

        self.deadline = int(time.time()) + 20 * 60

    async def run(self):
        result = await canculate_amount_out_swaps(
            client=self.client, token_out_name='ETH', token_get_name='KRAKEN',
            min_available_balance_token=50000.0, min_clearance=10000.0, from_eth=True
        )
        
        if result is None: return

        amount_out, decimals = result

        self.logger.info(
            f'{self.client.name} Swap ETH to {amount_out} KRAKEN on the Ink network'
        )

        address_contract: ChecksumAddress = AsyncWeb3.to_checksum_address(
            '0xb5b494e63c3a52391e6c8e4a4d6aa1aef369fb6b'
        )

        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract,
            abi=SWAP_INKSWAP_ABI
        )

        amount_out = int(amount_out * 10 ** decimals)
        path = [
            AsyncWeb3.to_checksum_address("0x4200000000000000000000000000000000000006"),
            AsyncWeb3.to_checksum_address("0xCa5f2cCBD9C40b32657dF57c716De44237f80F05")
        ]
        slippage_tolerance = 0.005 

        amounts_in = await contract.functions.getAmountsIn(amount_out, path).call()

        value = int(amounts_in[0] * (1 + slippage_tolerance)) 

        balance_nativ = await self.client.get_token_balance(check_native=True) 
        min_balance = int(self.module_info.min_available_balance * 10 ** 18) 
        if balance_nativ < min_balance + value:
            self.logger.warning(
                f'{self.client.name} Skip the swap ETH to KRAKEN on the Ink network. Insufficient ETH'
            )
            return

        try:
            tx_params = await self.client.prepare_transaction(value=value)
            transaction = await contract.functions.swapETHForExactTokens(
                amount_out,
                path,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap ETH to KRAKEN on the Ink network. Error: {error}'
            )


class SwapInkswapSINKtoETHWorker(Logger):
    def __init__(self, client: Client, module_info: SwapInkswapISWAPtoETHModule):
        super().__init__()

        self.client: Client = client
        self.module_info: SwapInkswapISWAPtoETHModule = module_info
        self.destination_network: str | None = module_info.destination_network
        self.source_network: str | None = module_info.source_network
        self.source_network_chain_id: int | None = module_info.source_network_chain_id
        self.destination_network_chain_id: int | None = module_info.destination_network_chain_id
        self.module_priority: int | None = module_info.module_priority
        self.module_name: str | None = module_info.module_name
        self.module_display_name: str | None = module_info.module_display_name

        self.deadline = int(time.time()) + 20 * 60

    async def run(self):       
        result = await canculate_amount_out_swaps(
            client=self.client, token_out_name='ISWAP', token_get_name='ETH',
            min_available_balance_token=25.0, min_clearance=10.0, from_eth=False
        )
        
        if result is None: return

        amount_out, decimals = result

        await approve(
            client=self.client, token_out_name='ISWAP', amount_out=int(amount_out * 10 ** decimals)
        )

        self.logger.info(
            f'{self.client.name} Swap {amount_out} ISWAP to ETH on the Ink network'
        )

        address_contract: ChecksumAddress = AsyncWeb3.to_checksum_address(
            '0xb5B494e63c3a52391E6C8E4a4D6aa1AEF369Fb6B'
        )

        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract,
            abi=SWAP_INKSWAP_ABI
        )

        amount_out = int(amount_out * 10 ** decimals)
        path = [
            AsyncWeb3.to_checksum_address("0x6814B9C5dae3DD05A8dBE9bF2b4E4FbB9Cef5302"),
            AsyncWeb3.to_checksum_address("0x4200000000000000000000000000000000000006")
        ]
        slippage_tolerance = 0.05 
        amounts_in = await contract.functions.getAmountsOut(amount_out, path).call()
        amount_out_min = int(amounts_in[1] * (1 - slippage_tolerance)) 
        try:
            
            tx_params = await self.client.prepare_transaction()
            transaction = await contract.functions.swapExactTokensForETHSupportingFeeOnTransferTokens(
                amount_out,
                amount_out_min,
                path,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap ISWAP to ETH on the Ink network. Error: {error}'
            )


class SwapInkswapISWAPtoETHWorker(Logger):
    def __init__(self, client: Client, module_info: SwapInkswapSINKtoETHModule):
        super().__init__()

        self.client: Client = client
        self.module_info: SwapInkswapSINKtoETHModule = module_info
        self.destination_network: str | None = module_info.destination_network
        self.source_network: str | None = module_info.source_network
        self.source_network_chain_id: int | None = module_info.source_network_chain_id
        self.destination_network_chain_id: int | None = module_info.destination_network_chain_id
        self.module_priority: int | None = module_info.module_priority
        self.module_name: str | None = module_info.module_name
        self.module_display_name: str | None = module_info.module_display_name

        self.deadline = int(time.time()) + 20 * 60

    async def run(self):       
        result = await canculate_amount_out_swaps(
            client=self.client, token_out_name='SINK', token_get_name='ETH',
            min_available_balance_token=5000.0, min_clearance=750.0, from_eth=False
        )
        
        if result is None: return

        amount_out, decimals = result

        await approve(
            client=self.client, token_out_name='SINK', amount_out=int(amount_out * 10 ** decimals)
        )

        self.logger.info(
            f'{self.client.name} Swap {amount_out} SINK to ETH on the Ink network'
        )

        address_contract: ChecksumAddress = AsyncWeb3.to_checksum_address(
            '0xb5b494e63c3a52391e6c8e4a4d6aa1aef369fb6b'
        )

        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract,
            abi=SWAP_INKSWAP_ABI
        )

        amount_out = int(amount_out * 10 ** decimals)
        path = [
            AsyncWeb3.to_checksum_address("0xD43e76fF8f95035E220070BdDFD3C0C2bdD3051B"),
            AsyncWeb3.to_checksum_address("0x4200000000000000000000000000000000000006")
        ]
        slippage_tolerance = 0.05 
        amounts_in = await contract.functions.getAmountsOut(amount_out, path).call()
        amount_out_min = int(amounts_in[1] * (1 - slippage_tolerance)) 
        try:
            
            tx_params = await self.client.prepare_transaction()
            transaction = await contract.functions.swapExactTokensForETHSupportingFeeOnTransferTokens(
                amount_out,
                amount_out_min,
                path,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap SINK to ETH on the Ink network. Error: {error}'
            )


class SwapInkswapKRAKENtoETHWorker(Logger):
    def __init__(self, client: Client, module_info: SwapInkswapKRAKENtoETHModule):
        super().__init__()

        self.client: Client = client
        self.module_info: SwapInkswapKRAKENtoETHModule = module_info
        self.destination_network: str | None = module_info.destination_network
        self.source_network: str | None = module_info.source_network
        self.source_network_chain_id: int | None = module_info.source_network_chain_id
        self.destination_network_chain_id: int | None = module_info.destination_network_chain_id
        self.module_priority: int | None = module_info.module_priority
        self.module_name: str | None = module_info.module_name
        self.module_display_name: str | None = module_info.module_display_name

        self.deadline = int(time.time()) + 20 * 60

    async def run(self):       
        result = await canculate_amount_out_swaps(
            client=self.client, token_out_name='KRAKEN', token_get_name='ETH',
            min_available_balance_token=50_000.0, min_clearance=10_000.0, from_eth=False
        )
        
        if result is None: return

        amount_out, decimals = result

        await approve(
            client=self.client, token_out_name='KRAKEN', amount_out=int(amount_out * 10 ** decimals)
        )

        self.logger.info(
            f'{self.client.name} Swap {amount_out} KRAKEN to ETH on the Ink network'
        )

        address_contract: ChecksumAddress = AsyncWeb3.to_checksum_address(
            '0xb5b494e63c3a52391e6c8e4a4d6aa1aef369fb6b'
        )

        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract,
            abi=SWAP_INKSWAP_ABI
        )

        amount_out = int(amount_out * 10 ** decimals)
        path = [
            AsyncWeb3.to_checksum_address("0xCa5f2cCBD9C40b32657dF57c716De44237f80F05"),
            AsyncWeb3.to_checksum_address("0x4200000000000000000000000000000000000006")
        ]
        slippage_tolerance = 0.05 
        amounts_in = await contract.functions.getAmountsOut(amount_out, path).call()
        amount_out_min = int(amounts_in[1] * (1 - slippage_tolerance)) 
        try:
            
            tx_params = await self.client.prepare_transaction()
            transaction = await contract.functions.swapExactTokensForETHSupportingFeeOnTransferTokens(
                amount_out,
                amount_out_min,
                path,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap KRAKEN to ETH on the Ink network. Error: {error}'
            )


class SwapInkswapISWAPtoSINKWorker(Logger):
    def __init__(self, client: Client, module_info: SwapInkswapISWAPtoSINKModule):
        super().__init__()

        self.client: Client = client
        self.module_info: SwapInkswapISWAPtoSINKModule = module_info
        self.destination_network: str | None = module_info.destination_network
        self.source_network: str | None = module_info.source_network
        self.source_network_chain_id: int | None = module_info.source_network_chain_id
        self.destination_network_chain_id: int | None = module_info.destination_network_chain_id
        self.module_priority: int | None = module_info.module_priority
        self.module_name: str | None = module_info.module_name
        self.module_display_name: str | None = module_info.module_display_name

        self.deadline = int(time.time()) + 20 * 60

    async def run(self):       
        result = await canculate_amount_out_swaps(
            client=self.client, token_out_name='ISWAP', token_get_name='SINK',
            min_available_balance_token=25.0, min_clearance=10.0, from_eth=False
        )
        
        if result is None: return

        amount_out, decimals = result
        
        await approve(
            client=self.client, token_out_name='ISWAP', amount_out=int(amount_out * 10 ** decimals)
        )

        self.logger.info(
            f'{self.client.name} Swap {amount_out} ISWAP to SINK on the Ink network'
        )

        address_contract: ChecksumAddress = AsyncWeb3.to_checksum_address(
            '0xb5b494e63c3a52391e6c8e4a4d6aa1aef369fb6b'
        )

        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract,
            abi=SWAP_INKSWAP_ABI
        )

        amount_out = int(amount_out * 10 ** decimals)
        path = [
            AsyncWeb3.to_checksum_address("0x6814B9C5dae3DD05A8dBE9bF2b4E4FbB9Cef5302"),
            AsyncWeb3.to_checksum_address("0x4200000000000000000000000000000000000006"),
            AsyncWeb3.to_checksum_address("0xD43e76fF8f95035E220070BdDFD3C0C2bdD3051B")
        ]
        slippage_tolerance = 0.05 
        amounts_in = await contract.functions.getAmountsOut(amount_out, path).call()
        amount_out_min = int(amounts_in[1] * (1 - slippage_tolerance)) 
        try:
            
            tx_params = await self.client.prepare_transaction()
            transaction = await contract.functions.swapExactTokensForTokensSupportingFeeOnTransferTokens(
                amount_out,
                amount_out_min,
                path,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap ISWAP to SINK on the Ink network. Error: {error}'
            )


class SwapInkswapSINKtoISWAPWorker(Logger):
    def __init__(self, client: Client, module_info: SwapInkswapSINKtoISWAPModule):
        super().__init__()

        self.client: Client = client
        self.module_info: SwapInkswapSINKtoISWAPModule = module_info
        self.destination_network: str | None = module_info.destination_network
        self.source_network: str | None = module_info.source_network
        self.source_network_chain_id: int | None = module_info.source_network_chain_id
        self.destination_network_chain_id: int | None = module_info.destination_network_chain_id
        self.module_priority: int | None = module_info.module_priority
        self.module_name: str | None = module_info.module_name
        self.module_display_name: str | None = module_info.module_display_name

        self.deadline = int(time.time()) + 20 * 60

    async def run(self):       
        result = await canculate_amount_out_swaps(
            client=self.client, token_out_name='SINK', token_get_name='ISWAP',
            min_available_balance_token=5000.0, min_clearance=750.0, from_eth=False
        )
        
        if result is None: return

        amount_out, decimals = result
        
        await approve(
            client=self.client, token_out_name='SINK', amount_out=int(amount_out * 10 ** decimals)
        )

        self.logger.info(
            f'{self.client.name} Swap {amount_out} SINK to ISWAP on the Ink network'
        )

        address_contract: ChecksumAddress = AsyncWeb3.to_checksum_address(
            '0xb5b494e63c3a52391e6c8e4a4d6aa1aef369fb6b'
        )

        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract,
            abi=SWAP_INKSWAP_ABI
        )

        amount_out = int(amount_out * 10 ** decimals)
        path = [
            AsyncWeb3.to_checksum_address("0xD43e76fF8f95035E220070BdDFD3C0C2bdD3051B"),
            AsyncWeb3.to_checksum_address("0x4200000000000000000000000000000000000006"),
            AsyncWeb3.to_checksum_address("0x6814B9C5dae3DD05A8dBE9bF2b4E4FbB9Cef5302")
        ]
        slippage_tolerance = 0.05 
        amounts_in = await contract.functions.getAmountsOut(amount_out, path).call()
        amount_out_min = int(amounts_in[1] * (1 - slippage_tolerance)) 
        try:
            
            tx_params = await self.client.prepare_transaction()
            transaction = await contract.functions.swapExactTokensForTokensSupportingFeeOnTransferTokens(
                amount_out,
                amount_out_min,
                path,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap SINK to ISWAP on the Ink network. Error: {error}'
            )


class SwapInkswapSINKtoKRAKENWorker(Logger):
    def __init__(self, client: Client, module_info: SwapInkswapSINKtoKRAKENModule):
        super().__init__()

        self.client: Client = client
        self.module_info: SwapInkswapSINKtoKRAKENModule = module_info
        self.destination_network: str | None = module_info.destination_network
        self.source_network: str | None = module_info.source_network
        self.source_network_chain_id: int | None = module_info.source_network_chain_id
        self.destination_network_chain_id: int | None = module_info.destination_network_chain_id
        self.module_priority: int | None = module_info.module_priority
        self.module_name: str | None = module_info.module_name
        self.module_display_name: str | None = module_info.module_display_name

        self.deadline = int(time.time()) + 20 * 60

    async def run(self):       
        result = await canculate_amount_out_swaps(
            client=self.client, token_out_name='SINK', token_get_name='KRAKEN',
            min_available_balance_token=5000.0, min_clearance=750.0, from_eth=False
        )
        
        if result is None: return

        amount_out, decimals = result
        
        await approve(
            client=self.client, token_out_name='SINK', amount_out=int(amount_out * 10 ** decimals)
        )

        self.logger.info(
            f'{self.client.name} Swap {amount_out} SINK to KRAKEN on the Ink network'
        )

        address_contract: ChecksumAddress = AsyncWeb3.to_checksum_address(
            '0xb5b494e63c3a52391e6c8e4a4d6aa1aef369fb6b'
        )

        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract,
            abi=SWAP_INKSWAP_ABI
        )

        amount_out = int(amount_out * 10 ** decimals)
        path = [
            AsyncWeb3.to_checksum_address("0xD43e76fF8f95035E220070BdDFD3C0C2bdD3051B"),
            AsyncWeb3.to_checksum_address("0x4200000000000000000000000000000000000006"),
            AsyncWeb3.to_checksum_address("0xCa5f2cCBD9C40b32657dF57c716De44237f80F05")
        ]
        slippage_tolerance = 0.05 
        amounts_in = await contract.functions.getAmountsOut(amount_out, path).call()
        amount_out_min = int(amounts_in[1] * (1 - slippage_tolerance)) 
        try:
            
            tx_params = await self.client.prepare_transaction()
            transaction = await contract.functions.swapExactTokensForTokensSupportingFeeOnTransferTokens(
                amount_out,
                amount_out_min,
                path,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap SINK to KRAKEN on the Ink network. Error: {error}'
            )


class SwapInkswapKRAKENtoSINKWorker(Logger):
    def __init__(self, client: Client, module_info: SwapInkswapKRAKENtoSINKModule):
        super().__init__()

        self.client: Client = client
        self.module_info: SwapInkswapKRAKENtoSINKModule = module_info
        self.destination_network: str | None = module_info.destination_network
        self.source_network: str | None = module_info.source_network
        self.source_network_chain_id: int | None = module_info.source_network_chain_id
        self.destination_network_chain_id: int | None = module_info.destination_network_chain_id
        self.module_priority: int | None = module_info.module_priority
        self.module_name: str | None = module_info.module_name
        self.module_display_name: str | None = module_info.module_display_name

        self.deadline = int(time.time()) + 20 * 60

    async def run(self):       
        result = await canculate_amount_out_swaps(
            client=self.client, token_out_name='KRAKEN', token_get_name='SINK',
            min_available_balance_token=50_000.0, min_clearance=10_000.0, from_eth=False
        )
        
        if result is None: return

        amount_out, decimals = result
        
        await approve(
            client=self.client, token_out_name='KRAKEN', amount_out=int(amount_out * 10 ** decimals)
        )

        self.logger.info(
            f'{self.client.name} Swap {amount_out} KRAKEN to SINK on the Ink network'
        )

        address_contract: ChecksumAddress = AsyncWeb3.to_checksum_address(
            '0xb5b494e63c3a52391e6c8e4a4d6aa1aef369fb6b'
        )

        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract,
            abi=SWAP_INKSWAP_ABI
        )

        amount_out = int(amount_out * 10 ** decimals)
        path = [
            AsyncWeb3.to_checksum_address("0xCa5f2cCBD9C40b32657dF57c716De44237f80F05"),
            AsyncWeb3.to_checksum_address("0x4200000000000000000000000000000000000006"),
            AsyncWeb3.to_checksum_address("0xD43e76fF8f95035E220070BdDFD3C0C2bdD3051B")
        ]
        slippage_tolerance = 0.05 
        amounts_in = await contract.functions.getAmountsOut(amount_out, path).call()
        amount_out_min = int(amounts_in[1] * (1 - slippage_tolerance)) 
        try:
            
            tx_params = await self.client.prepare_transaction()
            transaction = await contract.functions.swapExactTokensForTokensSupportingFeeOnTransferTokens(
                amount_out,
                amount_out_min,
                path,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap KRAKEN to SINK on the Ink network. Error: {error}'
            )


class SwapInkswapKRAKENtoISWAPWorker(Logger):
    def __init__(self, client: Client, module_info: SwapInkswapKRAKENtoISWAPModule):
        super().__init__()

        self.client: Client = client
        self.module_info: SwapInkswapKRAKENtoISWAPModule = module_info
        self.destination_network: str | None = module_info.destination_network
        self.source_network: str | None = module_info.source_network
        self.source_network_chain_id: int | None = module_info.source_network_chain_id
        self.destination_network_chain_id: int | None = module_info.destination_network_chain_id
        self.module_priority: int | None = module_info.module_priority
        self.module_name: str | None = module_info.module_name
        self.module_display_name: str | None = module_info.module_display_name

        self.deadline = int(time.time()) + 20 * 60

    async def run(self):       
        result = await canculate_amount_out_swaps(
            client=self.client, token_out_name='KRAKEN', token_get_name='ISWAP',
            min_available_balance_token=50_000.0, min_clearance=10_000.0, from_eth=False
        )
        
        if result is None: return

        amount_out, decimals = result
        
        await approve(
            client=self.client, token_out_name='KRAKEN', amount_out=int(amount_out * 10 ** decimals)
        )

        self.logger.info(
            f'{self.client.name} Swap {amount_out} KRAKEN to ISWAP on the Ink network'
        )

        address_contract: ChecksumAddress = AsyncWeb3.to_checksum_address(
            '0xb5b494e63c3a52391e6c8e4a4d6aa1aef369fb6b'
        )

        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract,
            abi=SWAP_INKSWAP_ABI
        )

        amount_out = int(amount_out * 10 ** decimals)
        path = [
            AsyncWeb3.to_checksum_address("0xCa5f2cCBD9C40b32657dF57c716De44237f80F05"),
            AsyncWeb3.to_checksum_address("0x4200000000000000000000000000000000000006"),
            AsyncWeb3.to_checksum_address("0x6814B9C5dae3DD05A8dBE9bF2b4E4FbB9Cef5302")
        ]
        slippage_tolerance = 0.05 
        amounts_in = await contract.functions.getAmountsOut(amount_out, path).call()
        amount_out_min = int(amounts_in[1] * (1 - slippage_tolerance)) 
        try:
            
            tx_params = await self.client.prepare_transaction()
            transaction = await contract.functions.swapExactTokensForTokensSupportingFeeOnTransferTokens(
                amount_out,
                amount_out_min,
                path,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap KRAKEN to ISWAP on the Ink network. Error: {error}'
            )


class SwapInkswapISWAPtoKRAKENWorker(Logger):
    def __init__(self, client: Client, module_info: SwapInkswapISWAPtoKRAKENModule):
        super().__init__()

        self.client: Client = client
        self.module_info: SwapInkswapISWAPtoKRAKENModule = module_info
        self.destination_network: str | None = module_info.destination_network
        self.source_network: str | None = module_info.source_network
        self.source_network_chain_id: int | None = module_info.source_network_chain_id
        self.destination_network_chain_id: int | None = module_info.destination_network_chain_id
        self.module_priority: int | None = module_info.module_priority
        self.module_name: str | None = module_info.module_name
        self.module_display_name: str | None = module_info.module_display_name

        self.deadline = int(time.time()) + 20 * 60

    async def run(self):       
        result = await canculate_amount_out_swaps(
            client=self.client, token_out_name='ISWAP', token_get_name='KRAKEN',
            min_available_balance_token=25.0, min_clearance=10.0, from_eth=False
        )
        
        if result is None: return

        amount_out, decimals = result
        
        await approve(
            client=self.client, token_out_name='ISWAP', amount_out=int(amount_out * 10 ** decimals)
        )

        self.logger.info(
            f'{self.client.name} Swap {amount_out} ISWAP to KRAKEN on the Ink network'
        )

        address_contract: ChecksumAddress = AsyncWeb3.to_checksum_address(
            '0xb5b494e63c3a52391e6c8e4a4d6aa1aef369fb6b'
        )

        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract,
            abi=SWAP_INKSWAP_ABI
        )

        amount_out = int(amount_out * 10 ** decimals)
        path = [
            AsyncWeb3.to_checksum_address("0x6814B9C5dae3DD05A8dBE9bF2b4E4FbB9Cef5302"),
            AsyncWeb3.to_checksum_address("0x4200000000000000000000000000000000000006"),
            AsyncWeb3.to_checksum_address("0xCa5f2cCBD9C40b32657dF57c716De44237f80F05")
        ]
        slippage_tolerance = 0.05 
        amounts_in = await contract.functions.getAmountsOut(amount_out, path).call()
        amount_out_min = int(amounts_in[1] * (1 - slippage_tolerance)) 
        try:
            
            tx_params = await self.client.prepare_transaction()
            transaction = await contract.functions.swapExactTokensForTokensSupportingFeeOnTransferTokens(
                amount_out,
                amount_out_min,
                path,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap ISWAP to KRAKEN on the Ink network. Error: {error}'
            )