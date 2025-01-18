import time
import random


from web3 import AsyncWeb3
from web3.contract import AsyncContract
from web3.contract.async_contract import AsyncContract
from web3.eth.async_eth import ChecksumAddress

from modules import *
from utils.client import Client
from data.abi import SWAP_INKSWAP_ABI
from modules.interfaces import SwapInkswapETHtoISWAPModule

# ETH ↔ WETH
# ETH ↔ ISWAP
# ETH ↔ SINK
# WETH ↔ ISWAP
# WETH ↔ SINK
# ISWAP ↔ SINK

logger: Logger = Logger().get_logger()

async def canculate_amount_out_swaps_eth_to_only(
        client: Client, token_out_name: str, token_get_name: str, min_available_balance_token: float,
        min_clearance: float
    ):
    balance_iswap = await client.get_token_balance(token_name=token_get_name)      
    decimals = await client.get_decimals(token_name=token_get_name)
    iswap_value = balance_iswap / 10 ** decimals 
    if iswap_value > min_available_balance_token or min_available_balance_token - iswap_value < min_clearance:
        logger.warning(
            f'{client.name} Skip the swap {token_out_name} to {token_get_name} on the Ink network, because we already have enough tokens {token_get_name}'
        )
        return None
    
    free_amount_iswap = min_available_balance_token - iswap_value
    if free_amount_iswap < 10:
        percent = 100
    else:
        percent = random.randint(50, 100)

    amount_out = round(free_amount_iswap * (1 - percent / 100), random.randint(2, 4))
    if amount_out < 10:
        amount_out = random.randint(10, 20)

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
        result = await canculate_amount_out_swaps_eth_to_only(
            client=self.client, token_out_name='ETH', token_get_name='ISWAP',
            min_available_balance_token=50.0, min_clearance=10.0
        )
        
        if result is None: return

        amount_out, decimals = result

        self.logger.info(
            f'{self.client.name} Swap ETH to {amount_out} ISWAP on the Ink network'
        )

        proxy_address_contract: ChecksumAddress = AsyncWeb3.to_checksum_address(
            '0xb5B494e63c3a52391E6C8E4a4D6aa1AEF369Fb6B'
        )

        contract: AsyncContract = self.client.w3.eth.contract(
            address=proxy_address_contract,
            abi=SWAP_INKSWAP_ABI
        )

        amount_out = amount_out * 10 ** decimals
        path = [
            AsyncWeb3.to_checksum_address("0x4200000000000000000000000000000000000006"),
            AsyncWeb3.to_checksum_address("0x6814B9C5dae3DD05A8dBE9bF2b4E4FbB9Cef5302")
        ]
        slippage_tolerance = 0.005 

        amounts_in = await contract.functions.getAmountsIn(amount_out, path).call()

        value = int(amounts_in[0] * (1 + slippage_tolerance)) 

        balance_nativ = await self.client.get_token_balance(check_native=True)  
        if balance_nativ - self.module_info.min_available_balance * 10 ** 18 < value:
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
                f'{self.client.name} Failed the swap ETH to ISWAP on the Ink network. Error: {error} '
            )
